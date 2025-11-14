"""
Main Telegram Bot File
"""
import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from .config import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from .api_client import api_client
from .handlers.start import start_command, help_command, menu_command
from .handlers.status import status_command, position_command, pnl_command, strategies_command
from .handlers.trading import (
    start_trading_command,
    start_bot_command,
    stop_trading_command,
    pause_command,
    resume_command,
    emergency_command
)
from .handlers.backtest import backtest_command, run_backtest_command, results_command
from .handlers.callbacks import button_callback

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)


async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "L An error occurred while processing your request. Please try again."
            )
    except Exception as e:
        logger.error(f"Error in error_handler: {e}")


async def unknown_command(update, context):
    """Handle unknown commands"""
    await update.message.reply_text(
        "S Unknown command. Use /help to see available commands."
    )


def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    logger.info("Starting Telegram Bot...")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))

    # Status commands
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("position", position_command))
    application.add_handler(CommandHandler("pnl", pnl_command))
    application.add_handler(CommandHandler("strategies", strategies_command))

    # Trading commands
    application.add_handler(CommandHandler("start_trading", start_trading_command))
    application.add_handler(CommandHandler("start_bot", start_bot_command))
    application.add_handler(CommandHandler("stop_trading", stop_trading_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
    application.add_handler(CommandHandler("emergency", emergency_command))

    # Backtest commands
    application.add_handler(CommandHandler("backtest", backtest_command))
    application.add_handler(CommandHandler("run_backtest", run_backtest_command))
    application.add_handler(CommandHandler("results", results_command))

    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot started! Polling for updates...")
    application.run_polling(allowed_updates=["message", "callback_query"])


async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down bot...")
    await api_client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        asyncio.run(shutdown())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        asyncio.run(shutdown())
