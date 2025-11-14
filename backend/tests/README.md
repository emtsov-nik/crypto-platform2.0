# Testing Documentation

Comprehensive test suite for the Crypto Trading Platform.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_strategies.py   # Strategy tests
│   ├── test_backtest_engine.py  # Backtest engine tests
│   └── test_safety_manager.py   # Safety manager tests
└── integration/             # Integration tests
    └── test_backtest_flow.py    # End-to-end backtest flow tests
```

## Running Tests

### All Tests

```bash
cd backend
pytest
```

### Unit Tests Only

```bash
pytest tests/unit -v
```

### Integration Tests Only

```bash
pytest tests/integration -v
```

### Specific Test Markers

```bash
# Run strategy tests
pytest -m strategy

# Run backtest tests
pytest -m backtest

# Run safety tests
pytest -m safety

# Run API tests
pytest -m api

# Run slow tests
pytest -m slow
```

### With Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

Coverage report will be generated in `htmlcov/` directory.

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, with dependencies)
- `@pytest.mark.strategy` - Strategy-related tests
- `@pytest.mark.backtest` - Backtest engine tests
- `@pytest.mark.safety` - Safety manager tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow-running tests

## Fixtures

### Database Fixtures

- `db_session` - Test database session
- `client` - FastAPI test client

### Data Fixtures

- `sample_ohlcv_data` - Sample price data (1000 candles)
- `sample_indicators_data` - Price data with indicators
- `sample_strategy` - Sample strategy in database
- `sample_backtest` - Sample backtest in database
- `sample_trade_data` - Sample trade data

### Strategy Fixtures

- `sample_strategy_params` - Default strategy parameters
- `sample_strategy_instance` - Instantiated strategy object

### Trading Fixtures

- `safety_limits` - Sample safety limits
- `mock_exchange` - Mock ccxt exchange object
- `mock_binance_data` - Mock Binance API response

## Writing New Tests

### Unit Test Example

```python
import pytest

@pytest.mark.unit
@pytest.mark.strategy
class TestMyStrategy:
    def test_signal_generation(self, sample_strategy_instance, sample_indicators_data):
        signal = sample_strategy_instance.generate_signal(sample_indicators_data, -1)
        assert signal in ['long', 'short', 'close', None]
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
class TestAPIFlow:
    def test_create_and_run(self, client, sample_strategy):
        response = client.post("/api/backtests/run", json={
            "strategy_id": sample_strategy.id,
            "symbol": "BTC/USDT",
            "initial_capital": 10000
        })
        assert response.status_code == 200
```

## Best Practices

1. **Use Fixtures**: Leverage existing fixtures instead of creating test data manually
2. **Mark Tests**: Always use appropriate markers (`@pytest.mark.unit`, etc.)
3. **Isolate Tests**: Each test should be independent
4. **Clear Names**: Test names should describe what they test
5. **Assert Messages**: Include clear assertion messages
6. **Mock External APIs**: Use mock objects for external services
7. **Test Edge Cases**: Include tests for boundary conditions
8. **Performance**: Keep unit tests fast (< 1s each)

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Push to claude/** branches

See `.github/workflows/tests.yml` for CI configuration.

## Coverage Goals

- **Overall**: > 80%
- **Critical modules** (strategies, backtest engine, safety manager): > 90%
- **API endpoints**: > 70%

## Troubleshooting

### Database Connection Errors

Make sure PostgreSQL is running:
```bash
docker-compose up -d postgres
```

### Import Errors

Ensure you're running tests from the `backend` directory:
```bash
cd backend
pytest
```

### Fixture Not Found

Check that `conftest.py` is in the correct location and contains the fixture.

### Slow Tests

Use `-m "not slow"` to skip slow tests during development:
```bash
pytest -m "not slow"
```

## Test Data

### Sample OHLCV Data

- 1000 candles of realistic BTC price data
- Hourly timeframe
- Base price: $40,000
- Random walk simulation
- Includes volume data

### Sample Strategy Parameters

```python
{
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "bb_period": 20,
    "bb_std": 2.0,
    "tp_percent": 2.0,
    "sl_percent": 1.0,
    "position_size_percent": 10.0
}
```

## Future Improvements

- [ ] Add performance benchmarking tests
- [ ] Add load testing for API endpoints
- [ ] Add mutation testing
- [ ] Add property-based testing with Hypothesis
- [ ] Add visual regression testing for frontend
- [ ] Add contract testing for API
- [ ] Add security testing automation
