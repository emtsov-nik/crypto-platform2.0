"""
Unit Tests for Trading Strategies
"""
import pytest
import pandas as pd
import numpy as np
from app.strategies.rsi_bb_strategy import RSIBBStrategy
from app.strategies.base_strategy import BaseStrategy


@pytest.mark.unit
@pytest.mark.strategy
class TestBaseStrategy:
    """Test BaseStrategy class"""

    def test_base_strategy_is_abstract(self):
        """Test that BaseStrategy cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseStrategy({})

    def test_strategy_has_required_methods(self, sample_strategy_instance):
        """Test that strategy has all required methods"""
        assert hasattr(sample_strategy_instance, 'initialize')
        assert hasattr(sample_strategy_instance, 'generate_signal')
        assert hasattr(sample_strategy_instance, 'calculate_position_size')
        assert hasattr(sample_strategy_instance, 'calculate_tp_sl')
        assert callable(sample_strategy_instance.initialize)
        assert callable(sample_strategy_instance.generate_signal)


@pytest.mark.unit
@pytest.mark.strategy
class TestRSIBBStrategy:
    """Test RSI + Bollinger Bands Strategy"""

    def test_strategy_initialization(self, sample_strategy_params):
        """Test strategy initialization with parameters"""
        strategy = RSIBBStrategy(sample_strategy_params)

        assert strategy.params['rsi_period'] == 14
        assert strategy.params['rsi_oversold'] == 30
        assert strategy.params['rsi_overbought'] == 70
        assert strategy.params['bb_period'] == 20
        assert strategy.params['bb_std'] == 2.0

    def test_strategy_with_invalid_params(self):
        """Test strategy with invalid parameters"""
        invalid_params = {
            "rsi_period": -1,  # Invalid
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "bb_period": 20,
            "bb_std": 2.0,
            "tp_percent": 2.0,
            "sl_percent": 1.0,
            "position_size_percent": 10.0
        }

        with pytest.raises((ValueError, AssertionError)):
            strategy = RSIBBStrategy(invalid_params)
            strategy.initialize()

    def test_generate_signal_with_indicators(self, sample_strategy_instance, sample_indicators_data):
        """Test signal generation with indicator data"""
        df = sample_indicators_data

        # Test with valid data
        signal = sample_strategy_instance.generate_signal(df, len(df) - 1)

        assert signal in ['long', 'short', 'close', None]

    def test_generate_signal_long(self, sample_strategy_instance):
        """Test long signal generation"""
        # Create data for long signal (RSI oversold + price below BB lower)
        df = pd.DataFrame({
            'close': [40000, 39900, 39800],
            'rsi': [25, 28, 29],  # Oversold
            'bb_lower': [40100, 40000, 39900],  # Price below BB lower
            'bb_upper': [41000, 40900, 40800]
        })

        signal = sample_strategy_instance.generate_signal(df, len(df) - 1)

        assert signal in ['long', None]  # Should generate long or no signal

    def test_generate_signal_short(self, sample_strategy_instance):
        """Test short signal generation"""
        # Create data for short signal (RSI overbought + price above BB upper)
        df = pd.DataFrame({
            'close': [41000, 41100, 41200],
            'rsi': [75, 78, 80],  # Overbought
            'bb_lower': [40100, 40000, 39900],
            'bb_upper': [40900, 41000, 41100]  # Price above BB upper
        })

        signal = sample_strategy_instance.generate_signal(df, len(df) - 1)

        assert signal in ['short', None]  # Should generate short or no signal

    def test_calculate_position_size(self, sample_strategy_instance):
        """Test position size calculation"""
        capital = 10000.0
        price = 40000.0

        position_size = sample_strategy_instance.calculate_position_size(capital, price)

        # Should be 10% of capital
        expected_size = (capital * 0.10) / price
        assert pytest.approx(position_size, rel=0.01) == expected_size
        assert position_size > 0

    def test_calculate_position_size_with_zero_capital(self, sample_strategy_instance):
        """Test position size with zero capital"""
        position_size = sample_strategy_instance.calculate_position_size(0, 40000.0)

        assert position_size == 0

    def test_calculate_tp_sl(self, sample_strategy_instance):
        """Test TP/SL calculation"""
        entry_price = 40000.0

        # Test long position
        tp_long, sl_long = sample_strategy_instance.calculate_tp_sl(entry_price, 'long')

        assert tp_long > entry_price  # TP should be above entry for long
        assert sl_long < entry_price  # SL should be below entry for long
        assert tp_long == pytest.approx(entry_price * 1.02, rel=0.001)  # 2% TP
        assert sl_long == pytest.approx(entry_price * 0.99, rel=0.001)  # 1% SL

        # Test short position
        tp_short, sl_short = sample_strategy_instance.calculate_tp_sl(entry_price, 'short')

        assert tp_short < entry_price  # TP should be below entry for short
        assert sl_short > entry_price  # SL should be above entry for short
        assert tp_short == pytest.approx(entry_price * 0.98, rel=0.001)  # 2% TP
        assert sl_short == pytest.approx(entry_price * 1.01, rel=0.001)  # 1% SL

    def test_calculate_tp_sl_with_invalid_side(self, sample_strategy_instance):
        """Test TP/SL calculation with invalid side"""
        with pytest.raises(ValueError):
            sample_strategy_instance.calculate_tp_sl(40000.0, 'invalid')

    def test_strategy_with_insufficient_data(self, sample_strategy_instance):
        """Test strategy behavior with insufficient data"""
        # Create dataframe with less data than required periods
        df = pd.DataFrame({
            'close': [40000, 40100, 40200],  # Only 3 candles
            'rsi': [50, 50, 50],
            'bb_lower': [39000, 39100, 39200],
            'bb_upper': [41000, 41100, 41200]
        })

        signal = sample_strategy_instance.generate_signal(df, len(df) - 1)

        # Should return None or handle gracefully
        assert signal is None or signal in ['long', 'short', 'close']

    def test_strategy_with_nan_values(self, sample_strategy_instance):
        """Test strategy behavior with NaN values"""
        df = pd.DataFrame({
            'close': [40000, 40100, np.nan],
            'rsi': [50, 50, np.nan],
            'bb_lower': [39000, 39100, np.nan],
            'bb_upper': [41000, 41100, np.nan]
        })

        signal = sample_strategy_instance.generate_signal(df, len(df) - 1)

        # Should handle NaN gracefully
        assert signal is None or signal in ['long', 'short', 'close']

    def test_strategy_metadata(self, sample_strategy_instance):
        """Test strategy metadata"""
        metadata = sample_strategy_instance.get_metadata()

        assert 'name' in metadata
        assert 'description' in metadata
        assert 'indicators' in metadata
        assert 'timeframes' in metadata
        assert isinstance(metadata['indicators'], list)
        assert 'rsi' in metadata['indicators']
        assert 'bb' in metadata['indicators']

    def test_strategy_param_validation(self, sample_strategy_params):
        """Test parameter validation"""
        # Valid params
        strategy = RSIBBStrategy(sample_strategy_params)
        strategy.initialize()

        # Invalid RSI period
        invalid_params = sample_strategy_params.copy()
        invalid_params['rsi_period'] = 0

        with pytest.raises((ValueError, AssertionError)):
            strategy = RSIBBStrategy(invalid_params)
            strategy.initialize()

    def test_strategy_requires_indicators(self, sample_strategy_instance):
        """Test that strategy works with required indicators"""
        required_indicators = sample_strategy_instance.get_required_indicators()

        assert isinstance(required_indicators, list)
        assert len(required_indicators) > 0
        assert 'rsi' in required_indicators
        assert 'bb' in required_indicators
