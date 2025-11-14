"""
Status and Information Command Handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..api_client import api_client
from ..keyboards import get_trading_control_keyboard, get_back_keyboard
from ..handlers.start import is_authorized

logger = logging.getLogger(__name__)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Fetching bot status...")

    try:
        status_data = await api_client.get_trading_status()

        if "error" in status_data:
            error_msg = status_data.get("error", "Unknown error")
            if "status" in status_data and status_data["status"] == 404:
                text = "> *Bot Status*\n\n" \
                       "Status: « Stopped\n\n" \
                       "The trading bot is not currently running."
                await update.message.reply_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=get_trading_control_keyboard(bot_running=False)
                )
            else:
                await update.message.reply_text(
                    f"L Error fetching status: {error_msg}",
                    reply_markup=get_back_keyboard()
                )
            return

        # Format status message
        status = status_data.get("status", "unknown")
        capital = status_data.get("capital", 0)
        total_pnl = status_data.get("total_pnl", 0)
        total_pnl_percent = status_data.get("total_pnl_percent", 0)
        total_trades = status_data.get("total_trades", 0)

        # Status emoji
        status_emoji = {
            "stopped": "«",
            "starting": "=á",
            "running": "=â",
            "paused": "=á",
        }.get(status.lower(), "ª")

        text = f"> *Bot Status*\n\n"
        text += f"Status: {status_emoji} {status.upper()}\n"
        text += f"Capital: ${capital:.2f}\n"
        text += f"Total PnL: ${total_pnl:.2f} ({total_pnl_percent:+.2f}%)\n"
        text += f"Total Trades: {total_trades}\n\n"

        # Safety status
        safety = status_data.get("safety_status", {})
        if safety:
            text += "*Safety Status:*\n"
            text += f"" Open Positions: {safety.get('open_positions_count', 0)}\n"
            text += f"" Daily Trades: {safety.get('daily_trades_count', 0)}\n"
            text += f"" Daily PnL: ${safety.get('daily_pnl', 0):.2f}\n"
            text += f"" Can Trade: {'' if safety.get('can_trade') else 'L'}\n"

            warnings = safety.get("warnings", [])
            if warnings:
                text += f"\n  *Warnings:*\n"
                for warn in warnings:
                    text += f"" {warn}\n"

        bot_running = status.lower() in ["running", "paused", "starting"]

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_trading_control_keyboard(bot_running=bot_running)
        )

    except Exception as e:
        logger.error(f"Error in status_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /position command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Fetching position...")

    try:
        status_data = await api_client.get_trading_status()

        if "error" in status_data:
            await update.message.reply_text(
                "L Error fetching position. Bot may not be running.",
                reply_markup=get_back_keyboard()
            )
            return

        position = status_data.get("position")

        if not position:
            text = "=¼ *Current Position*\n\n" \
                   "No open position"
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=get_back_keyboard()
            )
            return

        # Format position message
        side = position.get("side", "").upper()
        entry_price = position.get("entry_price", 0)
        quantity = position.get("quantity", 0)
        current_price = position.get("current_price", 0)
        pnl = position.get("pnl", 0)
        pnl_percent = position.get("pnl_percent", 0)
        steps = position.get("steps", 0)

        side_emoji = "=È" if side == "LONG" else "=É"
        pnl_emoji = "=â" if pnl >= 0 else "=4"

        text = f"=¼ *Current Position*\n\n"
        text += f"{side_emoji} Side: *{side}*\n"
        text += f"Entry Price: ${entry_price:.2f}\n"
        text += f"Current Price: ${current_price:.2f}\n"
        text += f"Quantity: {quantity:.6f}\n"
        text += f"Steps: {steps}\n\n"
        text += f"{pnl_emoji} PnL: ${pnl:.2f} ({pnl_percent:+.2f}%)\n"

        if position.get("tp_price"):
            text += f"\n<¯ Take Profit: ${position['tp_price']:.2f}"
        if position.get("sl_price"):
            text += f"\n=á Stop Loss: ${position['sl_price']:.2f}"

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in position_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pnl command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Fetching PnL data...")

    try:
        # Get current status
        status_data = await api_client.get_trading_status()

        if "error" in status_data:
            await update.message.reply_text(
                "L Error fetching PnL data.",
                reply_markup=get_back_keyboard()
            )
            return

        # Get trade history
        history_data = await api_client.get_trade_history()

        total_pnl = status_data.get("total_pnl", 0)
        total_pnl_percent = status_data.get("total_pnl_percent", 0)
        total_trades = status_data.get("total_trades", 0)
        capital = status_data.get("capital", 0)

        pnl_emoji = "=â" if total_pnl >= 0 else "=4"

        text = f"=È *Profit & Loss*\n\n"
        text += f"Capital: ${capital:.2f}\n"
        text += f"{pnl_emoji} Total PnL: ${total_pnl:.2f} ({total_pnl_percent:+.2f}%)\n"
        text += f"Total Trades: {total_trades}\n\n"

        # Recent trades
        if "error" not in history_data and history_data.get("trades"):
            trades = history_data["trades"][:5]  # Last 5 trades
            text += "*Recent Trades:*\n"
            for trade in trades:
                side = trade["side"].upper()
                pnl = trade["pnl"]
                pnl_pct = trade["pnl_percent"]
                emoji = "=â" if pnl >= 0 else "=4"
                text += f"{emoji} {side}: ${pnl:.2f} ({pnl_pct:+.2f}%)\n"
        else:
            text += "No trade history available."

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in pnl_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def strategies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /strategies command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Fetching strategies...")

    try:
        strategies_data = await api_client.get_strategies(limit=10)

        if "error" in strategies_data:
            await update.message.reply_text(
                "L Error fetching strategies.",
                reply_markup=get_back_keyboard()
            )
            return

        strategies = strategies_data.get("strategies", [])
        total = strategies_data.get("total", 0)

        if not strategies:
            text = "=Ë *Strategies*\n\nNo strategies found."
        else:
            text = f"=Ë *Strategies* (Total: {total})\n\n"
            for strategy in strategies[:10]:
                active = "" if strategy.get("is_active") else "L"
                text += f"{active} *{strategy['name']}*\n"
                text += f"   ID: {strategy['id']}\n"
                text += f"   Class: {strategy['class_name']}\n\n"

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in strategies_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )
