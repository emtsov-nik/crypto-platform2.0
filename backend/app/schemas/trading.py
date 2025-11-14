from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


# Bot control schemas

class StartBotRequest(BaseModel):
    """Request to start trading bot"""
    strategy_id: int
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    capital: float = Field(1000.0, gt=0)
    # Safety limits
    max_position_size_usd: float = Field(1000.0, gt=0)
    max_daily_loss_percent: float = Field(5.0, gt=0, le=50)
    max_daily_trades: int = Field(50, gt=0)


class BotStatusResponse(BaseModel):
    """Bot status response"""
    status: str
    symbol: str
    timeframe: str
    capital: float
    position: Optional[Dict[str, Any]] = None
    open_orders: int
    total_trades: int
    start_time: Optional[str] = None
    error_message: Optional[str] = None
    safety_status: Dict[str, Any]


class PositionInfo(BaseModel):
    """Current position information"""
    side: str
    entry_price: float
    quantity: float
    take_profit: float
    stop_loss: float
    entry_time: str
    unrealized_pnl: Optional[float] = None


class TradeHistoryItem(BaseModel):
    """Trade history item"""
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    entry_time: str
    exit_time: str
    exit_reason: str


class TradeHistoryResponse(BaseModel):
    """Trade history response"""
    trades: List[TradeHistoryItem]
    total: int
    total_pnl: float


# Action responses

class BotActionResponse(BaseModel):
    """Response for bot actions (start/stop/pause)"""
    success: bool
    message: str
    status: Optional[str] = None
