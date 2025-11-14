from celery import Task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.backtest_service import BacktestService


class BacktestTask(Task):
    """Custom Celery task for backtesting"""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db


@celery_app.task(bind=True, base=BacktestTask, name='run_backtest')
def run_backtest_task(self, backtest_id: int):
    """
    Celery task to run a backtest asynchronously

    Args:
        backtest_id: ID of the backtest to run

    Returns:
        Backtest results
    """
    service = BacktestService(self.db)

    def progress_callback(progress: int, message: str):
        """Update task progress"""
        self.update_state(
            state='PROGRESS',
            meta={
                'current': progress,
                'total': 100,
                'status': message
            }
        )

    try:
        results = service.run_backtest(
            backtest_id=backtest_id,
            progress_callback=progress_callback
        )

        return {
            'status': 'completed',
            'backtest_id': backtest_id,
            'results': results
        }

    except Exception as e:
        # Update backtest status to failed
        backtest = service.get_backtest(backtest_id)
        if backtest:
            backtest.status = 'failed'
            backtest.results = {'error': str(e)}
            self.db.commit()

        raise

    finally:
        self.db.close()


@celery_app.task(name='cleanup_old_backtests')
def cleanup_old_backtests():
    """
    Celery periodic task to clean up old backtests

    This task should be scheduled to run periodically (e.g., daily)
    to remove old backtest results and free up space.
    """
    from datetime import datetime, timedelta
    from app.models.backtest import Backtest

    db = SessionLocal()
    try:
        # Delete backtests older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        old_backtests = db.query(Backtest).filter(
            Backtest.created_at < cutoff_date
        ).all()

        count = len(old_backtests)

        for backtest in old_backtests:
            db.delete(backtest)

        db.commit()

        return {
            'status': 'completed',
            'deleted_count': count,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as e:
        db.rollback()
        raise

    finally:
        db.close()
