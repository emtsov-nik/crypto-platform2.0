"""
Pytest Configuration and Fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.strategy import Strategy
from app.models.backtest import Backtest


# Test Database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1H')
    np.random.seed(42)

    # Generate realistic price data
    base_price = 40000
    price_changes = np.random.randn(1000) * 100
    close_prices = base_price + np.cumsum(price_changes)

    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + np.random.randn(1000) * 50,
        'high': close_prices + np.abs(np.random.randn(1000) * 100),
        'low': close_prices - np.abs(np.random.randn(1000) * 100),
        'close': close_prices,
        'volume': np.random.randint(100, 1000, 1000) * 1000
    })

    return data


@pytest.fixture
def sample_strategy_params():
    """Sample strategy parameters"""
    return {
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "bb_period": 20,
        "bb_std": 2.0,
        "tp_percent": 2.0,
        "sl_percent": 1.0,
        "position_size_percent": 10.0
    }


@pytest.fixture
def sample_strategy(db_session, sample_strategy_params):
    """Create sample strategy in database"""
    strategy = Strategy(
        name="Test RSI BB Strategy",
        description="Test strategy for unit tests",
        class_name="RSIBBStrategy",
        params=sample_strategy_params,
        is_active=True
    )
    db_session.add(strategy)
    db_session.commit()
    db_session.refresh(strategy)
    return strategy


@pytest.fixture
def sample_backtest(db_session, sample_strategy):
    """Create sample backtest in database"""
    backtest = Backtest(
        strategy_id=sample_strategy.id,
        symbol="BTC/USDT",
        timeframe="1h",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        initial_capital=10000.0,
        status="pending",
        params=sample_strategy.params
    )
    db_session.add(backtest)
    db_session.commit()
    db_session.refresh(backtest)
    return backtest


@pytest.fixture
def mock_binance_data():
    """Mock Binance API response data"""
    return {
        'symbol': 'BTCUSDT',
        'price': '45000.50',
        'bidPrice': '44999.00',
        'askPrice': '45001.00',
        'high': '46000.00',
        'low': '44000.00',
        'volume': '1234.56',
        'quoteVolume': '55000000.00'
    }


@pytest.fixture
def sample_indicators_data(sample_ohlcv_data):
    """Sample data with calculated indicators"""
    from app.services.indicators import calculate_indicators

    df = sample_ohlcv_data.copy()
    df = calculate_indicators(
        df,
        indicators=['rsi', 'bb', 'sma_7', 'sma_25', 'ema_12', 'ema_26']
    )
    return df


@pytest.fixture
def safety_limits():
    """Sample safety limits for testing"""
    return {
        "max_position_size_usd": 1000,
        "max_open_positions": 3,
        "max_daily_trades": 10,
        "max_daily_loss_percent": 5.0,
        "min_capital_usd": 100,
        "max_total_loss_percent": 20.0
    }


@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing"""
    return {
        'id': 1,
        'entry_time': '2024-01-01 10:00:00',
        'exit_time': '2024-01-01 14:00:00',
        'side': 'long',
        'entry_price': 40000.0,
        'exit_price': 40800.0,
        'quantity': 0.1,
        'pnl': 80.0,
        'pnl_percent': 2.0,
        'fees': 20.0,
        'exit_reason': 'tp',
        'steps': 1
    }


@pytest.fixture
def mock_exchange():
    """Mock ccxt exchange object"""
    class MockExchange:
        def __init__(self):
            self.markets = {
                'BTC/USDT': {
                    'id': 'BTCUSDT',
                    'symbol': 'BTC/USDT',
                    'base': 'BTC',
                    'quote': 'USDT',
                    'active': True
                }
            }

        def fetch_balance(self):
            return {
                'USDT': {'free': 10000.0, 'used': 0.0, 'total': 10000.0},
                'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0}
            }

        def fetch_ticker(self, symbol):
            return {
                'symbol': symbol,
                'last': 45000.0,
                'bid': 44999.0,
                'ask': 45001.0,
                'high': 46000.0,
                'low': 44000.0,
                'volume': 1234.56
            }

        def create_order(self, symbol, order_type, side, amount, price=None):
            return {
                'id': 'test_order_123',
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'price': price or 45000.0,
                'status': 'closed',
                'filled': amount
            }

        def fetch_order(self, order_id, symbol):
            return {
                'id': order_id,
                'symbol': symbol,
                'status': 'closed',
                'filled': 0.1,
                'remaining': 0.0
            }

    return MockExchange()


@pytest.fixture
def sample_strategy_instance():
    """Sample strategy instance for testing"""
    from app.strategies.rsi_bb_strategy import RSIBBStrategy

    params = {
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "bb_period": 20,
        "bb_std": 2.0,
        "tp_percent": 2.0,
        "sl_percent": 1.0,
        "position_size_percent": 10.0
    }

    return RSIBBStrategy(params)
