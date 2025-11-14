import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from app.strategies.base_strategy import BaseStrategy


class OrderSide(Enum):
    """Order side enum"""
    LONG = "long"
    SHORT = "short"


class OrderStatus(Enum):
    """Order status enum"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass
class Trade:
    """Represents a completed trade"""
    id: int
    entry_time: datetime
    exit_time: datetime
    side: str  # 'long' or 'short'
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    fees: float
    exit_reason: str  # 'take_profit', 'stop_loss', 'strategy_signal'
    steps: int = 1  # Number of averaging steps

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'entry_time': self.entry_time.isoformat() if isinstance(self.entry_time, datetime) else self.entry_time,
            'exit_time': self.exit_time.isoformat() if isinstance(self.exit_time, datetime) else self.exit_time,
            'side': self.side,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'fees': self.fees,
            'exit_reason': self.exit_reason,
            'steps': self.steps
        }


@dataclass
class Position:
    """Represents an open position"""
    side: str  # 'long' or 'short'
    entry_time: datetime
    entry_price: float
    quantity: float
    take_profit: float
    stop_loss: float
    current_step: int = 0
    total_cost: float = 0.0
    total_quantity: float = 0.0

    def get_avg_price(self) -> float:
        """Get average entry price"""
        if self.total_quantity > 0:
            return self.total_cost / self.total_quantity
        return self.entry_price

    def add_to_position(self, price: float, quantity: float):
        """Add to position (averaging)"""
        self.total_cost += price * quantity
        self.total_quantity += quantity
        self.current_step += 1


class BacktestEngine:
    """
    Backtesting engine with event-driven architecture

    Features:
    - Event-driven simulation
    - Position averaging (martingale-style)
    - Stop loss and take profit
    - Fees and slippage
    - Detailed trade tracking
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 10000.0,
        fee_rate: float = 0.001,  # 0.1% fee
        slippage: float = 0.0005,  # 0.05% slippage
    ):
        """
        Initialize backtest engine

        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital in quote currency (USDT)
            fee_rate: Trading fee rate (0.001 = 0.1%)
            slippage: Slippage rate (0.0005 = 0.05%)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.slippage = slippage

        # State
        self.capital = initial_capital
        self.position: Optional[Position] = None
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[datetime] = []

        # Statistics
        self.trade_counter = 0
        self.peak_equity = initial_capital

    def run(
        self,
        df: pd.DataFrame,
        symbol: str = "BTC/USDT"
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data

        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol

        Returns:
            Dictionary with backtest results
        """
        # Prepare data with indicators
        df = self.strategy.prepare_data(df.copy())

        # Reset state
        self.capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.timestamps = []
        self.trade_counter = 0
        self.peak_equity = self.initial_capital

        # Event loop - iterate through each candle
        for i in range(len(df)):
            row = df.iloc[i]
            timestamp = row['timestamp']

            # Check if current position should be closed
            if self.position:
                self._check_position_exit(row, i, df)

            # Generate new signal if no position
            if not self.position:
                signal = self.strategy.generate_signal(df, i)
                if signal:
                    self._open_position(row, signal)

            # Check for position averaging
            elif self.position:
                should_average = self.strategy.should_average_position(
                    df, i, self.position.side,
                    self.position.get_avg_price(),
                    self.position.current_step
                )
                if should_average:
                    self._average_position(row)

            # Record equity
            current_equity = self._calculate_equity(row)
            self.equity_curve.append(current_equity)
            self.timestamps.append(timestamp)

            # Update peak equity for drawdown calculation
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity

        # Close any remaining position
        if self.position:
            last_row = df.iloc[-1]
            self._close_position(last_row, 'backtest_end')

        # Calculate final metrics
        results = self._calculate_metrics(symbol)

        return results

    def _open_position(self, row: pd.Series, side: str):
        """Open a new position"""
        price = self._get_execution_price(row['close'], side, is_entry=True)

        # Calculate position size
        quantity = self.strategy.calculate_position_size(
            self.capital, price, step=0
        )

        # Calculate TP and SL
        tp, sl = self.strategy.calculate_exit_prices(price, side)

        # Calculate cost including fees
        cost = quantity * price
        fees = cost * self.fee_rate
        total_cost = cost + fees

        # Check if we have enough capital
        if total_cost > self.capital:
            return  # Not enough capital

        # Deduct cost from capital
        self.capital -= total_cost

        # Create position
        self.position = Position(
            side=side,
            entry_time=row['timestamp'],
            entry_price=price,
            quantity=quantity,
            take_profit=tp,
            stop_loss=sl,
            current_step=0,
            total_cost=cost,
            total_quantity=quantity
        )

    def _average_position(self, row: pd.Series):
        """Add to existing position (averaging)"""
        if not self.position:
            return

        price = self._get_execution_price(row['close'], self.position.side, is_entry=True)

        # Calculate additional quantity
        quantity = self.strategy.calculate_position_size(
            self.capital, price, step=self.position.current_step + 1
        )

        # Calculate cost including fees
        cost = quantity * price
        fees = cost * self.fee_rate
        total_cost = cost + fees

        # Check if we have enough capital
        if total_cost > self.capital:
            return

        # Deduct cost from capital
        self.capital -= total_cost

        # Add to position
        self.position.add_to_position(price, quantity)

        # Recalculate TP/SL based on new average price
        avg_price = self.position.get_avg_price()
        tp, sl = self.strategy.calculate_exit_prices(avg_price, self.position.side)
        self.position.take_profit = tp
        self.position.stop_loss = sl

    def _check_position_exit(self, row: pd.Series, index: int, df: pd.DataFrame):
        """Check if position should be closed"""
        if not self.position:
            return

        close_price = row['close']
        high_price = row['high']
        low_price = row['low']

        exit_reason = None
        exit_price = None

        # Check stop loss and take profit
        if self.position.side == 'long':
            # Check stop loss (price went down)
            if low_price <= self.position.stop_loss:
                exit_reason = 'stop_loss'
                exit_price = self.position.stop_loss
            # Check take profit (price went up)
            elif high_price >= self.position.take_profit:
                exit_reason = 'take_profit'
                exit_price = self.position.take_profit

        elif self.position.side == 'short':
            # Check stop loss (price went up)
            if high_price >= self.position.stop_loss:
                exit_reason = 'stop_loss'
                exit_price = self.position.stop_loss
            # Check take profit (price went down)
            elif low_price <= self.position.take_profit:
                exit_reason = 'take_profit'
                exit_price = self.position.take_profit

        # Check strategy's close signal
        if not exit_reason:
            close_signal = self.strategy.should_close_position(
                df, index, self.position.side, self.position.get_avg_price()
            )
            if close_signal:
                exit_reason = f'strategy_signal_{close_signal}'
                exit_price = close_price

        # Execute exit
        if exit_reason:
            self._close_position(row, exit_reason, exit_price)

    def _close_position(self, row: pd.Series, exit_reason: str, exit_price: Optional[float] = None):
        """Close current position"""
        if not self.position:
            return

        # Get exit price
        if exit_price is None:
            exit_price = self._get_execution_price(row['close'], self.position.side, is_entry=False)
        else:
            # Apply slippage to TP/SL execution
            exit_price = self._get_execution_price(exit_price, self.position.side, is_entry=False)

        # Calculate PnL
        avg_entry_price = self.position.get_avg_price()
        quantity = self.position.total_quantity

        if self.position.side == 'long':
            gross_pnl = (exit_price - avg_entry_price) * quantity
        else:  # short
            gross_pnl = (avg_entry_price - exit_price) * quantity

        # Calculate fees
        exit_value = exit_price * quantity
        fees = exit_value * self.fee_rate + self.position.total_cost * self.fee_rate

        # Net PnL
        net_pnl = gross_pnl - fees
        pnl_percent = (net_pnl / self.position.total_cost) * 100

        # Add proceeds to capital
        self.capital += exit_value
        self.capital += net_pnl

        # Record trade
        self.trade_counter += 1
        trade = Trade(
            id=self.trade_counter,
            entry_time=self.position.entry_time,
            exit_time=row['timestamp'],
            side=self.position.side,
            entry_price=avg_entry_price,
            exit_price=exit_price,
            quantity=quantity,
            pnl=net_pnl,
            pnl_percent=pnl_percent,
            fees=fees,
            exit_reason=exit_reason,
            steps=self.position.current_step + 1
        )
        self.trades.append(trade)

        # Clear position
        self.position = None

    def _calculate_equity(self, row: pd.Series) -> float:
        """Calculate current equity (capital + unrealized PnL)"""
        if not self.position:
            return self.capital

        # Calculate unrealized PnL
        current_price = row['close']
        avg_entry_price = self.position.get_avg_price()
        quantity = self.position.total_quantity

        if self.position.side == 'long':
            unrealized_pnl = (current_price - avg_entry_price) * quantity
        else:  # short
            unrealized_pnl = (avg_entry_price - current_price) * quantity

        return self.capital + unrealized_pnl

    def _get_execution_price(self, price: float, side: str, is_entry: bool) -> float:
        """Apply slippage to execution price"""
        if is_entry:
            # Entry: buy at higher price for long, sell at lower for short
            if side == 'long':
                return price * (1 + self.slippage)
            else:  # short
                return price * (1 - self.slippage)
        else:
            # Exit: sell at lower price for long, buy at higher for short
            if side == 'long':
                return price * (1 - self.slippage)
            else:  # short
                return price * (1 + self.slippage)

    def _calculate_metrics(self, symbol: str) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'symbol': symbol,
                'initial_capital': self.initial_capital,
                'final_capital': self.capital,
                'total_pnl': 0.0,
                'total_pnl_percent': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'max_drawdown': 0.0,
                'max_drawdown_percent': 0.0,
                'sharpe_ratio': 0.0,
                'avg_trade_pnl': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'trades': [],
                'equity_curve': self.equity_curve,
                'timestamps': [ts.isoformat() if isinstance(ts, datetime) else ts for ts in self.timestamps]
            }

        # Basic metrics
        total_pnl = sum(t.pnl for t in self.trades)
        total_pnl_percent = (total_pnl / self.initial_capital) * 100

        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]

        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        win_rate = (num_wins / len(self.trades)) * 100 if self.trades else 0

        # Profit factor
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Average metrics
        avg_trade_pnl = total_pnl / len(self.trades) if self.trades else 0
        avg_win = sum(t.pnl for t in winning_trades) / num_wins if num_wins > 0 else 0
        avg_loss = sum(t.pnl for t in losing_trades) / num_losses if num_losses > 0 else 0

        largest_win = max((t.pnl for t in winning_trades), default=0)
        largest_loss = min((t.pnl for t in losing_trades), default=0)

        # Drawdown
        max_dd, max_dd_percent = self._calculate_max_drawdown()

        # Sharpe ratio
        sharpe = self._calculate_sharpe_ratio()

        return {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_pnl': round(total_pnl, 2),
            'total_pnl_percent': round(total_pnl_percent, 2),
            'total_trades': len(self.trades),
            'winning_trades': num_wins,
            'losing_trades': num_losses,
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_dd, 2),
            'max_drawdown_percent': round(max_dd_percent, 2),
            'sharpe_ratio': round(sharpe, 2),
            'avg_trade_pnl': round(avg_trade_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'trades': [t.to_dict() for t in self.trades],
            'equity_curve': self.equity_curve,
            'timestamps': [ts.isoformat() if isinstance(ts, datetime) else ts for ts in self.timestamps]
        }

    def _calculate_max_drawdown(self) -> Tuple[float, float]:
        """Calculate maximum drawdown"""
        if len(self.equity_curve) < 2:
            return 0.0, 0.0

        peak = self.equity_curve[0]
        max_dd = 0.0
        max_dd_percent = 0.0

        for equity in self.equity_curve[1:]:
            if equity > peak:
                peak = equity
            dd = peak - equity
            dd_percent = (dd / peak) * 100 if peak > 0 else 0

            if dd > max_dd:
                max_dd = dd
                max_dd_percent = dd_percent

        return max_dd, max_dd_percent

    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        if len(self.equity_curve) < 2:
            return 0.0

        # Calculate returns
        returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(ret)

        if not returns:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        # Annualize (assuming hourly data, 24*365 periods per year)
        sharpe = ((mean_return - risk_free_rate) / std_return) * np.sqrt(24 * 365)

        return sharpe
