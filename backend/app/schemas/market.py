from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SymbolInfo(BaseModel):
    """Symbol information"""
    symbol: str
    baseAsset: str
    quoteAsset: str
    status: str


class SymbolListResponse(BaseModel):
    """Response for symbols list"""
    symbols: List[SymbolInfo]
    count: int


class KlineData(BaseModel):
    """Single candlestick data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class KlineRequest(BaseModel):
    """Request parameters for klines"""
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    timeframe: str = Field(default="1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)")
    limit: int = Field(default=500, ge=1, le=1000, description="Number of candles")
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")


class KlineResponse(BaseModel):
    """Response with kline data"""
    symbol: str
    timeframe: str
    data: List[KlineData]
    count: int


class IndicatorRequest(BaseModel):
    """Request parameters for data with indicators"""
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    timeframe: str = Field(default="1h", description="Timeframe")
    limit: int = Field(default=500, ge=1, le=1000)
    indicators: Optional[List[str]] = Field(
        default=None,
        description="List of indicators to calculate (rsi, bb, sma, ema, macd, atr, vwap)"
    )
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class IndicatorData(BaseModel):
    """Kline data with indicators"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    # Optional indicator fields
    rsi: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    sma_7: Optional[float] = None
    sma_25: Optional[float] = None
    sma_99: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_diff: Optional[float] = None
    atr: Optional[float] = None
    vwap: Optional[float] = None

    class Config:
        extra = "allow"  # Allow additional indicator fields


class IndicatorResponse(BaseModel):
    """Response with indicator data"""
    symbol: str
    timeframe: str
    data: List[Dict[str, Any]]
    indicators: List[str]
    count: int


class TickerInfo(BaseModel):
    """Ticker information"""
    symbol: str
    last: float
    bid: float
    ask: float
    high: float
    low: float
    volume: float
    quoteVolume: float
    change: Optional[float] = None
    percentage: Optional[float] = None
    timestamp: int
