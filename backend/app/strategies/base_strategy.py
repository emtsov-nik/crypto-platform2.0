from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import pandas as pd
from datetime import datetime


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies

    All strategies must implement:
    - validate_params(): Validate strategy parameters
    - prepare_data(): Add necessary indicators to data
    - generate_signal(): Generate trading signal (long/short/None)
    - calculate_position_size(): Calculate position size
    - calculate_exit_prices(): Calculate take profit and stop loss prices
    """

    def __init__(self, params: Dict[str, Any]):
        """
        Initialize strategy with parameters

        Args:
            params: Strategy parameters dictionary
        """
        self.params = params
        self.name = self.__class__.__name__
        self.validate_params()

    @abstractmethod
    def validate_params(self):
        """
        Validate strategy parameters
        Raise ValueError if parameters are invalid
        """
        pass

    @abstractmethod
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add necessary indicators to the data

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicators
        """
        pass

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """
        Generate trading signal for a specific candle

        Args:
            df: DataFrame with prepared data (OHLCV + indicators)
            index: Index of the current candle

        Returns:
            'long' - >B:@KBL 4;8==CN ?>78F8N
            'short' - >B:@KBL :>@>B:CN ?>78F8N
            None - =5B A83=0;0
        """
        pass

    @abstractmethod
    def calculate_position_size(
        self,
        capital: float,
        price: float,
        step: int
    ) -> float:
        """
        Calculate position size for a given step

        Args:
            capital: Available capital
            price: Current price
            step: Position step number (0 for first entry, 1 for averaging, etc.)

        Returns:
            Position size in base asset
        """
        pass

    @abstractmethod
    def calculate_exit_prices(
        self,
        avg_price: float,
        side: str
    ) -> Tuple[float, float]:
        """
        Calculate take profit and stop loss prices

        Args:
            avg_price: Average entry price
            side: Position side ('long' or 'short')

        Returns:
            Tuple of (take_profit_price, stop_loss_price)
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get strategy metadata

        Returns:
            Dictionary with strategy information
        """
        return {
            "name": self.name,
            "params": self.params,
            "description": self.__doc__ or "No description",
        }

    def should_close_position(
        self,
        df: pd.DataFrame,
        index: int,
        position_side: str,
        avg_price: float
    ) -> Optional[str]:
        """
        Check if position should be closed (optional override)

        Args:
            df: DataFrame with prepared data
            index: Current index
            position_side: Current position side
            avg_price: Average position price

        Returns:
            Reason for closing ('signal', 'custom') or None
        """
        # Default: close on opposite signal
        signal = self.generate_signal(df, index)
        if signal and signal != position_side:
            return 'signal'
        return None

    def should_average_position(
        self,
        df: pd.DataFrame,
        index: int,
        position_side: str,
        avg_price: float,
        current_step: int
    ) -> bool:
        """
        Check if position should be averaged (optional override)

        Args:
            df: DataFrame with prepared data
            index: Current index
            position_side: Current position side
            avg_price: Average position price
            current_step: Current position step

        Returns:
            True if should average, False otherwise
        """
        # Default: no averaging
        return False

    def get_required_indicators(self) -> list[str]:
        """
        Get list of required indicators for this strategy

        Returns:
            List of indicator names
        """
        return []

    def __str__(self) -> str:
        return f"{self.name}({self.params})"

    def __repr__(self) -> str:
        return f"<{self.name} params={self.params}>"
