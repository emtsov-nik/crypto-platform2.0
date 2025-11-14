"""
Inline Keyboards for Telegram Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data="cmd_status"),
            InlineKeyboardButton("💼 Position", callback_data="cmd_position"),
        ],
        [
            InlineKeyboardButton("💰 PnL", callback_data="cmd_pnl"),
            InlineKeyboardButton("⚙️ Strategies", callback_data="cmd_strategies"),
        ],
        [
            InlineKeyboardButton("▶️ Start Trading", callback_data="cmd_start_trading"),
            InlineKeyboardButton("⏹️ Stop Trading", callback_data="cmd_stop_trading"),
        ],
        [
            InlineKeyboardButton("⏸️ Pause", callback_data="cmd_pause"),
            InlineKeyboardButton("▶️ Resume", callback_data="cmd_resume"),
        ],
        [
            InlineKeyboardButton("📈 Run Backtest", callback_data="cmd_backtest"),
            InlineKeyboardButton("📋 View Backtests", callback_data="cmd_view_backtests"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="cmd_settings"),
            InlineKeyboardButton("❓ Help", callback_data="cmd_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_trading_control_keyboard(bot_running: bool = False) -> InlineKeyboardMarkup:
    """Trading control keyboard"""
    if bot_running:
        keyboard = [
            [
                InlineKeyboardButton("⏸️ Pause", callback_data="trading_pause"),
                InlineKeyboardButton("⏹️ Stop", callback_data="trading_stop"),
            ],
            [
                InlineKeyboardButton("🚨 Emergency Stop", callback_data="trading_emergency"),
            ],
            [
                InlineKeyboardButton("◀️ Back", callback_data="back_main"),
            ],
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("▶️ Start Trading", callback_data="trading_start"),
            ],
            [
                InlineKeyboardButton("◀️ Back", callback_data="back_main"),
            ],
        ]
    return InlineKeyboardMarkup(keyboard)


def get_strategy_selection_keyboard(strategies: list) -> InlineKeyboardMarkup:
    """Strategy selection keyboard"""
    keyboard = []
    for strategy in strategies[:10]:  # Show first 10 strategies
        keyboard.append([
            InlineKeyboardButton(
                f"{strategy['name']} (ID: {strategy['id']})",
                callback_data=f"select_strategy_{strategy['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def get_backtest_keyboard() -> InlineKeyboardMarkup:
    """Backtest keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📈 Run New Backtest", callback_data="backtest_new"),
        ],
        [
            InlineKeyboardButton("📋 View Results", callback_data="backtest_results"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Confirmation keyboard for critical actions"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, proceed", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_action"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
        ],
        [
            InlineKeyboardButton("🛡️ Safety Limits", callback_data="settings_safety"),
        ],
        [
            InlineKeyboardButton("⚙️ Default Parameters", callback_data="settings_defaults"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Simple cancel keyboard"""
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back keyboard"""
    keyboard = [
        [InlineKeyboardButton("◀️ Back to Menu", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
