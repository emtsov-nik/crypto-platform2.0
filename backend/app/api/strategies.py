from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.strategy_service import StrategyService
from app.services.strategy_loader import get_strategy_loader
from app.schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyListResponse,
    AvailableStrategiesResponse,
    AvailableStrategyInfo,
    StrategyMetadata,
    StrategyTestRequest,
    StrategyTestResponse,
    StrategyValidationRequest,
    StrategyValidationResponse,
    GenerateSignalRequest,
    GenerateSignalResponse
)

router = APIRouter()


def get_strategy_service(db: Session = Depends(get_db)) -> StrategyService:
    """Dependency to get strategy service"""
    return StrategyService(db)


# Available Strategy Classes (from code)

@router.get("/available", response_model=AvailableStrategiesResponse)
async def list_available_strategies():
    """
    Get list of all available strategy classes that can be instantiated

    This endpoint returns strategy classes available in the codebase,
    not the user-created strategy configurations.
    """
    try:
        loader = get_strategy_loader()
        strategies = loader.list_strategies()

        # Convert to response format
        strategy_infos = []
        for strategy in strategies:
            strategy_infos.append(AvailableStrategyInfo(
                name=strategy['name'],
                class_name=strategy['class_name'],
                metadata=StrategyMetadata(**strategy['metadata']),
                default_params=strategy['default_params'],
                doc=strategy['doc']
            ))

        return AvailableStrategiesResponse(
            strategies=strategy_infos,
            total=len(strategy_infos)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading available strategies: {str(e)}"
        )


@router.get("/available/{class_name}")
async def get_available_strategy_info(class_name: str):
    """Get detailed information about a specific strategy class"""
    try:
        loader = get_strategy_loader()
        info = loader.get_strategy_info(class_name)

        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy class not found: {class_name}"
            )

        return AvailableStrategyInfo(
            name=info['name'],
            class_name=info['class_name'],
            metadata=StrategyMetadata(**info['metadata']),
            default_params=info['default_params'],
            doc=info['doc']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting strategy info: {str(e)}"
        )


# Strategy CRUD Operations (user-created strategies)

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Create a new strategy configuration

    This creates a new strategy instance with specific parameters
    that can be used for backtesting or live trading.
    """
    try:
        db_strategy = service.create_strategy(strategy_data)
        return db_strategy
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating strategy: {str(e)}"
        )


@router.get("/", response_model=StrategyListResponse)
async def list_strategies(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Get list of all user-created strategy configurations

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        active_only: If true, only return active strategies
    """
    try:
        strategies = service.get_all_strategies(
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        return StrategyListResponse(
            strategies=strategies,
            total=len(strategies)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing strategies: {str(e)}"
        )


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    service: StrategyService = Depends(get_strategy_service)
):
    """Get a specific strategy configuration by ID"""
    strategy = service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy not found: {strategy_id}"
        )
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    service: StrategyService = Depends(get_strategy_service)
):
    """Update a strategy configuration"""
    try:
        updated_strategy = service.update_strategy(strategy_id, strategy_data)
        if not updated_strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy not found: {strategy_id}"
            )
        return updated_strategy
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating strategy: {str(e)}"
        )


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: int,
    service: StrategyService = Depends(get_strategy_service)
):
    """Delete a strategy configuration"""
    success = service.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy not found: {strategy_id}"
        )
    return None


@router.post("/{strategy_id}/toggle", response_model=StrategyResponse)
async def toggle_strategy_active(
    strategy_id: int,
    service: StrategyService = Depends(get_strategy_service)
):
    """Toggle strategy active/inactive status"""
    strategy = service.toggle_strategy_active(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy not found: {strategy_id}"
        )
    return strategy


# Strategy Testing and Validation

@router.post("/test", response_model=StrategyTestResponse)
async def test_strategy(
    test_request: StrategyTestRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Test a strategy configuration on historical data

    This endpoint allows testing strategy parameters before saving them.
    It returns all signals generated by the strategy on historical data.
    """
    try:
        result = service.test_strategy(
            class_name=test_request.class_name,
            params=test_request.params,
            symbol=test_request.symbol,
            timeframe=test_request.timeframe,
            limit=test_request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing strategy: {str(e)}"
        )


@router.post("/validate", response_model=StrategyValidationResponse)
async def validate_strategy_params(
    validation_request: StrategyValidationRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Validate strategy parameters without running a full test

    This is useful for quick validation in the UI before saving or testing.
    """
    try:
        is_valid, errors = service.validate_strategy_params(
            validation_request.class_name,
            validation_request.params
        )
        return StrategyValidationResponse(
            valid=is_valid,
            errors=errors
        )
    except Exception as e:
        return StrategyValidationResponse(
            valid=False,
            errors=[f"Validation error: {str(e)}"]
        )


# Signal Generation

@router.post("/signal", response_model=GenerateSignalResponse)
async def generate_signal(
    signal_request: GenerateSignalRequest,
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Generate trading signal for current market conditions

    Uses a saved strategy configuration to generate a signal based on
    the latest market data.
    """
    try:
        result = service.generate_signal(
            strategy_id=signal_request.strategy_id,
            symbol=signal_request.symbol,
            timeframe=signal_request.timeframe
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy not found or inactive: {signal_request.strategy_id}"
            )

        return GenerateSignalResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating signal: {str(e)}"
        )
