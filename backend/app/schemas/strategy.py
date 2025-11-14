from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class StrategyBase(BaseModel):
    """Base strategy schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Strategy name")
    description: Optional[str] = Field(None, max_length=500, description="Strategy description")
    class_name: str = Field(..., description="Strategy class name (e.g., RSIBBStrategy)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters as JSON")
    is_active: bool = Field(default=True, description="Whether strategy is active")


class StrategyCreate(StrategyBase):
    """Schema for creating a new strategy"""
    pass

    @field_validator('class_name')
    @classmethod
    def validate_class_name(cls, v: str) -> str:
        """Validate that class name is not empty"""
        if not v or not v.strip():
            raise ValueError("class_name cannot be empty")
        return v.strip()


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    params: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class StrategyInDB(StrategyBase):
    """Strategy schema as stored in database"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyResponse(StrategyInDB):
    """Strategy schema for API responses"""
    pass


class StrategyListResponse(BaseModel):
    """Response schema for listing strategies"""
    strategies: List[StrategyResponse]
    total: int


# Strategy metadata schemas

class StrategyMetadata(BaseModel):
    """Strategy metadata from the strategy class"""
    name: str
    class_name: str
    description: Optional[str] = None
    indicators: List[str] = Field(default_factory=list)
    timeframes: List[str] = Field(default_factory=list)
    risk_level: Optional[str] = None
    strategy_type: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    default_params: Dict[str, Any] = Field(default_factory=dict)


class AvailableStrategyInfo(BaseModel):
    """Information about available strategy classes"""
    name: str = Field(..., description="Strategy class name")
    class_name: str = Field(..., description="Full class name")
    metadata: StrategyMetadata = Field(..., description="Strategy metadata")
    default_params: Dict[str, Any] = Field(default_factory=dict, description="Default parameters")
    doc: str = Field(default="", description="Strategy docstring")


class AvailableStrategiesResponse(BaseModel):
    """Response with list of available strategy classes"""
    strategies: List[AvailableStrategyInfo]
    total: int


# Strategy testing schemas

class StrategyTestRequest(BaseModel):
    """Request to test a strategy configuration"""
    class_name: str = Field(..., description="Strategy class name")
    params: Dict[str, Any] = Field(..., description="Strategy parameters")
    symbol: str = Field(default="BTC/USDT", description="Trading pair to test with")
    timeframe: str = Field(default="1h", description="Timeframe to test with")
    limit: int = Field(default=100, ge=10, le=1000, description="Number of candles to fetch")


class SignalInfo(BaseModel):
    """Information about a generated signal"""
    timestamp: datetime
    signal: str  # 'long', 'short', or 'close'
    price: float
    indicators: Dict[str, Any] = Field(default_factory=dict)


class StrategyTestResponse(BaseModel):
    """Response from strategy testing"""
    success: bool
    message: str
    signals: List[SignalInfo] = Field(default_factory=list)
    total_signals: int = 0
    long_signals: int = 0
    short_signals: int = 0
    close_signals: int = 0


# Strategy validation schemas

class StrategyValidationRequest(BaseModel):
    """Request to validate strategy parameters"""
    class_name: str
    params: Dict[str, Any]


class StrategyValidationResponse(BaseModel):
    """Response from strategy validation"""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# Strategy signal generation schemas

class GenerateSignalRequest(BaseModel):
    """Request to generate signal for current market conditions"""
    strategy_id: int = Field(..., description="Strategy ID from database")
    symbol: str = Field(default="BTC/USDT", description="Trading pair")
    timeframe: str = Field(default="1h", description="Timeframe")


class GenerateSignalResponse(BaseModel):
    """Response with generated signal"""
    strategy_id: int
    strategy_name: str
    symbol: str
    timeframe: str
    signal: Optional[str] = None  # 'long', 'short', or None
    timestamp: datetime
    current_price: float
    indicators: Dict[str, Any] = Field(default_factory=dict)
    message: str
