"""
Unit Tests for Safety Manager
"""
import pytest
from datetime import datetime
from app.trading.safety_manager import SafetyManager, SafetyLimits


@pytest.mark.unit
@pytest.mark.safety
class TestSafetyLimits:
    """Test SafetyLimits dataclass"""

    def test_safety_limits_creation(self):
        """Test safety limits creation with default values"""
        limits = SafetyLimits()

        assert limits.max_position_size_usd == 1000
        assert limits.max_open_positions == 3
        assert limits.max_daily_trades == 10
        assert limits.max_daily_loss_percent == 5.0

    def test_safety_limits_custom_values(self):
        """Test safety limits with custom values"""
        limits = SafetyLimits(
            max_position_size_usd=500,
            max_open_positions=2,
            max_daily_trades=5,
            max_daily_loss_percent=3.0
        )

        assert limits.max_position_size_usd == 500
        assert limits.max_open_positions == 2
        assert limits.max_daily_trades == 5
        assert limits.max_daily_loss_percent == 3.0


@pytest.mark.unit
@pytest.mark.safety
class TestSafetyManager:
    """Test SafetyManager class"""

    def test_manager_initialization(self):
        """Test safety manager initialization"""
        limits = SafetyLimits()
        manager = SafetyManager(limits)

        assert manager.limits == limits
        assert manager.daily_trades_count == 0
        assert manager.daily_pnl == 0.0
        assert manager.emergency_stopped == False

    def test_can_open_position_basic(self):
        """Test basic position opening permission"""
        manager = SafetyManager()

        can_open, reason = manager.can_open_position(
            position_size_usd=500,
            current_open_positions=1
        )

        assert can_open == True
        assert reason == ""

    def test_can_open_position_size_limit(self):
        """Test position size limit"""
        limits = SafetyLimits(max_position_size_usd=1000)
        manager = SafetyManager(limits)

        # Position size over limit
        can_open, reason = manager.can_open_position(
            position_size_usd=1500,
            current_open_positions=1
        )

        assert can_open == False
        assert "Position size" in reason

    def test_can_open_max_positions_limit(self):
        """Test max open positions limit"""
        limits = SafetyLimits(max_open_positions=3)
        manager = SafetyManager(limits)

        # Already at max positions
        can_open, reason = manager.can_open_position(
            position_size_usd=500,
            current_open_positions=3
        )

        assert can_open == False
        assert "Maximum open positions" in reason

    def test_can_open_daily_trades_limit(self):
        """Test daily trades limit"""
        limits = SafetyLimits(max_daily_trades=5)
        manager = SafetyManager(limits)

        # Set daily trades to limit
        manager.daily_trades_count = 5

        can_open, reason = manager.can_open_position(
            position_size_usd=500,
            current_open_positions=1
        )

        assert can_open == False
        assert "Daily trade limit" in reason

    def test_can_open_daily_loss_limit(self):
        """Test daily loss limit"""
        limits = SafetyLimits(max_daily_loss_percent=5.0)
        manager = SafetyManager(limits)

        # Set daily loss to exceed limit (assuming 10000 capital, 5% = 500)
        manager.daily_pnl = -600

        can_open, reason = manager.can_open_position(
            position_size_usd=500,
            current_open_positions=1,
            current_capital=10000
        )

        assert can_open == False
        assert "Daily loss limit" in reason

    def test_can_continue_trading_basic(self):
        """Test can continue trading with normal conditions"""
        manager = SafetyManager()

        can_continue, reason = manager.can_continue_trading(current_capital=10000)

        assert can_continue == True
        assert reason == ""

    def test_can_continue_emergency_stopped(self):
        """Test can't continue when emergency stopped"""
        manager = SafetyManager()
        manager.trigger_emergency_stop("Test emergency stop")

        can_continue, reason = manager.can_continue_trading(current_capital=10000)

        assert can_continue == False
        assert "Emergency stop" in reason

    def test_can_continue_min_capital(self):
        """Test can't continue below minimum capital"""
        limits = SafetyLimits(min_capital_usd=1000)
        manager = SafetyManager(limits)

        can_continue, reason = manager.can_continue_trading(current_capital=500)

        assert can_continue == False
        assert "Minimum capital" in reason

    def test_can_continue_max_total_loss(self):
        """Test can't continue after max total loss"""
        limits = SafetyLimits(max_total_loss_percent=20.0)
        manager = SafetyManager(limits)
        manager.initial_capital = 10000

        # Lost 25% of capital
        can_continue, reason = manager.can_continue_trading(current_capital=7500)

        assert can_continue == False
        assert "Total loss limit" in reason

    def test_trigger_emergency_stop(self):
        """Test emergency stop trigger"""
        manager = SafetyManager()

        manager.trigger_emergency_stop("Critical error detected")

        assert manager.emergency_stopped == True
        assert manager.emergency_stop_reason == "Critical error detected"

    def test_record_trade(self):
        """Test recording a trade"""
        manager = SafetyManager()

        manager.record_trade(pnl=100.0)

        assert manager.daily_trades_count == 1
        assert manager.daily_pnl == 100.0

        # Record another trade
        manager.record_trade(pnl=-50.0)

        assert manager.daily_trades_count == 2
        assert manager.daily_pnl == 50.0

    def test_reset_daily_stats(self):
        """Test resetting daily statistics"""
        manager = SafetyManager()

        # Record some trades
        manager.record_trade(pnl=100.0)
        manager.record_trade(pnl=50.0)

        assert manager.daily_trades_count == 2
        assert manager.daily_pnl == 150.0

        # Reset
        manager.reset_daily_stats()

        assert manager.daily_trades_count == 0
        assert manager.daily_pnl == 0.0

    def test_get_safety_status(self):
        """Test getting safety status"""
        manager = SafetyManager()

        status = manager.get_safety_status(
            current_open_positions=2,
            current_capital=10000
        )

        assert 'emergency_stopped' in status
        assert 'open_positions_count' in status
        assert 'daily_trades_count' in status
        assert 'daily_pnl' in status
        assert 'can_trade' in status
        assert 'warnings' in status

        assert status['emergency_stopped'] == False
        assert status['open_positions_count'] == 2
        assert isinstance(status['warnings'], list)

    def test_get_safety_status_with_warnings(self):
        """Test safety status with warnings"""
        limits = SafetyLimits(max_daily_trades=10)
        manager = SafetyManager(limits)

        # Set trades close to limit
        manager.daily_trades_count = 9

        status = manager.get_safety_status(
            current_open_positions=1,
            current_capital=10000
        )

        assert len(status['warnings']) > 0

    def test_multiple_safety_violations(self):
        """Test multiple simultaneous safety violations"""
        limits = SafetyLimits(
            max_position_size_usd=1000,
            max_open_positions=3,
            max_daily_trades=5
        )
        manager = SafetyManager(limits)

        # Set up multiple violations
        manager.daily_trades_count = 5

        can_open, reason = manager.can_open_position(
            position_size_usd=1500,  # Over limit
            current_open_positions=3  # At max
        )

        assert can_open == False
        # Should return first violation reason

    def test_safety_with_zero_capital(self):
        """Test safety checks with zero capital"""
        manager = SafetyManager()

        can_continue, reason = manager.can_continue_trading(current_capital=0)

        assert can_continue == False
        assert "Minimum capital" in reason

    def test_safety_with_negative_pnl(self):
        """Test recording negative PnL"""
        manager = SafetyManager()

        manager.record_trade(pnl=-200.0)

        assert manager.daily_pnl == -200.0
        assert manager.daily_trades_count == 1

    def test_consecutive_losses_tracking(self):
        """Test tracking consecutive losses"""
        manager = SafetyManager()

        # Record consecutive losses
        for _ in range(5):
            manager.record_trade(pnl=-100.0)

        assert manager.daily_trades_count == 5
        assert manager.daily_pnl == -500.0

    def test_safety_limits_edge_cases(self):
        """Test safety limits with edge case values"""
        # Zero limits
        limits = SafetyLimits(
            max_position_size_usd=0,
            max_open_positions=0,
            max_daily_trades=0
        )
        manager = SafetyManager(limits)

        can_open, reason = manager.can_open_position(
            position_size_usd=100,
            current_open_positions=0
        )

        assert can_open == False
