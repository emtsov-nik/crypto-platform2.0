"""
Backtest Command Handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..api_client import api_client
from ..keyboards import get_backtest_keyboard, get_back_keyboard
from ..handlers.start import is_authorized

logger = logging.getLogger(__name__)


async def backtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /backtest command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    text = (
        "=, *Backtest*\n\n"
        "To run a backtest, use:\n"
        "`/run_backtest <strategy_id>`\n\n"
        "Example: `/run_backtest 1`\n\n"
        "To view results:\n"
        "`/results`"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_backtest_keyboard()
    )


async def run_backtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /run_backtest <strategy_id> command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    # Parse arguments
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: `/run_backtest <strategy_id>`\n\n"
            "Example: `/run_backtest 1`",
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

    await update.message.reply_text("ó Starting backtest...")

    try:
        result = await api_client.run_backtest(
            strategy_id=strategy_id,
            symbol="BTC/USDT",
            timeframe="1h",
            initial_capital=10000
        )

        if "error" in result:
            await update.message.reply_text(
                f"L Error running backtest: {result['error']}",
                reply_markup=get_back_keyboard()
            )
            return

        backtest_id = result.get("backtest_id")
        await update.message.reply_text(
            f" Backtest started!\n\n"
            f"Backtest ID: {backtest_id}\n\n"
            f"Use `/results {backtest_id}` to view results when complete.",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in run_backtest_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def results_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /results [backtest_id] command"""
    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("L Access Denied")
        return

    # If no backtest_id provided, show recent backtests
    if not context.args:
        await update.message.reply_text("ó Fetching recent backtests...")

        try:
            backtests_data = await api_client.get_backtests(limit=10)

            if "error" in backtests_data or not backtests_data.get("backtests"):
                await update.message.reply_text(
                    "No backtests found.",
                    reply_markup=get_back_keyboard()
                )
                return

            backtests = backtests_data["backtests"]
            text = "=Ê *Recent Backtests*\n\n"
            for bt in backtests[:5]:
                status = bt.get("status", "unknown")
                text += f"ID {bt['id']}: {status}\n"
                if status == "completed":
                    pnl = bt.get("total_pnl_percent", 0)
                    text += f"   PnL: {pnl:+.2f}%\n"

            text += f"\nUse `/results <id>` to view details."

            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=get_back_keyboard()
            )

        except Exception as e:
            logger.error(f"Error fetching backtests: {e}")
            await update.message.reply_text(
                f"L Error: {str(e)}",
                reply_markup=get_back_keyboard()
            )
        return

    # Show specific backtest results
    try:
        backtest_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "L Invalid backtest ID.",
            reply_markup=get_back_keyboard()
        )
        return

    await update.message.reply_text("ó Fetching results...")

    try:
        results = await api_client.get_backtest_results(backtest_id)

        if "error" in results:
            await update.message.reply_text(
                f"L Error fetching results: {results['error']}",
                reply_markup=get_back_keyboard()
            )
            return

        # Format results
        text = f"=Ê *Backtest Results* (ID: {backtest_id})\n\n"
        text += f"Symbol: {results.get('symbol', 'N/A')}\n"
        text += f"Initial Capital: ${results.get('initial_capital', 0):.2f}\n"
        text += f"Final Capital: ${results.get('final_capital', 0):.2f}\n\n"
        text += f"Total PnL: ${results.get('total_pnl', 0):.2f} ({results.get('total_pnl_percent', 0):+.2f}%)\n"
        text += f"Total Trades: {results.get('total_trades', 0)}\n"
        text += f"Win Rate: {results.get('win_rate', 0):.1f}%\n"
        text += f"Profit Factor: {results.get('profit_factor', 0):.2f}\n"
        text += f"Max Drawdown: {results.get('max_drawdown_percent', 0):.2f}%\n"
        text += f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}\n"

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in results_command: {e}")
        await update.message.reply_text(
            f"L Error: {str(e)}",
            reply_markup=get_back_keyboard()
        )
