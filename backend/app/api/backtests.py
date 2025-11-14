from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services.backtest_service import BacktestService
from app.schemas.backtest import (
    BacktestCreate,
    BacktestResponse,
    BacktestListResponse,
    TradeListResponse,
    TradeInfo,
    BacktestResults,
    BacktestProgress,
    BacktestComparisonResponse,
    EquityCurveResponse,
    RunBacktestRequest,
    RunBacktestResponse
)
from app.tasks.backtest_tasks import run_backtest_task

router = APIRouter()


def get_backtest_service(db: Session = Depends(get_db)) -> BacktestService:
    """Dependency to get backtest service"""
    return BacktestService(db)


# Backtest CRUD Operations

@router.post("/", response_model=BacktestResponse, status_code=status.HTTP_201_CREATED)
async def create_backtest(
    backtest_data: BacktestCreate,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Create a new backtest configuration

    This only creates a backtest record. Use POST /run to actually run it.
    """
    try:
        db_backtest = service.create_backtest(backtest_data)
        return db_backtest
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating backtest: {str(e)}"
        )


@router.post("/run", response_model=RunBacktestResponse)
async def run_backtest(
    request: RunBacktestRequest,
    background_tasks: BackgroundTasks,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Create and run a backtest asynchronously

    This endpoint creates a backtest and queues it for execution.
    Use GET /{backtest_id}/progress to check progress.
    """
    try:
        # Create backtest
        backtest_create = BacktestCreate(
            strategy_id=request.strategy_id,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            params={
                'fee_rate': request.fee_rate,
                'slippage': request.slippage
            }
        )

        db_backtest = service.create_backtest(backtest_create)

        # Queue backtest for execution using Celery
        task = run_backtest_task.delay(db_backtest.id)

        return RunBacktestResponse(
            backtest_id=db_backtest.id,
            status='pending',
            message='Backtest queued for execution',
            task_id=task.id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting backtest: {str(e)}"
        )


@router.get("/", response_model=BacktestListResponse)
async def list_backtests(
    skip: int = 0,
    limit: int = 100,
    strategy_id: Optional[int] = None,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Get list of all backtests

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        strategy_id: Filter by strategy ID (optional)
    """
    try:
        backtests = service.get_all_backtests(
            skip=skip,
            limit=limit,
            strategy_id=strategy_id
        )
        return BacktestListResponse(
            backtests=backtests,
            total=len(backtests)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing backtests: {str(e)}"
        )


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: int,
    service: BacktestService = Depends(get_backtest_service)
):
    """Get a specific backtest by ID"""
    backtest = service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest not found: {backtest_id}"
        )
    return backtest


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(
    backtest_id: int,
    service: BacktestService = Depends(get_backtest_service)
):
    """Delete a backtest"""
    success = service.delete_backtest(backtest_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest not found: {backtest_id}"
        )
    return None


# Backtest Results

@router.get("/{backtest_id}/results", response_model=BacktestResults)
async def get_backtest_results(
    backtest_id: int,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Get complete backtest results including metrics, trades, and equity curve

    The backtest must be in 'completed' status.
    """
    backtest = service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest not found: {backtest_id}"
        )

    if backtest.status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Backtest is not completed yet. Current status: {backtest.status}"
        )

    results = service.get_backtest_results(backtest_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Results not found for backtest: {backtest_id}"
        )

    return BacktestResults(**results)


@router.get("/{backtest_id}/trades", response_model=TradeListResponse)
async def get_backtest_trades(
    backtest_id: int,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Get list of all trades from a backtest

    Returns detailed information about each trade including entry/exit prices, PnL, etc.
    """
    trades = service.get_backtest_trades(backtest_id)
    if trades is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest not found or has no results: {backtest_id}"
        )

    return TradeListResponse(
        trades=[TradeInfo(**trade) for trade in trades],
        total=len(trades)
    )


@router.get("/{backtest_id}/equity", response_model=EquityCurveResponse)
async def get_backtest_equity_curve(
    backtest_id: int,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Get equity curve from a backtest

    Returns timestamps and corresponding equity values for plotting.
    """
    equity_data = service.get_backtest_equity_curve(backtest_id)
    if equity_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest not found or has no results: {backtest_id}"
        )

    return EquityCurveResponse(**equity_data)


@router.get("/{backtest_id}/progress", response_model=BacktestProgress)
async def get_backtest_progress(
    backtest_id: int,
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Get backtest execution progress

    Returns current status and progress percentage.
    """
    backtest = service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest not found: {backtest_id}"
        )

    # Map status to progress
    progress_map = {
        'pending': (0, 'Waiting to start'),
        'running': (50, 'Running backtest...'),
        'completed': (100, 'Completed'),
        'failed': (0, 'Failed')
    }

    current, message = progress_map.get(backtest.status, (0, 'Unknown'))

    return BacktestProgress(
        backtest_id=backtest_id,
        status=backtest.status,
        current=current,
        total=100,
        message=message
    )


# Comparison

@router.post("/compare", response_model=BacktestComparisonResponse)
async def compare_backtests(
    backtest_ids: List[int],
    service: BacktestService = Depends(get_backtest_service)
):
    """
    Compare multiple backtests side-by-side

    Provide a list of backtest IDs to compare their performance metrics.
    """
    if len(backtest_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 backtests are required for comparison"
        )

    if len(backtest_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 backtests can be compared at once"
        )

    try:
        comparison = service.compare_backtests(backtest_ids)

        if 'error' in comparison:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=comparison['error']
            )

        return BacktestComparisonResponse(**comparison)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing backtests: {str(e)}"
        )
