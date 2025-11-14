"""
Callback Query Handlers for Inline Buttons
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..api_client import api_client
from ..keyboards import (
    get_main_menu_keyboard,
    get_trading_control_keyboard,
    get_backtest_keyboard,
    get_settings_keyboard,
    get_back_keyboard
)
from ..handlers.start import is_authorized

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await query.answer("L Access Denied")
        return

    await query.answer()

    data = query.data

    # Main menu commands
    if data == "cmd_status":
        await handle_status_button(update, context)
    elif data == "cmd_position":
        await handle_position_button(update, context)
    elif data == "cmd_pnl":
        await handle_pnl_button(update, context)
    elif data == "cmd_strategies":
        await handle_strategies_button(update, context)
    elif data == "cmd_start_trading":
        await handle_start_trading_button(update, context)
    elif data == "cmd_stop_trading":
        await handle_stop_trading_button(update, context)
    elif data == "cmd_pause":
        await handle_pause_button(update, context)
    elif data == "cmd_resume":
        await handle_resume_button(update, context)
    elif data == "cmd_backtest":
        await query.edit_message_text(
            "=, *Backtest Menu*\n\nChoose an option:",
            parse_mode="Markdown",
            reply_markup=get_backtest_keyboard()
        )
    elif data == "cmd_settings":
        await query.edit_message_text(
            "™ *Settings*\n\nConfigure bot settings:",
            parse_mode="Markdown",
            reply_markup=get_settings_keyboard()
        )
    elif data == "cmd_help":
        await handle_help_button(update, context)

    # Trading control
    elif data == "trading_pause":
        await handle_trading_pause(update, context)
    elif data == "trading_stop":
        await handle_trading_stop(update, context)
    elif data == "trading_emergency":
        await handle_trading_emergency(update, context)

    # Confirmations
    elif data.startswith("confirm_"):
        await handle_confirmation(update, context, data[8:])
    elif data == "cancel_action":
        await query.edit_message_text(
            "L Action cancelled",
            reply_markup=get_back_keyboard()
        )

    # Navigation
    elif data == "back_main":
        await query.edit_message_text(
            "=Ë *Main Menu*\n\nSelect an option:",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )


async def handle_status_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle status button"""
    query = update.callback_query
    await query.edit_message_text("ó Fetching bot status...")

    try:
        status_data = await api_client.get_trading_status()

        if "error" in status_data:
            if "status" in status_data and status_data["status"] == 404:
                text = "> *Bot Status*\n\nStatus: « Stopped\n\nThe trading bot is not currently running."
                await query.edit_message_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=get_trading_control_keyboard(bot_running=False)
                )
            else:
                await query.edit_message_text(
                    f"L Error: {status_data['error']}",
                    reply_markup=get_back_keyboard()
                )
            return

        status = status_data.get("status", "unknown")
        capital = status_data.get("capital", 0)
        total_pnl = status_data.get("total_pnl", 0)
        total_pnl_percent = status_data.get("total_pnl_percent", 0)
        total_trades = status_data.get("total_trades", 0)

        status_emoji = {"stopped": "«", "running": "=â", "paused": "=á"}.get(status.lower(), "ª")

        text = f"> *Bot Status*\n\n"
        text += f"Status: {status_emoji} {status.upper()}\n"
        text += f"Capital: ${capital:.2f}\n"
        text += f"PnL: ${total_pnl:.2f} ({total_pnl_percent:+.2f}%)\n"
        text += f"Trades: {total_trades}"

        bot_running = status.lower() in ["running", "paused"]
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_trading_control_keyboard(bot_running=bot_running)
        )

    except Exception as e:
        logger.error(f"Error handling status button: {e}")
        await query.edit_message_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def handle_position_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle position button"""
    query = update.callback_query
    await query.edit_message_text("ó Fetching position...")

    try:
        status_data = await api_client.get_trading_status()

        if "error" in status_data:
            await query.edit_message_text(
                "L Error fetching position.",
                reply_markup=get_back_keyboard()
            )
            return

        position = status_data.get("position")

        if not position:
            await query.edit_message_text(
                "=¼ *Current Position*\n\nNo open position",
                parse_mode="Markdown",
                reply_markup=get_back_keyboard()
            )
            return

        side = position.get("side", "").upper()
        entry_price = position.get("entry_price", 0)
        current_price = position.get("current_price", 0)
        pnl = position.get("pnl", 0)
        pnl_percent = position.get("pnl_percent", 0)

        side_emoji = "=È" if side == "LONG" else "=É"
        pnl_emoji = "=â" if pnl >= 0 else "=4"

        text = f"=¼ *Current Position*\n\n"
        text += f"{side_emoji} {side}\n"
        text += f"Entry: ${entry_price:.2f}\n"
        text += f"Current: ${current_price:.2f}\n"
        text += f"{pnl_emoji} PnL: ${pnl:.2f} ({pnl_percent:+.2f}%)"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error handling position button: {e}")
        await query.edit_message_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def handle_pnl_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PnL button"""
    query = update.callback_query
    await query.edit_message_text("ó Fetching PnL...")

    try:
        status_data = await api_client.get_trading_status()

        if "error" in status_data:
            await query.edit_message_text(
                "L Error fetching PnL.",
                reply_markup=get_back_keyboard()
            )
            return

        total_pnl = status_data.get("total_pnl", 0)
        total_pnl_percent = status_data.get("total_pnl_percent", 0)
        total_trades = status_data.get("total_trades", 0)
        capital = status_data.get("capital", 0)

        pnl_emoji = "=â" if total_pnl >= 0 else "=4"

        text = f"=È *Profit & Loss*\n\n"
        text += f"Capital: ${capital:.2f}\n"
        text += f"{pnl_emoji} Total PnL: ${total_pnl:.2f} ({total_pnl_percent:+.2f}%)\n"
        text += f"Total Trades: {total_trades}"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error handling PnL button: {e}")
        await query.edit_message_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def handle_strategies_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle strategies button"""
    query = update.callback_query
    await query.edit_message_text("ó Fetching strategies...")

    try:
        strategies_data = await api_client.get_strategies(limit=10)

        if "error" in strategies_data:
            await query.edit_message_text(
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
            for strategy in strategies[:5]:
                active = "" if strategy.get("is_active") else "L"
                text += f"{active} *{strategy['name']}*\n   ID: {strategy['id']}\n\n"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error handling strategies button: {e}")
        await query.edit_message_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def handle_start_trading_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start trading button"""
    query = update.callback_query
    await query.edit_message_text(
        "=€ *Start Live Trading*\n\n"
        "Use command: `/start_bot <strategy_id>`\n\n"
        "Example: `/start_bot 1`\n\n"
        "  Trading with REAL MONEY!",
        parse_mode="Markdown",
        reply_markup=get_back_keyboard()
    )


