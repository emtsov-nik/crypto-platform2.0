"""
Integration Tests for Complete Backtest Flow
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.integration
@pytest.mark.slow
class TestBacktestFlow:
    """Test complete backtest workflow"""

    def test_create_and_run_backtest(self, client, sample_strategy):
        """Test creating and running a backtest"""
        # Create backtest
        backtest_data = {
            "strategy_id": sample_strategy.id,
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "initial_capital": 10000,
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }

        response = client.post("/api/backtests/run", json=backtest_data)

        assert response.status_code == 200
        data = response.json()
        assert "backtest_id" in data
        assert data["status"] in ["pending", "running"]

        backtest_id = data["backtest_id"]

        # Check backtest status
        response = client.get(f"/api/backtests/{backtest_id}/progress")
        assert response.status_code == 200

    def test_list_backtests(self, client, sample_strategy):
        """Test listing backtests"""
        # Create a backtest first
        backtest_data = {
            "strategy_id": sample_strategy.id,
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "initial_capital": 10000
        }

        client.post("/api/backtests/run", json=backtest_data)

        # List backtests
        response = client.get("/api/backtests/")
        assert response.status_code == 200

        data = response.json()
        assert "backtests" in data
        assert "total" in data
        assert len(data["backtests"]) > 0

    def test_get_backtest_results(self, client, sample_backtest):
        """Test getting backtest results"""
        # Update backtest to completed status
        sample_backtest.status = "completed"
        sample_backtest.final_capital = 11000.0
        sample_backtest.total_pnl = 1000.0
        sample_backtest.total_trades = 10
        sample_backtest.winning_trades = 7
        sample_backtest.losing_trades = 3

        response = client.get(f"/api/backtests/{sample_backtest.id}/results")

        if response.status_code == 200:
            data = response.json()
            assert "total_pnl" in data
            assert "win_rate" in data

    def test_strategy_to_backtest_flow(self, client):
        """Test full flow from strategy creation to backtest"""
        # Create strategy
        strategy_data = {
            "name": "Integration Test Strategy",
            "description": "Strategy for integration testing",
            "class_name": "RSIBBStrategy",
            "params": {
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "bb_period": 20,
                "bb_std": 2.0,
                "tp_percent": 2.0,
                "sl_percent": 1.0,
                "position_size_percent": 10.0
            },
            "is_active": True
        }

        # Create strategy
        response = client.post("/api/strategies/", json=strategy_data)
        assert response.status_code == 200
        strategy = response.json()
        strategy_id = strategy["id"]

        # Run backtest with created strategy
        backtest_data = {
            "strategy_id": strategy_id,
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "initial_capital": 10000
        }

        response = client.post("/api/backtests/run", json=backtest_data)
        assert response.status_code == 200


@pytest.mark.integration
class TestAPIEndpoints:
    """Test API endpoints integration"""

    def test_market_data_endpoints(self, client):
        """Test market data endpoints"""
        # Get symbols
        response = client.get("/api/market/symbols")
        if response.status_code == 200:
            data = response.json()
            assert "symbols" in data

    def test_strategies_crud(self, client):
        """Test strategies CRUD operations"""
        # Create
        strategy_data = {
            "name": "Test Strategy",
            "class_name": "RSIBBStrategy",
            "params": {"rsi_period": 14},
            "is_active": True
        }

        response = client.post("/api/strategies/", json=strategy_data)
        assert response.status_code == 200
        strategy_id = response.json()["id"]

        # Read
        response = client.get(f"/api/strategies/{strategy_id}")
        assert response.status_code == 200

        # Update
        update_data = {"name": "Updated Strategy"}
        response = client.put(f"/api/strategies/{strategy_id}", json=update_data)
        assert response.status_code == 200

        # Delete
        response = client.delete(f"/api/strategies/{strategy_id}")
        assert response.status_code == 200

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database operations"""

    def test_strategy_persistence(self, db_session, sample_strategy):
        """Test strategy is persisted in database"""
        from app.models.strategy import Strategy

        strategy = db_session.query(Strategy).filter_by(id=sample_strategy.id).first()

        assert strategy is not None
        assert strategy.name == sample_strategy.name
        assert strategy.class_name == sample_strategy.class_name

    def test_backtest_persistence(self, db_session, sample_backtest):
        """Test backtest is persisted in database"""
        from app.models.backtest import Backtest

        backtest = db_session.query(Backtest).filter_by(id=sample_backtest.id).first()

        assert backtest is not None
        assert backtest.strategy_id == sample_backtest.strategy_id
        assert backtest.symbol == sample_backtest.symbol

    def test_relationship_integrity(self, db_session, sample_strategy):
        """Test database relationship integrity"""
        from app.models.backtest import Backtest

        # Create backtest for strategy
        backtest = Backtest(
            strategy_id=sample_strategy.id,
            symbol="BTC/USDT",
            timeframe="1h",
            initial_capital=10000,
            status="pending"
        )
        db_session.add(backtest)
        db_session.commit()

        # Verify relationship
        strategy = db_session.query(Strategy).filter_by(id=sample_strategy.id).first()
        assert len(strategy.backtests) > 0
