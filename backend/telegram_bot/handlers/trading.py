"""
Trading Control Command Handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..api_client import api_client
from ..keyboards import get_confirmation_keyboard, get_back_keyboard, get_strategy_selection_keyboard
from ..handlers.start import is_authorized

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_STRATEGY, ENTERING_CAPITAL, ENTERING_LIMITS = range(3)


async def start_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start_trading command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return ConversationHandler.END

    # Check if bot is already running
    try:
        status_data = await api_client.get_trading_status()
        if "error" not in status_data and status_data.get("status") in ["running", "paused", "starting"]:
            await update.message.reply_text(
                "  Trading bot is already running!\n\n"
                "Use /stop_trading to stop it first.",
                reply_markup=get_back_keyboard()
            )
            return ConversationHandler.END
    except:
        pass

    # Get strategies
    await update.message.reply_text("ó Fetching strategies...")

    try:
        strategies_data = await api_client.get_strategies(limit=20)

        if "error" in strategies_data or not strategies_data.get("strategies"):
            await update.message.reply_text(
                "L No strategies available. Please create a strategy first.",
                reply_markup=get_back_keyboard()
            )
            return ConversationHandler.END

        strategies = strategies_data["strategies"]

        # Show simple version for now
        text = "=€ *Start Live Trading*\n\n"
        text += "  *WARNING: This will trade with REAL MONEY!*\n\n"
        text += "To start trading, use:\n"
        text += "`/start_bot <strategy_id>`\n\n"
        text += "*Available Strategies:*\n"
        for s in strategies[:5]:
            text += f"" ID {s['id']}: {s['name']}\n"

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in start_trading_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )
        return ConversationHandler.END


async def start_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start_bot <strategy_id> command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    # Parse arguments
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: `/start_bot <strategy_id>`\n\n"
            "Example: `/start_bot 1`\n\n"
            "Use /strategies to see available strategies.",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
        return

    try:
        strategy_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "L Invalid strategy ID. Must be a number.",
            reply_markup=get_back_keyboard()
        )
        return

    # Confirmation
    text = (
        "  *CONFIRM: Start Live Trading*\n\n"
        f"Strategy ID: {strategy_id}\n"
        "Symbol: BTC/USDT\n"
        "Timeframe: 1h\n"
        "Capital: $1000\n"
        "Max Position: $100\n"
        "Max Daily Loss: 5%\n"
        "Max Daily Trades: 10\n\n"
        "  *This will trade with REAL MONEY!*\n\n"
        "Are you sure you want to proceed?"
    )

    # Store strategy_id in context
    context.user_data['pending_strategy_id'] = strategy_id

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_confirmation_keyboard("start_trading")
    )


async def stop_trading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop_trading command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Stopping trading bot...")

    try:
        result = await api_client.stop_trading()

        if "error" in result:
            await update.message.reply_text(
                f"L Error stopping bot: {result['error']}",
                reply_markup=get_back_keyboard()
            )
        else:
            await update.message.reply_text(
                " Trading bot stopped successfully!",
                reply_markup=get_back_keyboard()
            )

    except Exception as e:
        logger.error(f"Error in stop_trading_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pause command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Pausing trading bot...")

    try:
        result = await api_client.pause_trading()

        if "error" in result:
            await update.message.reply_text(
                f"L Error pausing bot: {result['error']}",
                reply_markup=get_back_keyboard()
            )
        else:
            await update.message.reply_text(
                "ø Trading bot paused successfully!",
                reply_markup=get_back_keyboard()
            )

    except Exception as e:
        logger.error(f"Error in pause_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resume command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    await update.message.reply_text("ó Resuming trading bot...")

    try:
        result = await api_client.resume_trading()

        if "error" in result:
            await update.message.reply_text(
                f"L Error resuming bot: {result['error']}",
                reply_markup=get_back_keyboard()
            )
        else:
            await update.message.reply_text(
                "¶ Trading bot resumed successfully!",
                reply_markup=get_back_keyboard()
            )

    except Exception as e:
        logger.error(f"Error in resume_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def emergency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /emergency command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    text = (
        "=¨ *EMERGENCY STOP*\n\n"
        "This will immediately stop all trading and close positions.\n\n"
        "  Are you sure?"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_confirmation_keyboard("emergency_stop")
    )
