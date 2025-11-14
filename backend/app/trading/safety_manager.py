"""
⚠️ WARNING: This module handles REAL MONEY trading ⚠️

Safety Manager ensures that all trading operations are within safe limits
and prevents catastrophic losses.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SafetyLimits:
    """Safety limits for trading"""
    max_position_size_usd: float = 1000.0  # Max position size in USD
    max_daily_loss_percent: float = 5.0  # Max daily loss as % of starting capital
    max_daily_trades: int = 50  # Max trades per day
    max_open_positions: int = 1  # Max simultaneous open positions
    min_capital_usd: float = 100.0  # Minimum capital to continue trading
    emergency_stop_loss_percent: float = 10.0  # Emergency stop if total loss exceeds this


class SafetyManager:
    """
    Manages safety checks and limits for live trading

    This class prevents catastrophic losses by enforcing:
    - Position size limits
    - Daily loss limits
    - Trade frequency limits
    - Emergency stops
    """

    def __init__(self, limits: Optional[SafetyLimits] = None):
        self.limits = limits or SafetyLimits()
        self.daily_trades_count = 0
        self.daily_pnl = 0.0
        self.starting_capital = 0.0
        self.current_day = datetime.utcnow().date()
        self.emergency_stop = False
        self.stop_reason = None

        logger.info(f"SafetyManager initialized with limits: {self.limits}")

    def set_starting_capital(self, capital: float):
        """Set starting capital for the day"""
        self.starting_capital = capital
        logger.info(f"Starting capital set to: ${capital:.2f}")

    def reset_daily_stats(self):
        """Reset daily statistics (call at start of new day)"""
        current_date = datetime.utcnow().date()
        if current_date != self.current_day:
            logger.info(f"Resetting daily stats. Previous: trades={self.daily_trades_count}, pnl=${self.daily_pnl:.2f}")
            self.current_day = current_date
            self.daily_trades_count = 0
            self.daily_pnl = 0.0

    def can_open_position(
        self,
        position_size_usd: float,
        current_open_positions: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check if we can open a new position

        Returns:
            (can_open, reason_if_not)
        """
        # Check emergency stop
        if self.emergency_stop:
            return False, f"EMERGENCY STOP ACTIVE: {self.stop_reason}"

        # Reset daily stats if new day
        self.reset_daily_stats()

        # Check position size limit
        if position_size_usd > self.limits.max_position_size_usd:
            reason = f"Position size ${position_size_usd:.2f} exceeds limit ${self.limits.max_position_size_usd:.2f}"
            logger.warning(reason)
            return False, reason

        # Check max open positions
        if current_open_positions >= self.limits.max_open_positions:
            reason = f"Already have {current_open_positions} open positions (limit: {self.limits.max_open_positions})"
            logger.warning(reason)
            return False, reason

        # Check daily trades limit
        if self.daily_trades_count >= self.limits.max_daily_trades:
            reason = f"Daily trades limit reached: {self.daily_trades_count}/{self.limits.max_daily_trades}"
            logger.warning(reason)
            return False, reason

        # Check daily loss limit
        if self.starting_capital > 0:
            daily_loss_percent = (abs(self.daily_pnl) / self.starting_capital) * 100
            if self.daily_pnl < 0 and daily_loss_percent >= self.limits.max_daily_loss_percent:
                reason = f"Daily loss limit reached: {daily_loss_percent:.2f}% (limit: {self.limits.max_daily_loss_percent}%)"
                logger.error(reason)
                self.trigger_emergency_stop(reason)
                return False, reason

        logger.info(f"Position opening approved: ${position_size_usd:.2f}")
        return True, None

    def can_continue_trading(self, current_capital: float) -> tuple[bool, Optional[str]]:
        """
        Check if we should continue trading

        Returns:
            (can_continue, reason_if_not)
        """
        # Check emergency stop
        if self.emergency_stop:
            return False, f"EMERGENCY STOP: {self.stop_reason}"

        # Check minimum capital
        if current_capital < self.limits.min_capital_usd:
            reason = f"Capital ${current_capital:.2f} below minimum ${self.limits.min_capital_usd:.2f}"
            logger.error(reason)
            self.trigger_emergency_stop(reason)
            return False, reason

        # Check total loss limit (emergency stop)
        if self.starting_capital > 0:
            total_loss_percent = ((self.starting_capital - current_capital) / self.starting_capital) * 100
            if total_loss_percent >= self.limits.emergency_stop_loss_percent:
                reason = f"EMERGENCY: Total loss {total_loss_percent:.2f}% exceeds limit {self.limits.emergency_stop_loss_percent}%"
                logger.critical(reason)
                self.trigger_emergency_stop(reason)
                return False, reason

        return True, None

    def record_trade(self, pnl: float):
        """Record a completed trade"""
        self.daily_trades_count += 1
        self.daily_pnl += pnl
        logger.info(f"Trade recorded: PnL=${pnl:.2f}, Daily total: {self.daily_trades_count} trades, ${self.daily_pnl:.2f} PnL")

    def trigger_emergency_stop(self, reason: str):
        """Trigger emergency stop"""
        self.emergency_stop = True
        self.stop_reason = reason
        logger.critical(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")

    def reset_emergency_stop(self):
        """Reset emergency stop (requires manual intervention)"""
        logger.warning("Emergency stop reset by user")
        self.emergency_stop = False
        self.stop_reason = None

    def get_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        return {
            'emergency_stop': self.emergency_stop,
            'stop_reason': self.stop_reason,
            'daily_trades': self.daily_trades_count,
            'daily_pnl': self.daily_pnl,
            'starting_capital': self.starting_capital,
            'limits': {
                'max_position_size_usd': self.limits.max_position_size_usd,
                'max_daily_loss_percent': self.limits.max_daily_loss_percent,
                'max_daily_trades': self.limits.max_daily_trades,
                'max_open_positions': self.limits.max_open_positions,
                'min_capital_usd': self.limits.min_capital_usd,
                'emergency_stop_loss_percent': self.limits.emergency_stop_loss_percent,
            }
        }
