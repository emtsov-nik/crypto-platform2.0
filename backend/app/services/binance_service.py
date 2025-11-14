import ccxt
from binance.client import Client
from typing import List, Dict, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import redis
import json
from app.config import settings


class BinanceService:
    """Service for interacting with Binance API"""

    def __init__(self):
        # Initialize ccxt for unified API
        # For public endpoints, API keys are optional
        exchange_config = {
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # Use spot market by default
            }
        }

        # Add API keys only if they are configured and not empty
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET and \
           settings.BINANCE_API_KEY != '' and settings.BINANCE_API_SECRET != '':
            exchange_config['apiKey'] = settings.BINANCE_API_KEY
            exchange_config['secret'] = settings.BINANCE_API_SECRET

        try:
            self.exchange = ccxt.binance(exchange_config)

            # Set testnet if configured (only works with API keys)
            if settings.BINANCE_TESTNET and 'apiKey' in exchange_config:
                self.exchange.set_sandbox_mode(True)
        except Exception as e:
            print(f"Warning: Failed to initialize ccxt exchange: {e}")
            # Create a basic exchange without credentials for public endpoints
            self.exchange = ccxt.binance({'enableRateLimit': True})

        # Initialize python-binance for additional features
        # Only if API keys are provided
        self.client = None
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET and \
           settings.BINANCE_API_KEY != '' and settings.BINANCE_API_SECRET != '':
            try:
                self.client = Client(
                    settings.BINANCE_API_KEY,
                    settings.BINANCE_API_SECRET,
                    testnet=settings.BINANCE_TESTNET
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Binance client: {e}")

        # Redis for caching
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            self.cache_enabled = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.cache_enabled = False

    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        params = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{prefix}:{params}"

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        if not self.cache_enabled:
            return None
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache read error: {e}")
        return None

    def _set_cache(self, key: str, data: Any, ttl: int = 300):
        """Set data in cache with TTL (default 5 minutes)"""
        if not self.cache_enabled:
            return
        try:
            self.redis_client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            print(f"Cache write error: {e}")

    def get_exchange_info(self) -> Dict:
        """Get exchange information"""
        cache_key = self._get_cache_key("exchange_info")
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        try:
            info = self.exchange.fetch_markets()
            # Cache for 1 hour
            self._set_cache(cache_key, info, ttl=3600)
            return info
        except Exception as e:
            print(f"Error fetching exchange info: {e}")
            raise

    def get_symbols(self, quote_currency: str = "USDT") -> List[Dict[str, str]]:
        """Get list of available trading pairs"""
        cache_key = self._get_cache_key("symbols", quote=quote_currency)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        try:
            markets = self.get_exchange_info()
            symbols = []

            for market in markets:
                if market['quote'] == quote_currency and market['active']:
                    symbols.append({
                        'symbol': market['symbol'],
                        'baseAsset': market['base'],
                        'quoteAsset': market['quote'],
                        'status': 'TRADING' if market['active'] else 'INACTIVE'
                    })

            # Sort by symbol
            symbols.sort(key=lambda x: x['symbol'])

            # Cache for 1 hour
            self._set_cache(cache_key, symbols, ttl=3600)
            return symbols
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            raise

    def get_klines(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 500,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles to fetch
            start_time: Start time (optional)
            end_time: End time (optional)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        # Create cache key
        cache_params = {
            'symbol': symbol,
            'timeframe': timeframe,
            'limit': limit,
        }
        if start_time:
            cache_params['start'] = start_time.isoformat()
        if end_time:
            cache_params['end'] = end_time.isoformat()

        cache_key = self._get_cache_key("klines", **cache_params)
        cached = self._get_from_cache(cache_key)
        if cached:
            return pd.DataFrame(cached)

        try:
            # Fetch data using ccxt
            since = int(start_time.timestamp() * 1000) if start_time else None

            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=since,
                limit=limit
            )

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Filter by end_time if provided
            if end_time:
                df = df[df['timestamp'] <= end_time]

            # Cache for 1 minute (data changes frequently)
            self._set_cache(cache_key, df.to_dict('records'), ttl=60)

            return df
        except Exception as e:
            print(f"Error fetching klines: {e}")
            raise

    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        cache_key = self._get_cache_key("price", symbol=symbol)
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']

            # Cache for 10 seconds
            self._set_cache(cache_key, price, ttl=10)
            return price
        except Exception as e:
            print(f"Error fetching price: {e}")
            raise

    def get_ticker(self, symbol: str) -> Dict:
        """Get ticker information for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'quoteVolume': ticker['quoteVolume'],
                'change': ticker['change'],
                'percentage': ticker['percentage'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            print(f"Error fetching ticker: {e}")
            raise

    def test_connection(self) -> bool:
        """Test connection to Binance API"""
        try:
            self.exchange.fetch_time()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
