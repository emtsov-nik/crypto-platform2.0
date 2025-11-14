from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=True)
    bot_state_id = Column(Integer, ForeignKey("bot_states.id"), nullable=True)
    side = Column(String(10), nullable=False)  # 'long' or 'short'
    entry_time = Column(DateTime(timezone=True), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    exit_price = Column(Numeric(20, 8), nullable=True)
    quantity = Column(Numeric(20, 8), nullable=False)
    pnl = Column(Numeric(20, 8), nullable=True)
    pnl_pct = Column(Numeric(10, 4), nullable=True)
    exit_reason = Column(String(50), nullable=True)  # 'tp', 'sl', 'signal'
    fees = Column(Numeric(20, 8), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    backtest = relationship("Backtest", backref="trades")
    bot_state = relationship("BotState", backref="trades")

    def __repr__(self):
        return f"<Trade(id={self.id}, side='{self.side}', entry_price={self.entry_price})>"