async def handle_stop_trading_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stop trading button"""
    query = update.callback_query
    await query.edit_message_text("ó Stopping bot...")

    try:
        result = await api_client.stop_trading()

        if "error" in result:
            await query.edit_message_text(
                f"L Error: {result['error']}",
                reply_markup=get_back_keyboard()
            )
        else:
            await query.edit_message_text(
                " Bot stopped successfully!",
                reply_markup=get_back_keyboard()
            )

    except Exception as e:
        await query.edit_message_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def handle_pause_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pause button"""
    query = update.callback_query
    await query.edit_message_text("ó Pausing bot...")

    try:
        result = await api_client.pause_trading()
        if "error" not in result:
            await query.edit_message_text(
                "ø Bot paused!",
                reply_markup=get_back_keyboard()
            )
        else:
            await query.edit_message_text(
                f"L Error: {result['error']}",
                reply_markup=get_back_keyboard()
            )
    except Exception as e:
        await query.edit_message_text(f"L Error: {str(e)}", reply_markup=get_back_keyboard())


async def handle_resume_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle resume button"""
    query = update.callback_query
    await query.edit_message_text("ó Resuming bot...")

    try:
        result = await api_client.resume_trading()
        if "error" not in result:
            await query.edit_message_text(
                "¶ Bot resumed!",
                reply_markup=get_back_keyboard()
            )
        else:
            await query.edit_message_text(
                f"L Error: {result['error']}",
                reply_markup=get_back_keyboard()
            )
    except Exception as e:
        await query.edit_message_text(f"L Error: {str(e)}", reply_markup=get_back_keyboard())


async def handle_trading_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle trading pause from inline button"""
    await handle_pause_button(update, context)


async def handle_trading_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle trading stop from inline button"""
    await handle_stop_trading_button(update, context)


async def handle_trading_emergency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle emergency stop from inline button"""
    query = update.callback_query
    await query.edit_message_text("=¨ Emergency stopping...")

    try:
        result = await api_client.emergency_stop()
        if "error" not in result:
            await query.edit_message_text(
                "=¨ EMERGENCY STOP ACTIVATED!",
                reply_markup=get_back_keyboard()
            )
        else:
            await query.edit_message_text(
                f"L Error: {result['error']}",
                reply_markup=get_back_keyboard()
            )
    except Exception as e:
        await query.edit_message_text(f"L Error: {str(e)}", reply_markup=get_back_keyboard())


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """Handle confirmation actions"""
    query = update.callback_query

    if action == "start_trading":
        strategy_id = context.user_data.get('pending_strategy_id')
        if not strategy_id:
            await query.edit_message_text(
                "L Error: No strategy selected",
                reply_markup=get_back_keyboard()
            )
            return

        await query.edit_message_text("=€ Starting bot...")

        try:
            result = await api_client.start_trading(
                strategy_id=strategy_id,
                symbol="BTC/USDT",
                timeframe="1h",
                capital=1000,
                max_position_size_usd=100,
                max_daily_loss_percent=5,
                max_daily_trades=10
            )

            if "error" in result:
                await query.edit_message_text(
                    f"L Error: {result['error']}",
                    reply_markup=get_back_keyboard()
                )
            else:
                await query.edit_message_text(
                    " Trading bot started!",
                    reply_markup=get_back_keyboard()
                )

        except Exception as e:
            await query.edit_message_text(
                f"L Error: {str(e)}",
                reply_markup=get_back_keyboard()
            )

    elif action == "emergency_stop":
        await handle_trading_emergency(update, context)


async def handle_help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help button"""
    query = update.callback_query

    help_text = (
        "=Ú *Help*\n\n"
        "Use /help for full command list.\n\n"
        "Quick commands:\n"
        "" /status - Bot status\n"
        "" /position - Current position\n"
        "" /pnl - Profit & Loss\n"
        "" /start\\_bot <id> - Start trading\n"
        "" /stop\\_trading - Stop bot"
    )

    await query.edit_message_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_back_keyboard()
    )
