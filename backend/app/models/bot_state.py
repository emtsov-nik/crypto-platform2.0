from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class BotState(Base):
    __tablename__ = "bot_states"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=True)  # 'long', 'short', or None
    steps_opened = Column(Integer, default=0)
    avg_price = Column(Numeric(20, 8), nullable=True)
    total_qty = Column(Numeric(20, 8), nullable=True)
    last_signal_ts = Column(BigInteger, nullable=True)
    paused = Column(Boolean, default=False)
    is_live = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    strategy = relationship("Strategy", backref="bot_states")

    def __repr__(self):
        return f"<BotState(id={self.id}, symbol='{self.symbol}', direction='{self.direction}')>"
