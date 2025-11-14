from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

from app.models.strategy import Strategy
from app.schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyTestResponse,
    SignalInfo
)
from app.services.strategy_loader import get_strategy_loader
from app.services.binance_service import BinanceService


class StrategyService:
    """Service for managing trading strategies"""

    def __init__(self, db: Session):
        self.db = db
        self.loader = get_strategy_loader()
        self.binance_service = BinanceService()

    # CRUD Operations

    def create_strategy(self, strategy_data: StrategyCreate) -> Strategy:
        """
        Create a new strategy

        Args:
            strategy_data: Strategy creation data

        Returns:
            Created strategy

        Raises:
            ValueError: If strategy class doesn't exist or validation fails
        """
        # Validate that strategy class exists
        if not self.loader.strategy_exists(strategy_data.class_name):
            raise ValueError(f"Strategy class not found: {strategy_data.class_name}")

        # Validate parameters by trying to instantiate the strategy
        try:
            strategy_instance = self.loader.get_strategy(
                strategy_data.class_name,
                strategy_data.params
            )
            if strategy_instance is None:
                raise ValueError(f"Failed to instantiate strategy: {strategy_data.class_name}")
        except Exception as e:
            raise ValueError(f"Strategy validation failed: {str(e)}")

        # Create database record
        db_strategy = Strategy(
            name=strategy_data.name,
            description=strategy_data.description,
            class_name=strategy_data.class_name,
            params=strategy_data.params,
            is_active=strategy_data.is_active
        )

        self.db.add(db_strategy)
        self.db.commit()
        self.db.refresh(db_strategy)

        return db_strategy

    def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        """Get strategy by ID"""
        return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()

    def get_all_strategies(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Strategy]:
        """
        Get all strategies

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: If True, only return active strategies

        Returns:
            List of strategies
        """
        query = self.db.query(Strategy)

        if active_only:
            query = query.filter(Strategy.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update_strategy(
        self,
        strategy_id: int,
        strategy_data: StrategyUpdate
    ) -> Optional[Strategy]:
        """
        Update strategy

        Args:
            strategy_id: Strategy ID
            strategy_data: Updated strategy data

        Returns:
            Updated strategy or None if not found

        Raises:
            ValueError: If validation fails
        """
        db_strategy = self.get_strategy(strategy_id)
        if not db_strategy:
            return None

        # Validate new parameters if provided
        if strategy_data.params is not None:
            try:
                strategy_instance = self.loader.get_strategy(
                    db_strategy.class_name,
                    strategy_data.params
                )
                if strategy_instance is None:
                    raise ValueError(f"Failed to instantiate strategy with new params")
            except Exception as e:
                raise ValueError(f"Parameter validation failed: {str(e)}")

        # Update fields
        update_data = strategy_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_strategy, field, value)

        db_strategy.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_strategy)

        return db_strategy

    def delete_strategy(self, strategy_id: int) -> bool:
        """
        Delete strategy

        Args:
            strategy_id: Strategy ID

        Returns:
            True if deleted, False if not found
        """
        db_strategy = self.get_strategy(strategy_id)
        if not db_strategy:
            return False

        self.db.delete(db_strategy)
        self.db.commit()

        return True

    def toggle_strategy_active(self, strategy_id: int) -> Optional[Strategy]:
        """
        Toggle strategy active status

        Args:
            strategy_id: Strategy ID

        Returns:
            Updated strategy or None if not found
        """
        db_strategy = self.get_strategy(strategy_id)
        if not db_strategy:
            return None

        db_strategy.is_active = not db_strategy.is_active
        db_strategy.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_strategy)

        return db_strategy

    # Strategy Testing and Validation

    def test_strategy(
        self,
        class_name: str,
        params: Dict[str, Any],
        symbol: str = "BTC/USDT",
        timeframe: str = "1h",
        limit: int = 100
    ) -> StrategyTestResponse:
        """
        Test strategy on historical data

        Args:
            class_name: Strategy class name
            params: Strategy parameters
            symbol: Trading pair
            timeframe: Timeframe
            limit: Number of candles to test

        Returns:
            Test results with generated signals
        """
        try:
            # Load strategy
            strategy = self.loader.get_strategy(class_name, params)
            if strategy is None:
                return StrategyTestResponse(
                    success=False,
                    message=f"Failed to load strategy: {class_name}",
                    signals=[],
                    total_signals=0
                )

            # Fetch historical data
            df = self.binance_service.get_klines(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )

            # Prepare data with indicators
            df = strategy.prepare_data(df)

            # Generate signals
            signals = []
            for i in range(len(df)):
                signal = strategy.generate_signal(df, i)
                if signal:
                    row = df.iloc[i]
                    signals.append(SignalInfo(
                        timestamp=row['timestamp'],
                        signal=signal,
                        price=float(row['close']),
                        indicators={
                            'rsi': float(row.get('rsi', 0)) if pd.notna(row.get('rsi')) else None,
                            'bb_upper': float(row.get('bb_upper', 0)) if pd.notna(row.get('bb_upper')) else None,
                            'bb_middle': float(row.get('bb_middle', 0)) if pd.notna(row.get('bb_middle')) else None,
                            'bb_lower': float(row.get('bb_lower', 0)) if pd.notna(row.get('bb_lower')) else None,
                        }
                    ))

            # Count signal types
            long_signals = sum(1 for s in signals if s.signal == 'long')
            short_signals = sum(1 for s in signals if s.signal == 'short')

            return StrategyTestResponse(
                success=True,
                message=f"Generated {len(signals)} signals from {len(df)} candles",
                signals=signals,
                total_signals=len(signals),
                long_signals=long_signals,
                short_signals=short_signals
            )

        except Exception as e:
            return StrategyTestResponse(
                success=False,
                message=f"Error testing strategy: {str(e)}",
                signals=[],
                total_signals=0
            )

    def validate_strategy_params(
        self,
        class_name: str,
        params: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate strategy parameters

        Args:
            class_name: Strategy class name
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            strategy = self.loader.get_strategy(class_name, params)
            if strategy is None:
                return False, [f"Failed to instantiate strategy: {class_name}"]
            return True, []
        except ValueError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected error: {str(e)}"]

    def generate_signal(
        self,
        strategy_id: int,
        symbol: str = "BTC/USDT",
        timeframe: str = "1h"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate signal for current market conditions using saved strategy

        Args:
            strategy_id: Database strategy ID
            symbol: Trading pair
            timeframe: Timeframe

        Returns:
            Signal information or None if error
        """
        try:
            # Get strategy from database
            db_strategy = self.get_strategy(strategy_id)
            if not db_strategy or not db_strategy.is_active:
                return None

            # Load strategy instance
            strategy = self.loader.get_strategy(
                db_strategy.class_name,
                db_strategy.params
            )
            if strategy is None:
                return None

            # Fetch recent data
            df = self.binance_service.get_klines(
                symbol=symbol,
                timeframe=timeframe,
                limit=100  # Get enough data for indicators
            )

            # Prepare data
            df = strategy.prepare_data(df)

            # Generate signal for latest candle
            latest_index = len(df) - 1
            signal = strategy.generate_signal(df, latest_index)

            latest_row = df.iloc[latest_index]

            return {
                'strategy_id': strategy_id,
                'strategy_name': db_strategy.name,
                'symbol': symbol,
                'timeframe': timeframe,
                'signal': signal,
                'timestamp': latest_row['timestamp'],
                'current_price': float(latest_row['close']),
                'indicators': {
                    'rsi': float(latest_row.get('rsi', 0)) if pd.notna(latest_row.get('rsi')) else None,
                    'bb_upper': float(latest_row.get('bb_upper', 0)) if pd.notna(latest_row.get('bb_upper')) else None,
                    'bb_middle': float(latest_row.get('bb_middle', 0)) if pd.notna(latest_row.get('bb_middle')) else None,
                    'bb_lower': float(latest_row.get('bb_lower', 0)) if pd.notna(latest_row.get('bb_lower')) else None,
                },
                'message': f"Signal: {signal if signal else 'No signal'}"
            }

        except Exception as e:
            print(f"Error generating signal: {e}")
            return None

    def get_strategy_info_from_loader(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get strategy information from loader (available strategy classes)"""
        return self.loader.get_strategy_info(class_name)

    def list_available_strategies(self) -> List[Dict[str, Any]]:
        """List all available strategy classes from loader"""
        return self.loader.list_strategies()
