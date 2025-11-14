# Strategy Examples

Comprehensive guide to creating custom trading strategies.

## Table of Contents

- [Strategy Basics](#strategy-basics)
- [BaseStrategy API](#basestrategy-api)
- [Example 1: Simple MA Crossover](#example-1-simple-ma-crossover)
- [Example 2: MACD Strategy](#example-2-macd-strategy)
- [Example 3: Breakout Strategy](#example-3-breakout-strategy)
- [Example 4: Mean Reversion](#example-4-mean-reversion)
- [Example 5: Multi-Indicator Strategy](#example-5-multi-indicator-strategy)
- [Testing Your Strategy](#testing-your-strategy)
- [Best Practices](#best-practices)

## Strategy Basics

### What is a Trading Strategy?

A trading strategy is a set of rules that determines:
1. **When to enter** a position (buy/sell signals)
2. **Position size** (how much to trade)
3. **When to exit** a position (take profit/stop loss)
4. **Risk management** (maximum loss, position limits)

### Strategy Lifecycle

```
1. Initialize
   ↓
2. Load historical data
   ↓
3. Calculate indicators
   ↓
4. Loop through each candle:
   ├─ Generate signal (long/short/close)
   ├─ Calculate position size
   ├─ Calculate TP/SL levels
   └─ Execute trade (if signal present)
   ↓
5. Calculate performance metrics
```

### Strategy Components

Every strategy must implement:
- `initialize()` - Setup parameters and state
- `generate_signal()` - Entry/exit logic
- `calculate_position_size()` - Position sizing
- `calculate_tp_sl()` - Take profit and stop loss levels

## BaseStrategy API

### Class Definition

```python
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Tuple, Dict, Any

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""

    def __init__(self, params: Dict[str, Any]):
        """Initialize strategy with parameters.

        Args:
            params: Strategy parameters dictionary
        """
        self.params = params
        self.position = None  # Current position: None, 'long', 'short'
        self.initialize()

    @abstractmethod
    def initialize(self):
        """Initialize strategy-specific parameters and state.

        Override this method to set up your strategy.
        """
        pass

    @abstractmethod
    def generate_signal(
        self,
        df: pd.DataFrame,
        index: int
    ) -> Optional[str]:
        """Generate trading signal.

        Args:
            df: DataFrame with OHLCV data and indicators
            index: Current candle index

        Returns:
            'long': Open long position
            'short': Open short position
            'close': Close current position
            None: No action
        """
        pass

    @abstractmethod
    def calculate_position_size(
        self,
        capital: float,
        price: float
    ) -> float:
        """Calculate position size.

        Args:
            capital: Available capital in quote currency
            price: Current price

        Returns:
            Position size in base currency
        """
        pass

    @abstractmethod
    def calculate_tp_sl(
        self,
        entry_price: float,
        side: str
    ) -> Tuple[float, float]:
        """Calculate take profit and stop loss prices.

        Args:
            entry_price: Position entry price
            side: 'long' or 'short'

        Returns:
            (take_profit_price, stop_loss_price)
        """
        pass
```

### Available Data

The `df` DataFrame contains:
- **OHLCV:** `open`, `high`, `low`, `close`, `volume`
- **Indicators:** `rsi`, `bb_upper`, `bb_middle`, `bb_lower`, `sma_20`, `ema_20`, etc.
- **Timestamps:** `timestamp` (datetime index)

### Position State

- `self.position` - Current position state:
  - `None` - No position open
  - `'long'` - Long position open
  - `'short'` - Short position open

## Example 1: Simple MA Crossover

Classic moving average crossover strategy.

### Strategy Logic

- **Entry Long:** Fast MA crosses above Slow MA
- **Entry Short:** Fast MA crosses below Slow MA
- **Exit:** Reverse signal or TP/SL hit

### Implementation

```python
# strategies/ma_crossover_strategy.py
from app.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Tuple

class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover Strategy.

    Signals:
    - Long: Fast MA crosses above Slow MA
    - Short: Fast MA crosses below Slow MA
    """

    def initialize(self):
        """Initialize parameters."""
        self.fast_period = self.params.get('fast_period', 10)
        self.slow_period = self.params.get('slow_period', 30)
        self.tp_percent = self.params.get('tp_percent', 2.0)
        self.sl_percent = self.params.get('sl_percent', 1.0)
        self.position_size_percent = self.params.get('position_size_percent', 10.0)

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Generate signal based on MA crossover."""
        # Need enough history
        if index < self.slow_period:
            return None

        # Get current and previous values
        fast_ma_current = df.iloc[index][f'sma_{self.fast_period}']
        slow_ma_current = df.iloc[index][f'sma_{self.slow_period}']
        fast_ma_prev = df.iloc[index - 1][f'sma_{self.fast_period}']
        slow_ma_prev = df.iloc[index - 1][f'sma_{self.slow_period}']

        # Check for crossover
        bullish_cross = (fast_ma_prev <= slow_ma_prev and
                        fast_ma_current > slow_ma_current)
        bearish_cross = (fast_ma_prev >= slow_ma_prev and
                        fast_ma_current < slow_ma_current)

        if self.position is None:
            # Entry signals
            if bullish_cross:
                return 'long'
            elif bearish_cross:
                return 'short'
        else:
            # Exit signals (reverse)
            if self.position == 'long' and bearish_cross:
                return 'close'
            elif self.position == 'short' and bullish_cross:
                return 'close'

        return None

    def calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size as percentage of capital."""
        size = (capital * self.position_size_percent / 100) / price
        return round(size, 8)

    def calculate_tp_sl(self, entry_price: float, side: str) -> Tuple[float, float]:
        """Calculate TP and SL based on percentage."""
        if side == 'long':
            tp = entry_price * (1 + self.tp_percent / 100)
            sl = entry_price * (1 - self.sl_percent / 100)
        else:  # short
            tp = entry_price * (1 - self.tp_percent / 100)
            sl = entry_price * (1 + self.sl_percent / 100)

        return round(tp, 2), round(sl, 2)
```

### Usage

```python
# Create strategy
params = {
    'fast_period': 10,
    'slow_period': 30,
    'tp_percent': 2.0,
    'sl_percent': 1.0,
    'position_size_percent': 10.0
}

strategy = MACrossoverStrategy(params)

# Add to registry
from app.strategies.strategy_registry import STRATEGY_REGISTRY
STRATEGY_REGISTRY['ma_crossover'] = MACrossoverStrategy
```

## Example 2: MACD Strategy

MACD (Moving Average Convergence Divergence) strategy.

### Strategy Logic

- **Entry Long:** MACD line crosses above signal line and MACD > 0
- **Entry Short:** MACD line crosses below signal line and MACD < 0
- **Exit:** Reverse crossover or TP/SL

### Implementation

```python
# strategies/macd_strategy.py
from app.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Tuple

class MACDStrategy(BaseStrategy):
    """MACD Crossover Strategy."""

    def initialize(self):
        """Initialize parameters."""
        self.fast_period = self.params.get('fast_period', 12)
        self.slow_period = self.params.get('slow_period', 26)
        self.signal_period = self.params.get('signal_period', 9)
        self.tp_percent = self.params.get('tp_percent', 2.5)
        self.sl_percent = self.params.get('sl_percent', 1.5)
        self.position_size_percent = self.params.get('position_size_percent', 15.0)

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Generate signal based on MACD crossover."""
        if index < self.slow_period + self.signal_period:
            return None

        # Get MACD values
        macd = df.iloc[index]['macd']
        macd_signal = df.iloc[index]['macd_signal']
        macd_prev = df.iloc[index - 1]['macd']
        macd_signal_prev = df.iloc[index - 1]['macd_signal']

        # Detect crossovers
        bullish_cross = (macd_prev <= macd_signal_prev and
                        macd > macd_signal and
                        macd > 0)  # Above zero line

        bearish_cross = (macd_prev >= macd_signal_prev and
                        macd < macd_signal and
                        macd < 0)  # Below zero line

        if self.position is None:
            if bullish_cross:
                return 'long'
            elif bearish_cross:
                return 'short'
        else:
            # Exit on reverse crossover
            if self.position == 'long' and macd < macd_signal:
                return 'close'
            elif self.position == 'short' and macd > macd_signal:
                return 'close'

        return None

    def calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size."""
        size = (capital * self.position_size_percent / 100) / price
        return round(size, 8)

    def calculate_tp_sl(self, entry_price: float, side: str) -> Tuple[float, float]:
        """Calculate TP and SL."""
        if side == 'long':
            tp = entry_price * (1 + self.tp_percent / 100)
            sl = entry_price * (1 - self.sl_percent / 100)
        else:
            tp = entry_price * (1 - self.tp_percent / 100)
            sl = entry_price * (1 + self.sl_percent / 100)

        return round(tp, 2), round(sl, 2)
```

## Example 3: Breakout Strategy

Support/resistance breakout strategy.

### Strategy Logic

- **Entry Long:** Price breaks above resistance (20-period high)
- **Entry Short:** Price breaks below support (20-period low)
- **Exit:** TP/SL or move back within range

### Implementation

```python
# strategies/breakout_strategy.py
from app.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Tuple

class BreakoutStrategy(BaseStrategy):
    """Breakout Strategy based on support/resistance."""

    def initialize(self):
        """Initialize parameters."""
        self.period = self.params.get('period', 20)
        self.atr_multiplier = self.params.get('atr_multiplier', 1.5)
        self.position_size_percent = self.params.get('position_size_percent', 10.0)

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Generate breakout signal."""
        if index < self.period:
            return None

        # Get current price and range
        current_close = df.iloc[index]['close']
        resistance = df.iloc[index - self.period:index]['high'].max()
        support = df.iloc[index - self.period:index]['low'].min()
        atr = df.iloc[index]['atr']

        if self.position is None:
            # Breakout above resistance
            if current_close > resistance:
                return 'long'
            # Breakdown below support
            elif current_close < support:
                return 'short'
        else:
            # Exit if price moves back into range
            if self.position == 'long' and current_close < support:
                return 'close'
            elif self.position == 'short' and current_close > resistance:
                return 'close'

        return None

    def calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size."""
        size = (capital * self.position_size_percent / 100) / price
        return round(size, 8)

    def calculate_tp_sl(self, entry_price: float, side: str) -> Tuple[float, float]:
        """Calculate TP and SL using ATR.

        Uses ATR for dynamic stop loss placement.
        """
        # Get current ATR (would need to pass df or store it)
        # For simplicity, using fixed percentage here
        tp_multiplier = self.atr_multiplier * 2
        sl_multiplier = self.atr_multiplier

        if side == 'long':
            tp = entry_price * (1 + tp_multiplier / 100)
            sl = entry_price * (1 - sl_multiplier / 100)
        else:
            tp = entry_price * (1 - tp_multiplier / 100)
            sl = entry_price * (1 + sl_multiplier / 100)

        return round(tp, 2), round(sl, 2)
```

## Example 4: Mean Reversion

Bollinger Bands mean reversion strategy.

### Strategy Logic

- **Entry Long:** Price < Lower BB and RSI < 30 (oversold)
- **Entry Short:** Price > Upper BB and RSI > 70 (overbought)
- **Exit:** Price returns to middle BB

### Implementation

```python
# strategies/mean_reversion_strategy.py
from app.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Tuple

class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion Strategy using Bollinger Bands."""

    def initialize(self):
        """Initialize parameters."""
        self.bb_period = self.params.get('bb_period', 20)
        self.bb_std = self.params.get('bb_std', 2.0)
        self.rsi_period = self.params.get('rsi_period', 14)
        self.rsi_oversold = self.params.get('rsi_oversold', 30)
        self.rsi_overbought = self.params.get('rsi_overbought', 70)
        self.tp_percent = self.params.get('tp_percent', 1.5)
        self.sl_percent = self.params.get('sl_percent', 2.0)
        self.position_size_percent = self.params.get('position_size_percent', 10.0)

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Generate mean reversion signal."""
        if index < max(self.bb_period, self.rsi_period):
            return None

        # Get current values
        close = df.iloc[index]['close']
        bb_upper = df.iloc[index]['bb_upper']
        bb_lower = df.iloc[index]['bb_lower']
        bb_middle = df.iloc[index]['bb_middle']
        rsi = df.iloc[index]['rsi']

        if self.position is None:
            # Oversold: buy when price hits lower BB and RSI confirms
            if close <= bb_lower and rsi < self.rsi_oversold:
                return 'long'
            # Overbought: sell when price hits upper BB and RSI confirms
            elif close >= bb_upper and rsi > self.rsi_overbought:
                return 'short'
        else:
            # Exit when price returns to middle BB
            if self.position == 'long' and close >= bb_middle:
                return 'close'
            elif self.position == 'short' and close <= bb_middle:
                return 'close'

        return None

    def calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size."""
        size = (capital * self.position_size_percent / 100) / price
        return round(size, 8)

    def calculate_tp_sl(self, entry_price: float, side: str) -> Tuple[float, float]:
        """Calculate TP and SL."""
        if side == 'long':
            tp = entry_price * (1 + self.tp_percent / 100)
            sl = entry_price * (1 - self.sl_percent / 100)
        else:
            tp = entry_price * (1 - self.tp_percent / 100)
            sl = entry_price * (1 + self.sl_percent / 100)

        return round(tp, 2), round(sl, 2)
```

## Example 5: Multi-Indicator Strategy

Advanced strategy combining multiple indicators.

### Strategy Logic

Combines RSI, MACD, and Bollinger Bands for confirmation:
- **Entry Long:** RSI < 40 AND MACD bullish cross AND Price near lower BB
- **Entry Short:** RSI > 60 AND MACD bearish cross AND Price near upper BB
- **Exit:** Any indicator shows reversal

### Implementation

```python
# strategies/multi_indicator_strategy.py
from app.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Tuple

class MultiIndicatorStrategy(BaseStrategy):
    """Advanced strategy combining multiple indicators."""

    def initialize(self):
        """Initialize parameters."""
        # RSI parameters
        self.rsi_period = self.params.get('rsi_period', 14)
        self.rsi_long_threshold = self.params.get('rsi_long_threshold', 40)
        self.rsi_short_threshold = self.params.get('rsi_short_threshold', 60)

        # Bollinger Bands parameters
        self.bb_period = self.params.get('bb_period', 20)
        self.bb_std = self.params.get('bb_std', 2.0)
        self.bb_proximity_percent = self.params.get('bb_proximity_percent', 5.0)

        # MACD parameters
        self.macd_fast = self.params.get('macd_fast', 12)
        self.macd_slow = self.params.get('macd_slow', 26)
        self.macd_signal = self.params.get('macd_signal', 9)

        # Position parameters
        self.tp_percent = self.params.get('tp_percent', 3.0)
        self.sl_percent = self.params.get('sl_percent', 1.5)
        self.position_size_percent = self.params.get('position_size_percent', 10.0)

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Generate signal based on multiple indicators."""
        min_period = max(self.rsi_period, self.bb_period,
                        self.macd_slow + self.macd_signal)

        if index < min_period + 1:
            return None

        # Get current values
        close = df.iloc[index]['close']
        rsi = df.iloc[index]['rsi']
        bb_upper = df.iloc[index]['bb_upper']
        bb_lower = df.iloc[index]['bb_lower']
        macd = df.iloc[index]['macd']
        macd_signal = df.iloc[index]['macd_signal']
        macd_prev = df.iloc[index - 1]['macd']
        macd_signal_prev = df.iloc[index - 1]['macd_signal']

        # Check MACD crossovers
        macd_bullish_cross = (macd_prev <= macd_signal_prev and
                             macd > macd_signal)
        macd_bearish_cross = (macd_prev >= macd_signal_prev and
                             macd < macd_signal)

        # Check BB proximity
        bb_range = bb_upper - bb_lower
        near_lower_bb = (close - bb_lower) / bb_range < (self.bb_proximity_percent / 100)
        near_upper_bb = (bb_upper - close) / bb_range < (self.bb_proximity_percent / 100)

        if self.position is None:
            # Long entry: All conditions must be met
            long_conditions = [
                rsi < self.rsi_long_threshold,  # Oversold
                macd_bullish_cross,              # MACD turning bullish
                near_lower_bb                    # Price near support
            ]

            if all(long_conditions):
                return 'long'

            # Short entry: All conditions must be met
            short_conditions = [
                rsi > self.rsi_short_threshold,  # Overbought
                macd_bearish_cross,               # MACD turning bearish
                near_upper_bb                     # Price near resistance
            ]

            if all(short_conditions):
                return 'short'

        else:
            # Exit on any reversal signal
            if self.position == 'long':
                exit_long = [
                    rsi > 70,                    # Overbought
                    macd_bearish_cross,          # MACD turning bearish
                    close > bb_upper             # Price above resistance
                ]
                if any(exit_long):
                    return 'close'

            elif self.position == 'short':
                exit_short = [
                    rsi < 30,                    # Oversold
                    macd_bullish_cross,          # MACD turning bullish
                    close < bb_lower             # Price below support
                ]
                if any(exit_short):
                    return 'close'

        return None

    def calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size."""
        size = (capital * self.position_size_percent / 100) / price
        return round(size, 8)

    def calculate_tp_sl(self, entry_price: float, side: str) -> Tuple[float, float]:
        """Calculate TP and SL."""
        if side == 'long':
            tp = entry_price * (1 + self.tp_percent / 100)
            sl = entry_price * (1 - self.sl_percent / 100)
        else:
            tp = entry_price * (1 - self.tp_percent / 100)
            sl = entry_price * (1 + self.sl_percent / 100)

        return round(tp, 2), round(sl, 2)
```

## Testing Your Strategy

### 1. Unit Testing

```python
# tests/unit/test_my_strategy.py
import pytest
import pandas as pd
from app.strategies.my_strategy import MyStrategy

@pytest.mark.unit
@pytest.mark.strategy
class TestMyStrategy:
    def test_initialization(self):
        """Test strategy initializes correctly."""
        params = {'period': 20, 'tp_percent': 2.0}
        strategy = MyStrategy(params)

        assert strategy.period == 20
        assert strategy.tp_percent == 2.0

    def test_signal_generation(self, sample_indicators_data):
        """Test signal generation logic."""
        params = {'period': 14}
        strategy = MyStrategy(params)

        signal = strategy.generate_signal(sample_indicators_data, -1)

        assert signal in ['long', 'short', 'close', None]

    def test_position_sizing(self):
        """Test position size calculation."""
        params = {'position_size_percent': 10.0}
        strategy = MyStrategy(params)

        size = strategy.calculate_position_size(10000, 40000)

        assert size > 0
        assert size < 1  # For BTC at $40k with 10% of $10k

    def test_tp_sl_calculation(self):
        """Test TP/SL calculation."""
        params = {'tp_percent': 2.0, 'sl_percent': 1.0}
        strategy = MyStrategy(params)

        tp, sl = strategy.calculate_tp_sl(40000, 'long')

        assert tp == 40800  # 40000 * 1.02
        assert sl == 39600  # 40000 * 0.99
```

### 2. Backtesting

```python
# Run backtest via API or service
from app.services.backtest_service import BacktestService
from app.backtesting.backtest_engine import BacktestEngine

# Create backtest
backtest_data = {
    'strategy_id': 1,
    'symbol': 'BTC/USDT',
    'timeframe': '1h',
    'initial_capital': 10000,
    'start_date': '2024-01-01',
    'end_date': '2024-03-01'
}

# Run backtest
service = BacktestService(db)
results = await service.run_backtest(backtest_data)

# Analyze results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

### 3. Paper Trading

Test on testnet before live trading:

```bash
# Set testnet in .env
BINANCE_TESTNET=true

# Start trading with your strategy
curl -X POST "http://localhost:8000/api/trading/start" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": 1,
    "symbol": "BTC/USDT",
    "timeframe": "1h"
  }'
```

## Best Practices

### 1. Strategy Design

**✅ DO:**
- Keep strategies simple and explainable
- Use well-known indicators
- Define clear entry/exit rules
- Include risk management (TP/SL)
- Test on multiple timeframes and symbols

**❌ DON'T:**
- Over-complicate with too many indicators
- Use magic numbers without explanation
- Rely on a single indicator
- Ignore risk management
- Optimize only for historical data

### 2. Parameter Selection

**Good Parameter Ranges:**
- RSI: 14-21 period
- Moving Averages: 10, 20, 50, 100, 200
- Bollinger Bands: 20 period, 2 std dev
- Stop Loss: 0.5-2% for crypto
- Take Profit: 1.5-3% for crypto
- Position Size: 5-15% of capital

**Parameter Optimization:**
1. Start with defaults
2. Test variations systematically
3. Use walk-forward analysis
4. Validate on out-of-sample data

### 3. Risk Management

```python
def calculate_position_size_kelly(
    self,
    capital: float,
    price: float,
    win_rate: float,
    avg_win: float,
    avg_loss: float
) -> float:
    """Calculate position size using Kelly Criterion.

    Kelly% = W - [(1-W) / R]
    where W = win rate, R = avg_win / avg_loss
    """
    if avg_loss == 0:
        return 0

    r = avg_win / abs(avg_loss)
    kelly_percent = win_rate - ((1 - win_rate) / r)

    # Use fractional Kelly (e.g., 25% of Kelly)
    fractional_kelly = kelly_percent * 0.25

    # Cap at maximum position size
    max_position_percent = self.params.get('max_position_percent', 10.0)
    position_percent = min(fractional_kelly * 100, max_position_percent)

    size = (capital * position_percent / 100) / price
    return round(size, 8)
```

### 4. Performance Metrics

Monitor these key metrics:
- **Win Rate:** > 50% (ideally 55-65%)
- **Profit Factor:** > 1.5
- **Sharpe Ratio:** > 1.0
- **Max Drawdown:** < 20%
- **Average Trade:** Positive and meaningful

### 5. Common Pitfalls

**1. Look-Ahead Bias:**
```python
# ❌ WRONG: Using future data
signal = df.iloc[index + 1]['close'] > df.iloc[index]['close']

# ✅ CORRECT: Only use past and current data
signal = df.iloc[index]['close'] > df.iloc[index - 1]['close']
```

**2. Survivorship Bias:**
- Test on delisted/dead coins too
- Don't only test on winners

**3. Overfitting:**
```python
# ❌ WRONG: Too many conditions
if (rsi < 31.2 and macd > 0.0042 and volume > 12345.67):
    return 'long'

# ✅ CORRECT: Simple, robust conditions
if (rsi < 30 and macd > 0):
    return 'long'
```

### 6. Documentation

Always document your strategy:

```python
class MyStrategy(BaseStrategy):
    """
    My Custom Strategy

    **Logic:**
    - Entry Long: Condition A and Condition B
    - Entry Short: Condition C and Condition D
    - Exit: TP/SL or reverse signal

    **Parameters:**
    - period: Indicator period (default: 14)
    - tp_percent: Take profit % (default: 2.0)
    - sl_percent: Stop loss % (default: 1.0)

    **Performance:**
    - Tested on BTC/USDT 1h (2024-01-01 to 2024-03-01)
    - Win Rate: 58.5%
    - Sharpe Ratio: 1.85
    - Max Drawdown: 12.3%

    **Risk:**
    - Medium risk
    - Suitable for trending markets
    - Use stop losses
    """
```

## Resources

### Learning Materials

- [Investopedia - Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)
- [TradingView - Ideas](https://www.tradingview.com/ideas/)
- [QuantConnect - Tutorials](https://www.quantconnect.com/tutorials)

### Indicator Documentation

- [ta Library Docs](https://technical-analysis-library-in-python.readthedocs.io/)
- [pandas-ta](https://github.com/twopirllc/pandas-ta)

### Books

- "Technical Analysis of the Financial Markets" by John Murphy
- "Trading Systems and Methods" by Perry Kaufman
- "Evidence-Based Technical Analysis" by David Aronson

---

**Previous:** [Developer Guide](DEVELOPER_GUIDE.md) | **Next:** [Deployment Guide](DEPLOYMENT.md)
