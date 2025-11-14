import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice
from typing import Dict, Optional


class IndicatorService:
    """Service for calculating technical indicators"""

    @staticmethod
    def add_moving_averages(df: pd.DataFrame, periods: list = [7, 25, 99]) -> pd.DataFrame:
        """
        Add Simple Moving Averages (SMA) to dataframe

        Args:
            df: DataFrame with OHLCV data
            periods: List of periods for SMAs

        Returns:
            DataFrame with SMA columns added
        """
        df = df.copy()

        for period in periods:
            sma = SMAIndicator(close=df['close'], window=period)
            df[f'sma_{period}'] = sma.sma_indicator()

        return df

    @staticmethod
    def add_exponential_moving_averages(df: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """
        Add Exponential Moving Averages (EMA) to dataframe

        Args:
            df: DataFrame with OHLCV data
            periods: List of periods for EMAs

        Returns:
            DataFrame with EMA columns added
        """
        df = df.copy()

        for period in periods:
            ema = EMAIndicator(close=df['close'], window=period)
            df[f'ema_{period}'] = ema.ema_indicator()

        return df

    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Relative Strength Index (RSI) to dataframe

        Args:
            df: DataFrame with OHLCV data
            period: RSI period (default 14)

        Returns:
            DataFrame with RSI column added
        """
        df = df.copy()

        rsi = RSIIndicator(close=df['close'], window=period)
        df['rsi'] = rsi.rsi()

        return df

    @staticmethod
    def add_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """
        Add Bollinger Bands to dataframe

        Args:
            df: DataFrame with OHLCV data
            period: Period for moving average (default 20)
            std_dev: Standard deviation multiplier (default 2.0)

        Returns:
            DataFrame with BB columns added (bb_upper, bb_middle, bb_lower, bb_width)
        """
        df = df.copy()

        bb = BollingerBands(
            close=df['close'],
            window=period,
            window_dev=std_dev
        )

        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        df['bb_pband'] = bb.bollinger_pband()

        return df

    @staticmethod
    def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Volume Weighted Average Price (VWAP) to dataframe

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with VWAP column added
        """
        df = df.copy()

        vwap = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        )

        df['vwap'] = vwap.volume_weighted_average_price()

        return df

    @staticmethod
    def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Average True Range (ATR) to dataframe

        Args:
            df: DataFrame with OHLCV data
            period: ATR period (default 14)

        Returns:
            DataFrame with ATR column added
        """
        df = df.copy()

        # Calculate True Range
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

        # Calculate ATR as SMA of TR
        df['atr'] = df['tr'].rolling(window=period).mean()

        # Clean up temporary columns
        df.drop(['tr1', 'tr2', 'tr3', 'tr'], axis=1, inplace=True)

        return df

    @staticmethod
    def add_macd(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence) to dataframe

        Args:
            df: DataFrame with OHLCV data
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)

        Returns:
            DataFrame with MACD columns added (macd, macd_signal, macd_diff)
        """
        df = df.copy()

        # Calculate fast and slow EMAs
        ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()

        # MACD line
        df['macd'] = ema_fast - ema_slow

        # Signal line
        df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()

        # MACD histogram
        df['macd_diff'] = df['macd'] - df['macd_signal']

        return df

    @staticmethod
    def add_all_indicators(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
        """
        Add all indicators to dataframe

        Args:
            df: DataFrame with OHLCV data
            config: Optional configuration for indicators

        Returns:
            DataFrame with all indicators added
        """
        if config is None:
            config = {}

        df = df.copy()

        # Moving Averages
        sma_periods = config.get('sma_periods', [7, 25, 99])
        df = IndicatorService.add_moving_averages(df, sma_periods)

        ema_periods = config.get('ema_periods', [12, 26])
        df = IndicatorService.add_exponential_moving_averages(df, ema_periods)

        # RSI
        rsi_period = config.get('rsi_period', 14)
        df = IndicatorService.add_rsi(df, rsi_period)

        # Bollinger Bands
        bb_period = config.get('bb_period', 20)
        bb_std = config.get('bb_std', 2.0)
        df = IndicatorService.add_bollinger_bands(df, bb_period, bb_std)

        # MACD
        df = IndicatorService.add_macd(df)

        # ATR
        atr_period = config.get('atr_period', 14)
        df = IndicatorService.add_atr(df, atr_period)

        # VWAP
        df = IndicatorService.add_vwap(df)

        return df

    @staticmethod
    def prepare_data_for_strategy(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data with common indicators for strategy

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with indicators added
        """
        return IndicatorService.add_all_indicators(df)
