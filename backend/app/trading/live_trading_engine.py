"""
⚠️ WARNING: This module executes REAL TRADES with REAL MONEY ⚠️

Live Trading Engine manages real-time trading operations.
EXTREME CAUTION required when modifying this code.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import ccxt

from app.strategies.base_strategy import BaseStrategy
from app.trading.safety_manager import SafetyManager, SafetyLimits

logger = logging.getLogger(__name__)


class BotStatus(Enum):
    """Bot status states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


class LiveTradingEngine:
    """
    Live trading engine with real-time execution

    ⚠️ CRITICAL: This class executes real trades on Binance
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        exchange: ccxt.Exchange,
        symbol: str,
        timeframe: str = '1h',
        capital: float = 1000.0,
        safety_limits: Optional[SafetyLimits] = None
    ):
        self.strategy = strategy
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.capital = capital

        # Safety manager
        self.safety = SafetyManager(safety_limits)
        self.safety.set_starting_capital(capital)

        # State
        self.status = BotStatus.STOPPED
        self.position = None  # Current open position
        self.orders = []  # Active orders
        self.trades_history = []
        self.start_time = None
        self.error_message = None

        logger.info(f"LiveTradingEngine initialized: {symbol} {timeframe}, Capital: ${capital}")

    async def start(self):
        """Start the trading bot"""
        if self.status != BotStatus.STOPPED:
            raise ValueError(f"Cannot start: Bot is {self.status.value}")

        logger.info("🚀 Starting live trading bot...")
        self.status = BotStatus.STARTING

        try:
            # Verify exchange connection
            await self._verify_exchange()

            # Verify account balance
            await self._verify_balance()

            self.status = BotStatus.RUNNING
            self.start_time = datetime.utcnow()
            logger.info("✅ Bot started successfully")

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.status = BotStatus.ERROR
            self.error_message = str(e)
            raise

    async def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        self.status = BotStatus.STOPPING

        try:
            # Close any open positions
            if self.position:
                logger.warning("Closing open position before stopping...")
                await self._close_position("bot_stopped")

            # Cancel pending orders
            if self.orders:
                logger.info(f"Cancelling {len(self.orders)} pending orders...")
                await self._cancel_all_orders()

            self.status = BotStatus.STOPPED
            logger.info("✅ Bot stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            self.status = BotStatus.ERROR
            self.error_message = str(e)
            raise

    async def pause(self):
        """Pause trading (keep positions open)"""
        if self.status != BotStatus.RUNNING:
            raise ValueError(f"Cannot pause: Bot is {self.status.value}")

        logger.info("Pausing trading bot...")
        self.status = BotStatus.PAUSED

    async def resume(self):
        """Resume trading"""
        if self.status != BotStatus.PAUSED:
            raise ValueError(f"Cannot resume: Bot is {self.status.value}")

        logger.info("Resuming trading bot...")
        self.status = BotStatus.RUNNING

    async def process_signal(self, signal: Optional[str]) -> Dict[str, Any]:
        """
        Process a trading signal from strategy

        Args:
            signal: 'long', 'short', or None

        Returns:
            Result dictionary
        """
        if self.status != BotStatus.RUNNING:
            return {'success': False, 'message': f'Bot not running (status: {self.status.value})'}

        if not signal:
            return {'success': True, 'message': 'No signal'}

        # Check if we can trade
        can_continue, reason = self.safety.can_continue_trading(self.capital)
        if not can_continue:
            logger.error(f"Cannot continue trading: {reason}")
            await self.stop()
            return {'success': False, 'message': reason}

        try:
            # If we have an open position, check if we should close it first
            if self.position:
                if self.position['side'] != signal:
                    # Close opposite position
                    await self._close_position("opposite_signal")

            # Open new position if we don't have one
            if not self.position:
                result = await self._open_position(signal)
                return result

            return {'success': True, 'message': 'Position already open'}

        except Exception as e:
            logger.error(f"Error processing signal: {e}")
            return {'success': False, 'message': str(e)}

    async def _open_position(self, side: str) -> Dict[str, Any]:
        """Open a new position"""
        try:
            # Get current price
            ticker = self.exchange.fetch_ticker(self.symbol)
            current_price = ticker['last']

            # Calculate position size
            position_size_usd = min(
                self.capital * 0.1,  # Use 10% of capital per position
                self.safety.limits.max_position_size_usd
            )

            # Check safety
            can_open, reason = self.safety.can_open_position(
                position_size_usd,
                1 if self.position else 0
            )

            if not can_open:
                logger.warning(f"Position opening rejected: {reason}")
                return {'success': False, 'message': reason}

            # Calculate quantity
            quantity = position_size_usd / current_price

            # Place market order
            order_type = 'market'
            order_side = 'buy' if side == 'long' else 'sell'

            logger.info(f"Placing {order_side} {order_type} order: {quantity} {self.symbol} @ ${current_price}")

            # ⚠️ REAL ORDER EXECUTION ⚠️
            order = self.exchange.create_order(
                symbol=self.symbol,
                type=order_type,
                side=order_side,
                amount=quantity
            )

            # Calculate TP/SL
            tp, sl = self.strategy.calculate_exit_prices(current_price, side)

            # Store position
            self.position = {
                'side': side,
                'entry_price': current_price,
                'quantity': quantity,
                'take_profit': tp,
                'stop_loss': sl,
                'entry_time': datetime.utcnow(),
                'order_id': order['id']
            }

            logger.info(f"✅ Position opened: {side} {quantity} @ ${current_price}, TP: ${tp}, SL: ${sl}")

            return {
                'success': True,
                'message': f'Opened {side} position',
                'position': self.position
            }

        except Exception as e:
            logger.error(f"Failed to open position: {e}")
            return {'success': False, 'message': str(e)}

    async def _close_position(self, reason: str) -> Dict[str, Any]:
        """Close current position"""
        if not self.position:
            return {'success': False, 'message': 'No position to close'}

        try:
            # Get current price
            ticker = self.exchange.fetch_ticker(self.symbol)
            exit_price = ticker['last']

            # Place closing order
            order_side = 'sell' if self.position['side'] == 'long' else 'buy'

            logger.info(f"Closing position: {order_side} {self.position['quantity']} @ ${exit_price}")

            # ⚠️ REAL ORDER EXECUTION ⚠️
            order = self.exchange.create_order(
                symbol=self.symbol,
                type='market',
                side=order_side,
                amount=self.position['quantity']
            )

            # Calculate PnL
            if self.position['side'] == 'long':
                pnl = (exit_price - self.position['entry_price']) * self.position['quantity']
            else:
                pnl = (self.position['entry_price'] - exit_price) * self.position['quantity']

            # Record trade
            trade = {
                'side': self.position['side'],
                'entry_price': self.position['entry_price'],
                'exit_price': exit_price,
                'quantity': self.position['quantity'],
                'pnl': pnl,
                'entry_time': self.position['entry_time'],
                'exit_time': datetime.utcnow(),
                'exit_reason': reason
            }

            self.trades_history.append(trade)
            self.capital += pnl
            self.safety.record_trade(pnl)

            logger.info(f"✅ Position closed: PnL=${pnl:.2f}, Reason: {reason}")

            # Clear position
            self.position = None

            return {
                'success': True,
                'message': f'Position closed: {reason}',
                'trade': trade
            }

        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return {'success': False, 'message': str(e)}

    async def _verify_exchange(self):
        """Verify exchange connection"""
        try:
            balance = self.exchange.fetch_balance()
            logger.info("Exchange connection verified")
        except Exception as e:
            raise ValueError(f"Exchange connection failed: {e}")

    async def _verify_balance(self):
        """Verify account has sufficient balance"""
        try:
            balance = self.exchange.fetch_balance()
            # Get quote currency (e.g., USDT from BTC/USDT)
            quote = self.symbol.split('/')[1]
            available = balance['free'].get(quote, 0)

            if available < self.safety.limits.min_capital_usd:
                raise ValueError(f"Insufficient balance: ${available} < ${self.safety.limits.min_capital_usd}")

            logger.info(f"Balance verified: ${available} {quote}")

        except Exception as e:
            raise ValueError(f"Balance verification failed: {e}")

    async def _cancel_all_orders(self):
        """Cancel all open orders"""
        try:
            open_orders = self.exchange.fetch_open_orders(self.symbol)
            for order in open_orders:
                self.exchange.cancel_order(order['id'], self.symbol)
                logger.info(f"Cancelled order: {order['id']}")
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'status': self.status.value,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'capital': self.capital,
            'position': self.position,
            'open_orders': len(self.orders),
            'total_trades': len(self.trades_history),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'error_message': self.error_message,
            'safety_status': self.safety.get_status()
        }
