from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class BacktestBase(BaseModel):
    """Base backtest schema"""
    strategy_id: int = Field(..., description="Strategy ID to use for backtest")
    symbol: str = Field(..., min_length=1, description="Trading pair symbol (e.g., BTC/USDT)")
    timeframe: str = Field(..., description="Timeframe (e.g., 1h, 4h, 1d)")
    start_date: Optional[datetime] = Field(None, description="Start date for backtest")
    end_date: Optional[datetime] = Field(None, description="End date for backtest")
    initial_capital: float = Field(10000.0, gt=0, description="Initial capital in quote currency")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters (fee_rate, slippage, etc.)")


class BacktestCreate(BacktestBase):
    """Schema for creating a new backtest"""
    pass

    @field_validator('timeframe')
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        """Validate timeframe"""
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']
        if v not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}")
        return v


class BacktestUpdate(BaseModel):
    """Schema for updating a backtest"""
    status: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


class BacktestInDB(BacktestBase):
    """Backtest schema as stored in database"""
    id: int
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    # Results (filled after completion)
    final_capital: Optional[float] = None
    total_pnl: Optional[float] = None
    total_pnl_percent: Optional[float] = None
    total_trades: Optional[int] = None
    winning_trades: Optional[int] = None
    losing_trades: Optional[int] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    max_drawdown: Optional[float] = None
    max_drawdown_percent: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    results: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class BacktestResponse(BacktestInDB):
    """Backtest schema for API responses"""
    pass


class BacktestListResponse(BaseModel):
    """Response schema for listing backtests"""
    backtests: List[BacktestResponse]
    total: int


# Trade schemas

class TradeInfo(BaseModel):
    """Information about a single trade from backtest"""
    id: int
    entry_time: str
    exit_time: str
    side: str  # 'long' or 'short'
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    fees: float
    exit_reason: str
    steps: int = 1


class TradeListResponse(BaseModel):
    """Response with list of trades"""
    trades: List[TradeInfo]
    total: int


# Results schemas

class BacktestMetrics(BaseModel):
    """Backtest performance metrics"""
    symbol: str
    initial_capital: float
    final_capital: float
    total_pnl: float
    total_pnl_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    avg_trade_pnl: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float


class BacktestResults(BacktestMetrics):
    """Complete backtest results with trades and equity curve"""
    trades: List[TradeInfo]
    equity_curve: List[float]
    timestamps: List[str]


# Progress tracking

class BacktestProgress(BaseModel):
    """Backtest progress information"""
    backtest_id: int
    status: str  # 'pending', 'running', 'completed', 'failed'
    current: int  # Current progress (0-100)
    total: int  # Total progress (100)
    message: str  # Status message


# Comparison schemas

class BacktestComparisonItem(BaseModel):
    """Single backtest in comparison"""
    id: int
    strategy_id: int
    symbol: str
    timeframe: str
    total_pnl_percent: Optional[float]
    win_rate: Optional[float]
    profit_factor: Optional[float]
    max_drawdown_percent: Optional[float]
    sharpe_ratio: Optional[float]
    total_trades: Optional[int]


class BacktestComparisonResponse(BaseModel):
    """Response for comparing multiple backtests"""
    backtests: List[BacktestComparisonItem]
    metrics: List[str]


# Equity curve schema

class EquityCurveResponse(BaseModel):
    """Response with equity curve data"""
    timestamps: List[str]
    equity: List[float]


# Run backtest request

class RunBacktestRequest(BaseModel):
    """Request to run a backtest"""
    strategy_id: int
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    initial_capital: float = 10000.0
    fee_rate: float = Field(0.001, ge=0, le=0.01, description="Trading fee rate (0.001 = 0.1%)")
    slippage: float = Field(0.0005, ge=0, le=0.01, description="Slippage rate (0.0005 = 0.05%)")


class RunBacktestResponse(BaseModel):
    """Response after starting a backtest"""
    backtest_id: int
    status: str
    message: str
    task_id: Optional[str] = None  # Celery task ID for async execution
