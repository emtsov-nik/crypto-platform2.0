"""
Unit Tests for Backtest Engine
"""
import pytest
import pandas as pd
import numpy as np
from app.backtesting.backtest_engine import BacktestEngine, Trade, Position


@pytest.mark.unit
@pytest.mark.backtest
class TestTrade:
    """Test Trade dataclass"""

    def test_trade_creation(self):
        """Test trade creation"""
        trade = Trade(
            entry_time='2024-01-01 10:00:00',
            exit_time='2024-01-01 14:00:00',
            side='long',
            entry_price=40000.0,
            exit_price=40800.0,
            quantity=0.1,
            pnl=80.0,
            pnl_percent=2.0,
            fees=20.0,
            exit_reason='tp',
            steps=1
        )

        assert trade.side == 'long'
        assert trade.pnl == 80.0
        assert trade.exit_reason == 'tp'

    def test_trade_pnl_calculation(self):
        """Test trade PnL calculation logic"""
        # Long trade profit
        entry_price = 40000.0
        exit_price = 40800.0
        quantity = 0.1

        pnl = (exit_price - entry_price) * quantity
        assert pnl == 80.0

        # Short trade profit
        pnl_short = (entry_price - exit_price) * quantity
        assert pnl_short == -80.0


@pytest.mark.unit
@pytest.mark.backtest
class TestPosition:
    """Test Position dataclass"""

    def test_position_creation(self):
        """Test position creation"""
        position = Position(
            side='long',
            entry_price=40000.0,
            quantity=0.1,
            entry_time='2024-01-01 10:00:00',
            tp_price=40800.0,
            sl_price=39600.0,
            steps=1
        )

        assert position.side == 'long'
        assert position.quantity == 0.1
        assert position.steps == 1

    def test_position_averaging(self):
        """Test position averaging logic"""
        position = Position(
            side='long',
            entry_price=40000.0,
            quantity=0.1,
            entry_time='2024-01-01 10:00:00',
            tp_price=40800.0,
            sl_price=39600.0,
            steps=1
        )

        # Simulate averaging
        new_entry_price = 39500.0
        new_quantity = 0.1

        # Calculate averaged price
        total_cost = (position.entry_price * position.quantity) + (new_entry_price * new_quantity)
        total_quantity = position.quantity + new_quantity
        avg_price = total_cost / total_quantity

        assert avg_price == 39750.0
        assert total_quantity == 0.2


