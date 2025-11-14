"""
API Client for Backend Communication
"""
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from .config import BACKEND_API_URL

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """Client for communicating with the backend API"""

    def __init__(self, base_url: str = BACKEND_API_URL):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
        except Exception as e:
            logger.error(f"API request exception: {e}")
            return {"error": str(e)}

    # Trading API

    async def start_trading(
        self,
        strategy_id: int,
        symbol: str = "BTC/USDT",
        timeframe: str = "1h",
        capital: float = 1000,
        max_position_size_usd: float = 100,
        max_daily_loss_percent: float = 5,
        max_daily_trades: int = 10
    ) -> Dict[str, Any]:
        """Start live trading bot"""
        data = {
            "strategy_id": strategy_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "capital": capital,
            "max_position_size_usd": max_position_size_usd,
            "max_daily_loss_percent": max_daily_loss_percent,
            "max_daily_trades": max_daily_trades
        }
        return await self._request("POST", "/api/trading/start", json=data)

    async def stop_trading(self) -> Dict[str, Any]:
        """Stop trading bot"""
        return await self._request("POST", "/api/trading/stop")

    async def pause_trading(self) -> Dict[str, Any]:
        """Pause trading bot"""
        return await self._request("POST", "/api/trading/pause")

    async def resume_trading(self) -> Dict[str, Any]:
        """Resume trading bot"""
        return await self._request("POST", "/api/trading/resume")

    async def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading bot status"""
        return await self._request("GET", "/api/trading/status")

    async def get_trade_history(self) -> Dict[str, Any]:
        """Get trade history"""
        return await self._request("GET", "/api/trading/history")

    async def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop trading"""
        return await self._request("POST", "/api/trading/emergency-stop")

    # Strategy API

    async def get_strategies(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get list of strategies"""
        return await self._request("GET", f"/api/strategies/?skip={skip}&limit={limit}")

    async def get_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """Get strategy by ID"""
        return await self._request("GET", f"/api/strategies/{strategy_id}")

    # Backtest API

    async def run_backtest(
        self,
        strategy_id: int,
        symbol: str = "BTC/USDT",
        timeframe: str = "1h",
        initial_capital: float = 10000,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run backtest"""
        data = {
            "strategy_id": strategy_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "initial_capital": initial_capital
        }
        if start_date:
            data["start_date"] = start_date
        if end_date:
            data["end_date"] = end_date

        return await self._request("POST", "/api/backtests/run", json=data)

    async def get_backtest_results(self, backtest_id: int) -> Dict[str, Any]:
        """Get backtest results"""
        return await self._request("GET", f"/api/backtests/{backtest_id}/results")

    async def get_backtest_progress(self, backtest_id: int) -> Dict[str, Any]:
        """Get backtest progress"""
        return await self._request("GET", f"/api/backtests/{backtest_id}/progress")

    async def get_backtests(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Get list of backtests"""
        return await self._request("GET", f"/api/backtests/?skip={skip}&limit={limit}")

    # Market API

    async def get_price(self, symbol: str = "BTC/USDT") -> Dict[str, Any]:
        """Get current price"""
        return await self._request("GET", f"/api/market/price?symbol={symbol}")

    async def get_ticker(self, symbol: str = "BTC/USDT") -> Dict[str, Any]:
        """Get ticker info"""
        return await self._request("GET", f"/api/market/ticker?symbol={symbol}")


# Global API client instance
api_client = BackendAPIClient()
