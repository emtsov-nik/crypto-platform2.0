"""
Start and Help Command Handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards import get_main_menu_keyboard
from ..config import REQUIRE_AUTH, ALLOWED_USER_IDS

logger = logging.getLogger(__name__)


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized"""
    if not REQUIRE_AUTH:
        return True
    return user_id in ALLOWED_USER_IDS


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id

    logger.info(f"User {user_id} ({user.username}) used /start command")

    # Check authorization
    if not is_authorized(user_id):
        await update.message.reply_text(
            "🔒 *Access Denied*\n\n"
            "You are not authorized to use this bot.\n"
            f"Your Telegram ID: `{user_id}`\n\n"
            "Please contact the administrator to get access.",
            parse_mode="Markdown"
        )
        logger.warning(f"Unauthorized access attempt from user {user_id} ({user.username})")
        return

    # Welcome message
    welcome_text = (
        f"👋 Welcome, {user.first_name}!\n\n"
        "🤖 *Crypto Trading Bot*\n\n"
        "This bot allows you to:\n"
        "📊 Monitor trading bot status\n"
        "💰 View current positions and PnL\n"
        "▶️ Start/Stop live trading\n"
        "📈 Run backtests on strategies\n"
        "⚙️ Manage trading strategies\n"
        "🔧 Configure bot settings\n\n"
        "⚠️ *Warning:* Live trading uses real money. Always use caution!\n\n"
        "Use the menu below to get started 👇"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("🔒 Access Denied")
        return

    help_text = (
        "📚 *Available Commands:*\n\n"
        "📋 *Basic Commands*\n"
        "/start - Start the bot and show main menu\n"
        "/help - Show this help message\n"
        "/menu - Show main menu\n\n"
        "📋 *Trading Commands*\n"
        "/status - Show bot status\n"
        "/position - Show current position\n"
        "/pnl - Show profit and loss\n"
        "/start\\_trading - Start live trading\n"
        "/stop\\_trading - Stop trading bot\n"
        "/pause - Pause trading\n"
        "/resume - Resume trading\n\n"
        "📋 *Strategy Commands*\n"
        "/strategies - List available strategies\n"
        "/backtest - Run backtest\n"
        "/results - View backtest results\n\n"
        "📋 *Other Commands*\n"
        "/settings - Bot settings\n"
        "/emergency - Emergency stop (⚠️)\n\n"
        "💡 *Tip:* You can use inline buttons for easier navigation!"
    )

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("🔒 Access Denied")
        return

    await update.message.reply_text(
        "📱 *Main Menu*\n\nSelect an option:",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )
