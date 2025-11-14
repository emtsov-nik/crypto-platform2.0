from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    initial_capital = Column(Numeric(20, 8), nullable=False)
    final_capital = Column(Numeric(20, 8), nullable=True)
    total_pnl = Column(Numeric(20, 8), nullable=True)
    total_return = Column(Numeric(10, 4), nullable=True)
    total_trades = Column(Integer, nullable=True, default=0)
    winning_trades = Column(Integer, nullable=True, default=0)
    losing_trades = Column(Integer, nullable=True, default=0)
    num_trades = Column(Integer, nullable=True)
    win_rate = Column(Numeric(5, 2), nullable=True)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    params = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")

    def __repr__(self):
        return f"<Backtest(id={self.id}, symbol='{self.symbol}', timeframe='{self.timeframe}', status='{self.status}')>"
