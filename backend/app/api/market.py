from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.services.binance_service import BinanceService
from app.services.indicators import IndicatorService
from app.schemas.market import (
    SymbolListResponse,
    SymbolInfo,
    KlineResponse,
    KlineData,
    IndicatorResponse,
    TickerInfo
)

router = APIRouter()
binance_service = BinanceService()


@router.get("/symbols", response_model=SymbolListResponse)
async def get_symbols(quote: str = Query(default="USDT", description="Quote currency")):
    """Get list of available trading pairs"""
    try:
        symbols = binance_service.get_symbols(quote_currency=quote)
        return SymbolListResponse(
            symbols=symbols,
            count=len(symbols)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/klines", response_model=KlineResponse)
async def get_klines(
    symbol: str = Query(..., description="Trading pair (e.g., BTC/USDT)"),
    timeframe: str = Query(default="1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(default=500, ge=1, le=1000, description="Number of candles"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)")
):
    """Get historical OHLCV data"""
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        # Fetch data
        df = binance_service.get_klines(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            start_time=start_dt,
            end_time=end_dt
        )

        # Convert to response format
        klines = [
            KlineData(
                timestamp=row['timestamp'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume']
            )
            for _, row in df.iterrows()
        ]

        return KlineResponse(
            symbol=symbol,
            timeframe=timeframe,
            data=klines,
            count=len(klines)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators", response_model=IndicatorResponse)
async def get_indicators(
    symbol: str = Query(..., description="Trading pair (e.g., BTC/USDT)"),
    timeframe: str = Query(default="1h", description="Timeframe"),
    limit: int = Query(default=500, ge=1, le=1000),
    indicators: Optional[str] = Query(
        None,
        description="Comma-separated list of indicators (rsi,bb,sma,ema,macd,atr,vwap) or 'all'"
    ),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)")
):
    """Get OHLCV data with technical indicators"""
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        # Fetch base data
        df = binance_service.get_klines(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            start_time=start_dt,
            end_time=end_dt
        )

        # Parse requested indicators
        indicator_list = []
        if indicators:
            if indicators.lower() == 'all':
                # Add all indicators
                df = IndicatorService.add_all_indicators(df)
                indicator_list = ['rsi', 'bb', 'sma', 'ema', 'macd', 'atr', 'vwap']
            else:
                # Add specific indicators
                indicator_list = [ind.strip().lower() for ind in indicators.split(',')]
                
                for indicator in indicator_list:
                    if indicator == 'rsi':
                        df = IndicatorService.add_rsi(df)
                    elif indicator == 'bb':
                        df = IndicatorService.add_bollinger_bands(df)
                    elif indicator == 'sma':
                        df = IndicatorService.add_moving_averages(df)
                    elif indicator == 'ema':
                        df = IndicatorService.add_exponential_moving_averages(df)
                    elif indicator == 'macd':
                        df = IndicatorService.add_macd(df)
                    elif indicator == 'atr':
                        df = IndicatorService.add_atr(df)
                    elif indicator == 'vwap':
                        df = IndicatorService.add_vwap(df)

        # Convert timestamps to ISO format strings
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Convert to dict records
        data = df.to_dict('records')

        return IndicatorResponse(
            symbol=symbol,
            timeframe=timeframe,
            data=data,
            indicators=indicator_list,
            count=len(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{symbol}", response_model=TickerInfo)
async def get_ticker(symbol: str):
    """Get ticker information for a symbol"""
    try:
        ticker = binance_service.get_ticker(symbol)
        return TickerInfo(**ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for a symbol"""
    try:
        price = binance_service.get_current_price(symbol)
        return {"symbol": symbol, "price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_connection():
    """Test connection to Binance API"""
    try:
        result = binance_service.test_connection()
        return {"status": "connected" if result else "disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