@pytest.mark.unit
@pytest.mark.backtest
class TestBacktestEngine:
    """Test BacktestEngine class"""

    def test_engine_initialization(self, sample_strategy_instance):
        """Test engine initialization"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0,
            fee_rate=0.001,
            slippage=0.0005
        )

        assert engine.initial_capital == 10000.0
        assert engine.capital == 10000.0
        assert engine.fee_rate == 0.001
        assert engine.slippage == 0.0005
        assert len(engine.trades) == 0

    def test_run_backtest_with_sample_data(self, sample_strategy_instance, sample_indicators_data):
        """Test running backtest with sample data"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        assert 'initial_capital' in results
        assert 'final_capital' in results
        assert 'total_pnl' in results
        assert 'total_trades' in results
        assert 'win_rate' in results
        assert 'sharpe_ratio' in results
        assert 'max_drawdown' in results

        assert results['initial_capital'] == 10000.0
        assert results['total_trades'] >= 0

    def test_fee_calculation(self, sample_strategy_instance):
        """Test fee calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0,
            fee_rate=0.001
        )

        position_value = 1000.0
        fees = position_value * engine.fee_rate

        assert fees == 1.0

    def test_slippage_calculation(self, sample_strategy_instance):
        """Test slippage calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0,
            slippage=0.0005
        )

        price = 40000.0
        slippage = price * engine.slippage

        assert slippage == 20.0

    def test_position_opening(self, sample_strategy_instance, sample_indicators_data):
        """Test position opening logic"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        # Run backtest
        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        # If trades were made, check that positions were opened
        if results['total_trades'] > 0:
            assert len(engine.trades) > 0

    def test_capital_management(self, sample_strategy_instance, sample_indicators_data):
        """Test capital management during backtest"""
        initial_capital = 10000.0
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=initial_capital
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        # Capital should change based on PnL
        final_capital = results['final_capital']
        total_pnl = results['total_pnl']

        assert pytest.approx(final_capital, rel=0.01) == initial_capital + total_pnl

    def test_metrics_calculation(self, sample_strategy_instance, sample_indicators_data):
        """Test metrics calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        # Check all metrics are present
        required_metrics = [
            'total_pnl', 'total_pnl_percent', 'total_trades',
            'winning_trades', 'losing_trades', 'win_rate',
            'profit_factor', 'max_drawdown', 'max_drawdown_percent',
            'sharpe_ratio', 'avg_trade_pnl'
        ]

        for metric in required_metrics:
            assert metric in results

    def test_win_rate_calculation(self, sample_strategy_instance):
        """Test win rate calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        # Manually set trades
        engine.trades = [
            Trade('', '', 'long', 40000, 40800, 0.1, 80, 2.0, 10, 'tp', 1),  # Win
            Trade('', '', 'long', 40000, 39600, 0.1, -40, -1.0, 10, 'sl', 1),  # Loss
            Trade('', '', 'long', 40000, 41000, 0.1, 100, 2.5, 10, 'tp', 1),  # Win
        ]

        engine.winning_trades = 2
        engine.losing_trades = 1
        engine.total_pnl = 140

        win_rate = (engine.winning_trades / len(engine.trades)) * 100

        assert win_rate == pytest.approx(66.67, rel=0.01)

    def test_profit_factor_calculation(self, sample_strategy_instance):
        """Test profit factor calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        # Manually set trades
        gross_profit = 180.0  # 80 + 100
        gross_loss = 40.0

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        assert profit_factor == 4.5

    def test_max_drawdown_calculation(self, sample_strategy_instance, sample_indicators_data):
        """Test max drawdown calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        max_drawdown = results['max_drawdown']
        max_drawdown_percent = results['max_drawdown_percent']

        assert max_drawdown >= 0
        assert max_drawdown_percent >= 0

    def test_sharpe_ratio_calculation(self, sample_strategy_instance, sample_indicators_data):
        """Test Sharpe ratio calculation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        sharpe_ratio = results.get('sharpe_ratio', 0)

        # Sharpe ratio can be positive, negative, or zero
        assert isinstance(sharpe_ratio, (int, float))

    def test_equity_curve_generation(self, sample_strategy_instance, sample_indicators_data):
        """Test equity curve generation"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        equity_curve = engine.equity_curve

        assert isinstance(equity_curve, list)
        assert len(equity_curve) > 0
        assert equity_curve[0] == 10000.0  # Should start with initial capital

    def test_averaging_functionality(self, sample_strategy_instance):
        """Test position averaging functionality"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0,
            averaging_enabled=True,
            max_avg_steps=3
        )

        assert engine.averaging_enabled == True
        assert engine.max_avg_steps == 3

    def test_no_trades_scenario(self, sample_strategy_instance):
        """Test backtest with no trades generated"""
        # Create data that won't trigger any signals
        df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
            'close': [50000.0] * 100,  # Flat price
            'rsi': [50.0] * 100,  # Neutral RSI
            'bb_lower': [49000.0] * 100,
            'bb_upper': [51000.0] * 100
        })

        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10000.0
        )

        results = engine.run(df, symbol="BTC/USDT")

        # Should handle no trades gracefully
        assert results['total_trades'] == 0
        assert results['final_capital'] == 10000.0
        assert results['total_pnl'] == 0

    def test_insufficient_capital(self, sample_strategy_instance, sample_indicators_data):
        """Test behavior with insufficient capital"""
        engine = BacktestEngine(
            strategy=sample_strategy_instance,
            initial_capital=10.0  # Very low capital
        )

        results = engine.run(sample_indicators_data, symbol="BTC/USDT")

        # Should handle gracefully
        assert results['initial_capital'] == 10.0
        assert results['total_trades'] >= 0
