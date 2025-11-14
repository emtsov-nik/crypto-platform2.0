#!/usr/bin/env python3
"""
Simple test script for strategy system
"""
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing Strategy System...\n")

# Test 1: Import modules
print("1. Testing imports...")
try:
    from app.strategies.base_strategy import BaseStrategy
    from app.strategies.rsi_bb_strategy import RSIBBStrategy
    from app.services.strategy_loader import StrategyLoader, get_strategy_loader
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Load strategies
print("\n2. Testing strategy loader...")
try:
    loader = get_strategy_loader()
    available = loader.list_strategies()
    print(f"   ✓ Loaded {len(available)} strategies")
    for strategy in available:
        print(f"     - {strategy['name']}: {strategy['class_name']}")
except Exception as e:
    print(f"   ✗ Strategy loader failed: {e}")
    sys.exit(1)

# Test 3: Instantiate RSI+BB Strategy
print("\n3. Testing RSI+BB Strategy instantiation...")
try:
    params = {
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'bb_period': 20,
        'bb_std': 2.0,
        'atr_period': 14,
        'risk_percent': 1.0,
        'risk_reward_ratio': 2.0,
        'max_steps': 3,
        'step_distance_percent': 2.0,
    }

    strategy = RSIBBStrategy(params)
    print("   ✓ Strategy instantiated successfully")
    print(f"     Name: {strategy.name}")

    metadata = strategy.get_metadata()
    print(f"     Indicators: {metadata['indicators']}")
    print(f"     Risk Level: {metadata['risk_level']}")
except Exception as e:
    print(f"   ✗ Strategy instantiation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test with sample data
print("\n4. Testing strategy with sample data...")
try:
    import pandas as pd
    import numpy as np

    # Create sample OHLCV data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)

    # Generate sample price data with trend
    base_price = 40000
    price_changes = np.random.randn(100) * 100
    closes = base_price + np.cumsum(price_changes)

    df = pd.DataFrame({
        'timestamp': dates,
        'open': closes - np.random.rand(100) * 50,
        'high': closes + np.random.rand(100) * 100,
        'low': closes - np.random.rand(100) * 100,
        'close': closes,
        'volume': np.random.randint(100, 1000, 100)
    })

    print(f"   Created sample data: {len(df)} candles")

    # Prepare data with indicators
    df_prepared = strategy.prepare_data(df)
    print(f"   ✓ Data prepared with indicators")
    print(f"     Columns: {', '.join([c for c in df_prepared.columns if c not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']])}")

    # Generate signals
    signals = []
    for i in range(50, len(df_prepared)):  # Start after indicator warm-up
        signal = strategy.generate_signal(df_prepared, i)
        if signal:
            signals.append((i, signal, df_prepared.iloc[i]['close']))

    print(f"   ✓ Generated {len(signals)} signals")
    if signals:
        for idx, signal, price in signals[:3]:  # Show first 3 signals
            print(f"     - Candle {idx}: {signal.upper()} at ${price:.2f}")

except Exception as e:
    print(f"   ✗ Testing with sample data failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test position sizing and exit prices
print("\n5. Testing position sizing and exit prices...")
try:
    capital = 10000  # $10,000
    price = 40000

    position_size = strategy.calculate_position_size(capital, price, step=0)
    print(f"   ✓ Position size calculated: {position_size:.6f} BTC")

    tp, sl = strategy.calculate_exit_prices(price, 'long')
    print(f"   ✓ Exit prices calculated:")
    print(f"     Take Profit: ${tp:.2f} ({((tp/price - 1) * 100):.2f}%)")
    print(f"     Stop Loss: ${sl:.2f} ({((sl/price - 1) * 100):.2f}%)")

except Exception as e:
    print(f"   ✗ Position sizing/exit prices failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("All tests passed! ✓")
print("="*50)
