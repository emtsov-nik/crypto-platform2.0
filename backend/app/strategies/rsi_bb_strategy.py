import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from app.strategies.base_strategy import BaseStrategy


class RSIBBStrategy(BaseStrategy):
    """
    RSI + Bollinger Bands Strategy

    Entry signals:
    - LONG: RSI < oversold_threshold AND price touches/crosses below BB lower band
    - SHORT: RSI > overbought_threshold AND price touches/crosses above BB upper band

    Exit signals:
    - Take Profit: Based on BB width and risk-reward ratio
    - Stop Loss: Based on ATR and risk percentage

    Averaging:
    - Allows position averaging on favorable price movements
    - Max 3 steps (initial + 2 averages)
    """

    def __init__(self, params: Dict[str, Any]):
        """
        Initialize RSI+BB Strategy

        Default params:
        {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'bb_period': 20,
            'bb_std': 2.0,
            'atr_period': 14,
            'risk_percent': 1.0,  # Risk per trade as % of capital
            'risk_reward_ratio': 2.0,  # TP/SL ratio
            'max_steps': 3,  # Max averaging steps
            'step_distance_percent': 2.0,  # Distance for averaging (% from avg price)
        }
        """
        super().__init__(params)

    def validate_params(self):
        """Validate strategy parameters"""
        required_params = [
            'rsi_period', 'rsi_overbought', 'rsi_oversold',
            'bb_period', 'bb_std', 'atr_period',
            'risk_percent', 'risk_reward_ratio', 'max_steps',
            'step_distance_percent'
        ]

        for param in required_params:
            if param not in self.params:
                raise ValueError(f"Missing required parameter: {param}")

        # Validate ranges
        if not (0 < self.params['rsi_oversold'] < 50):
            raise ValueError("rsi_oversold must be between 0 and 50")

        if not (50 < self.params['rsi_overbought'] < 100):
            raise ValueError("rsi_overbought must be between 50 and 100")

        if self.params['risk_percent'] <= 0 or self.params['risk_percent'] > 10:
            raise ValueError("risk_percent must be between 0 and 10")

        if self.params['risk_reward_ratio'] <= 0:
            raise ValueError("risk_reward_ratio must be positive")

        if self.params['max_steps'] < 1 or self.params['max_steps'] > 5:
            raise ValueError("max_steps must be between 1 and 5")

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add required indicators to dataframe

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with indicators added
        """
        from app.services.indicators import IndicatorService

        df = df.copy()

        # Add RSI
        df = IndicatorService.add_rsi(df, period=self.params['rsi_period'])

        # Add Bollinger Bands
        df = IndicatorService.add_bollinger_bands(
            df,
            period=self.params['bb_period'],
            std_dev=self.params['bb_std']
        )

        # Add ATR for stop loss calculation
        df = IndicatorService.add_atr(df, period=self.params['atr_period'])

        return df

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """
        Generate trading signal

        Args:
            df: DataFrame with OHLCV and indicators
            index: Current candle index

        Returns:
            'long', 'short', or None
        """
        if index < 1:
            return None

        current = df.iloc[index]
        previous = df.iloc[index - 1]

        # Check for NaN values
        if pd.isna(current['rsi']) or pd.isna(current['bb_lower']) or pd.isna(current['bb_upper']):
            return None

        rsi = current['rsi']
        close = current['close']
        bb_lower = current['bb_lower']
        bb_upper = current['bb_upper']

        # Previous values
        prev_close = previous['close']

        # LONG signal: RSI oversold AND price at/below BB lower band
        if (rsi < self.params['rsi_oversold'] and
            close <= bb_lower and
            prev_close > previous['bb_lower']):
            return 'long'

        # SHORT signal: RSI overbought AND price at/above BB upper band
        if (rsi > self.params['rsi_overbought'] and
            close >= bb_upper and
            prev_close < previous['bb_upper']):
            return 'short'

        return None

    def calculate_position_size(
        self,
        capital: float,
        price: float,
        step: int = 0
    ) -> float:
        """
        Calculate position size based on risk management

        Args:
            capital: Available capital in USDT
            price: Entry price
            step: Current averaging step (0 = initial position)

        Returns:
            Position size in base currency
        """
        # Risk amount per trade
        risk_amount = capital * (self.params['risk_percent'] / 100)

        # For averaging, use smaller position sizes
        if step == 0:
            # Initial position: use full risk amount
            position_multiplier = 1.0
        elif step == 1:
            # First average: 50% of initial
            position_multiplier = 0.5
        else:
            # Second average: 25% of initial
            position_multiplier = 0.25

        adjusted_risk = risk_amount * position_multiplier

        # Simple position sizing: risk_amount / (price * stop_loss_percent)
        # Assume 2% stop loss for sizing calculation
        stop_loss_percent = 0.02
        position_size = adjusted_risk / (price * stop_loss_percent)

        return position_size

    def calculate_exit_prices(
        self,
        avg_price: float,
        side: str
    ) -> Tuple[float, float]:
        """
        Calculate take profit and stop loss prices

        Args:
            avg_price: Average entry price
            side: 'long' or 'short'

        Returns:
            Tuple of (take_profit, stop_loss)
        """
        # Calculate stop loss distance based on risk_percent
        # For simplicity, use fixed percentage
        sl_distance_percent = self.params['risk_percent']  # 1% default

        # Calculate TP based on risk-reward ratio
        tp_distance_percent = sl_distance_percent * self.params['risk_reward_ratio']

        if side == 'long':
            stop_loss = avg_price * (1 - sl_distance_percent / 100)
            take_profit = avg_price * (1 + tp_distance_percent / 100)
        else:  # short
            stop_loss = avg_price * (1 + sl_distance_percent / 100)
            take_profit = avg_price * (1 - tp_distance_percent / 100)

        return take_profit, stop_loss

    def should_close_position(
        self,
        df: pd.DataFrame,
        index: int,
        position_side: str,
        avg_price: float
    ) -> Optional[str]:
        """
        Check if position should be closed based on strategy logic

        Args:
            df: DataFrame with OHLCV and indicators
            index: Current candle index
            position_side: 'long' or 'short'
            avg_price: Average position price

        Returns:
            Reason string if should close, None otherwise
        """
        current = df.iloc[index]

        # Check for NaN values
        if pd.isna(current['rsi']) or pd.isna(current['bb_middle']):
            return None

        rsi = current['rsi']
        close = current['close']
        bb_middle = current['bb_middle']

        # For LONG positions
        if position_side == 'long':
            # Close if RSI becomes overbought
            if rsi > self.params['rsi_overbought']:
                return 'rsi_overbought'

            # Close if price crosses above BB middle (take partial profit zone)
            if close > bb_middle and avg_price < bb_middle:
                return 'bb_middle_cross'

        # For SHORT positions
        elif position_side == 'short':
            # Close if RSI becomes oversold
            if rsi < self.params['rsi_oversold']:
                return 'rsi_oversold'

            # Close if price crosses below BB middle
            if close < bb_middle and avg_price > bb_middle:
                return 'bb_middle_cross'

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
        Check if we should add to the position (averaging)

        Args:
            df: DataFrame with OHLCV and indicators
            index: Current candle index
            position_side: 'long' or 'short'
            avg_price: Current average price
            current_step: Current averaging step

        Returns:
            True if should average, False otherwise
        """
        # Check if we haven't exceeded max steps
        if current_step >= self.params['max_steps'] - 1:
            return False

        current = df.iloc[index]
        close = current['close']

        # Calculate distance from average price
        step_distance = self.params['step_distance_percent'] / 100

        # For LONG positions: average if price drops below threshold
        if position_side == 'long':
            threshold_price = avg_price * (1 - step_distance)
            if close <= threshold_price:
                # Also check RSI is still oversold
                if not pd.isna(current['rsi']) and current['rsi'] < self.params['rsi_oversold']:
                    return True

        # For SHORT positions: average if price rises above threshold
        elif position_side == 'short':
            threshold_price = avg_price * (1 + step_distance)
            if close >= threshold_price:
                # Also check RSI is still overbought
                if not pd.isna(current['rsi']) and current['rsi'] > self.params['rsi_overbought']:
                    return True

        return False

    def get_required_indicators(self) -> list[str]:
        """
        Get list of required indicators for this strategy

        Returns:
            List of indicator names
        """
        return ['rsi', 'bollinger_bands', 'atr']

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get strategy metadata

        Returns:
            Dictionary with strategy information
        """
        metadata = super().get_metadata()
        metadata.update({
            'description': 'RSI + Bollinger Bands mean reversion strategy',
            'indicators': self.get_required_indicators(),
            'timeframes': ['1h', '4h', '1d'],  # Recommended timeframes
            'risk_level': 'medium',
            'strategy_type': 'mean_reversion',
            'author': 'System',
            'version': '1.0.0'
        })
        return metadata
