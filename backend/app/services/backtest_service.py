from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.backtest import Backtest
from app.schemas.backtest import BacktestCreate, BacktestUpdate
from app.services.strategy_loader import get_strategy_loader
from app.services.binance_service import BinanceService
from app.backtesting.backtest_engine import BacktestEngine


class BacktestService:
    """Service for managing backtests"""

    def __init__(self, db: Session):
        self.db = db
        self.strategy_loader = get_strategy_loader()
        self.binance_service = BinanceService()

    def create_backtest(
        self,
        backtest_data: BacktestCreate,
        user_id: Optional[int] = None
    ) -> Backtest:
        """
        Create a new backtest record

        Args:
            backtest_data: Backtest creation data
            user_id: Optional user ID

        Returns:
            Created backtest record
        """
        db_backtest = Backtest(
            strategy_id=backtest_data.strategy_id,
            symbol=backtest_data.symbol,
            timeframe=backtest_data.timeframe,
            start_date=backtest_data.start_date,
            end_date=backtest_data.end_date,
            initial_capital=backtest_data.initial_capital,
            params=backtest_data.params,
            status='pending'
        )

        self.db.add(db_backtest)
        self.db.commit()
        self.db.refresh(db_backtest)

        return db_backtest

    def get_backtest(self, backtest_id: int) -> Optional[Backtest]:
        """Get backtest by ID"""
        return self.db.query(Backtest).filter(Backtest.id == backtest_id).first()

    def get_all_backtests(
        self,
        skip: int = 0,
        limit: int = 100,
        strategy_id: Optional[int] = None
    ) -> List[Backtest]:
        """
        Get all backtests

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            strategy_id: Filter by strategy ID

        Returns:
            List of backtests
        """
        query = self.db.query(Backtest)

        if strategy_id is not None:
            query = query.filter(Backtest.strategy_id == strategy_id)

        return query.order_by(Backtest.created_at.desc()).offset(skip).limit(limit).all()

    def update_backtest(
        self,
        backtest_id: int,
        backtest_data: BacktestUpdate
    ) -> Optional[Backtest]:
        """
        Update backtest

        Args:
            backtest_id: Backtest ID
            backtest_data: Updated backtest data

        Returns:
            Updated backtest or None if not found
        """
        db_backtest = self.get_backtest(backtest_id)
        if not db_backtest:
            return None

        update_data = backtest_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_backtest, field, value)

        db_backtest.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_backtest)

        return db_backtest

    def delete_backtest(self, backtest_id: int) -> bool:
        """
        Delete backtest

        Args:
            backtest_id: Backtest ID

        Returns:
            True if deleted, False if not found
        """
        db_backtest = self.get_backtest(backtest_id)
        if not db_backtest:
            return False

        self.db.delete(db_backtest)
        self.db.commit()

        return True

    def run_backtest(
        self,
        backtest_id: int,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Run a backtest

        Args:
            backtest_id: Backtest ID
            progress_callback: Optional callback for progress updates

        Returns:
            Backtest results

        Raises:
            ValueError: If backtest not found or invalid
        """
        # Get backtest from DB
        db_backtest = self.get_backtest(backtest_id)
        if not db_backtest:
            raise ValueError(f"Backtest not found: {backtest_id}")

        # Update status
        db_backtest.status = 'running'
        self.db.commit()

        try:
            # Get strategy
            from app.models.strategy import Strategy
            strategy_model = self.db.query(Strategy).filter(
                Strategy.id == db_backtest.strategy_id
            ).first()

            if not strategy_model:
                raise ValueError(f"Strategy not found: {db_backtest.strategy_id}")

            # Load strategy instance
            strategy = self.strategy_loader.get_strategy(
                strategy_model.class_name,
                strategy_model.params
            )

            if not strategy:
                raise ValueError(f"Failed to load strategy: {strategy_model.class_name}")

            # Fetch historical data
            if progress_callback:
                progress_callback(10, "Fetching historical data...")

            df = self.binance_service.get_klines(
                symbol=db_backtest.symbol,
                timeframe=db_backtest.timeframe,
                limit=5000,  # Maximum allowed
                start_time=db_backtest.start_date.isoformat() if db_backtest.start_date else None,
                end_time=db_backtest.end_date.isoformat() if db_backtest.end_date else None
            )

            if df.empty:
                raise ValueError("No historical data available for the specified period")

            if progress_callback:
                progress_callback(30, "Data fetched, starting backtest...")

            # Create backtest engine
            engine = BacktestEngine(
                strategy=strategy,
                initial_capital=db_backtest.initial_capital,
                fee_rate=db_backtest.params.get('fee_rate', 0.001),
                slippage=db_backtest.params.get('slippage', 0.0005)
            )

            # Run backtest
            results = engine.run(df, symbol=db_backtest.symbol)

            if progress_callback:
                progress_callback(90, "Backtest complete, saving results...")

            # Update backtest with results
            db_backtest.status = 'completed'
            db_backtest.final_capital = results['final_capital']
            db_backtest.total_pnl = results['total_pnl']
            db_backtest.total_pnl_percent = results['total_pnl_percent']
            db_backtest.total_trades = results['total_trades']
            db_backtest.winning_trades = results['winning_trades']
            db_backtest.losing_trades = results['losing_trades']
            db_backtest.win_rate = results['win_rate']
            db_backtest.profit_factor = results['profit_factor']
            db_backtest.max_drawdown = results['max_drawdown']
            db_backtest.max_drawdown_percent = results['max_drawdown_percent']
            db_backtest.sharpe_ratio = results['sharpe_ratio']
            db_backtest.results = results  # Store full results as JSON
            db_backtest.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(db_backtest)

            if progress_callback:
                progress_callback(100, "Done!")

            return results

        except Exception as e:
            # Mark as failed
            db_backtest.status = 'failed'
            db_backtest.results = {'error': str(e)}
            self.db.commit()
            raise

    def get_backtest_results(self, backtest_id: int) -> Optional[Dict[str, Any]]:
        """
        Get backtest results

        Args:
            backtest_id: Backtest ID

        Returns:
            Backtest results or None if not found
        """
        db_backtest = self.get_backtest(backtest_id)
        if not db_backtest:
            return None

        return db_backtest.results

    def get_backtest_trades(self, backtest_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of trades from backtest

        Args:
            backtest_id: Backtest ID

        Returns:
            List of trades or None if not found
        """
        db_backtest = self.get_backtest(backtest_id)
        if not db_backtest or not db_backtest.results:
            return None

        return db_backtest.results.get('trades', [])

    def get_backtest_equity_curve(
        self,
        backtest_id: int
    ) -> Optional[Dict[str, List]]:
        """
        Get equity curve from backtest

        Args:
            backtest_id: Backtest ID

        Returns:
            Dictionary with timestamps and equity values
        """
        db_backtest = self.get_backtest(backtest_id)
        if not db_backtest or not db_backtest.results:
            return None

        return {
            'timestamps': db_backtest.results.get('timestamps', []),
            'equity': db_backtest.results.get('equity_curve', [])
        }

    def compare_backtests(
        self,
        backtest_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Compare multiple backtests

        Args:
            backtest_ids: List of backtest IDs to compare

        Returns:
            Comparison results
        """
        backtests = []
        for backtest_id in backtest_ids:
            bt = self.get_backtest(backtest_id)
            if bt and bt.status == 'completed':
                backtests.append(bt)

        if not backtests:
            return {'error': 'No completed backtests found'}

        comparison = {
            'backtests': [],
            'metrics': [
                'total_pnl_percent',
                'win_rate',
                'profit_factor',
                'max_drawdown_percent',
                'sharpe_ratio',
                'total_trades'
            ]
        }

        for bt in backtests:
            comparison['backtests'].append({
                'id': bt.id,
                'strategy_id': bt.strategy_id,
                'symbol': bt.symbol,
                'timeframe': bt.timeframe,
                'total_pnl_percent': bt.total_pnl_percent,
                'win_rate': bt.win_rate,
                'profit_factor': bt.profit_factor,
                'max_drawdown_percent': bt.max_drawdown_percent,
                'sharpe_ratio': bt.sharpe_ratio,
                'total_trades': bt.total_trades
            })

        return comparison
