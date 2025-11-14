# User Guide

Complete guide to using the Crypto Trading Platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Web Dashboard](#web-dashboard)
- [Trading Strategies](#trading-strategies)
- [Backtesting](#backtesting)
- [Live Trading](#live-trading)
- [Telegram Bot](#telegram-bot)
- [Monitoring & Safety](#monitoring--safety)
- [Best Practices](#best-practices)

## Getting Started

### First Time Setup

1. **Complete Installation:**
   - Follow the [Installation Guide](INSTALLATION.md)
   - Ensure all services are running
   - Configure API keys and Telegram bot

2. **Access the Platform:**
   - Open web dashboard at http://localhost:3000
   - Check API docs at http://localhost:8000/docs
   - Test Telegram bot with `/start`

3. **Verify Configuration:**
   - Check connection to Binance (testnet recommended)
   - Verify safety limits are appropriate
   - Test notifications via Telegram

### Understanding the Interface

The platform provides three interfaces:
- **Web Dashboard:** Visual control panel with charts and real-time data
- **REST API:** Programmatic access for custom integrations
- **Telegram Bot:** Mobile control and notifications

## Web Dashboard

### Dashboard Overview

Navigate to http://localhost:3000 to access the web dashboard.

#### Main Navigation

- **Home:** Overview and quick stats
- **Strategies:** Manage trading strategies
- **Backtest:** Run historical simulations
- **Live Trading:** Control live trading bots
- **Market Data:** View charts and indicators

### Home Page

The home page displays:
- System status
- Active trading bots
- Recent performance metrics
- Quick action buttons

### Strategies Page

**View Strategies:**
- Lists all available trading strategies
- Shows strategy parameters
- Displays performance statistics

**Create New Strategy:**
1. Click "Create Strategy"
2. Enter strategy name and description
3. Select strategy type (e.g., RSI + Bollinger Bands)
4. Configure parameters:
   ```
   RSI Period: 14
   RSI Oversold: 30
   RSI Overbought: 70
   BB Period: 20
   BB Standard Deviation: 2.0
   Take Profit %: 2.0
   Stop Loss %: 1.0
   Position Size %: 10.0
   ```
5. Click "Save"

**Edit Strategy:**
1. Click on strategy card
2. Click "Edit"
3. Modify parameters
4. Click "Update"

**Delete Strategy:**
1. Click on strategy card
2. Click "Delete"
3. Confirm deletion

### Market Data Page

**View Price Charts:**
1. Select symbol (e.g., BTC/USDT)
2. Select timeframe (1m, 5m, 15m, 1h, 4h, 1d)
3. View TradingView-style chart with:
   - Candlestick patterns
   - Volume bars
   - Technical indicators

**Available Indicators:**
- RSI (Relative Strength Index)
- Bollinger Bands
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- MACD (Moving Average Convergence Divergence)
- ATR (Average True Range)
- VWAP (Volume Weighted Average Price)

## Trading Strategies

### Built-in Strategies

#### RSI + Bollinger Bands Strategy

**How It Works:**
1. **Entry Conditions (Long):**
   - RSI < Oversold threshold (default: 30)
   - Price touches or breaks below lower Bollinger Band
   - Indicates oversold condition

2. **Entry Conditions (Short):**
   - RSI > Overbought threshold (default: 70)
   - Price touches or breaks above upper Bollinger Band
   - Indicates overbought condition

3. **Exit Conditions:**
   - Take Profit: +2% from entry (default)
   - Stop Loss: -1% from entry (default)
   - RSI crosses back to neutral zone

4. **Position Sizing:**
   - Uses 10% of capital per trade (default)
   - Supports averaging down (up to 3 steps)

**Parameters:**
- `rsi_period`: RSI calculation period (default: 14)
- `rsi_oversold`: Oversold threshold (default: 30)
- `rsi_overbought`: Overbought threshold (default: 70)
- `bb_period`: Bollinger Bands period (default: 20)
- `bb_std`: Standard deviations (default: 2.0)
- `tp_percent`: Take profit percentage (default: 2.0)
- `sl_percent`: Stop loss percentage (default: 1.0)
- `position_size_percent`: Capital allocation (default: 10.0)
- `enable_averaging`: Enable position averaging (default: false)
- `max_avg_steps`: Maximum averaging steps (default: 3)

### Creating Custom Strategies

See [Strategy Examples](STRATEGY_EXAMPLES.md) for detailed instructions on creating custom strategies.

## Backtesting

Backtesting allows you to test strategies against historical data before risking real money.

### Running a Backtest

**Via Web Dashboard:**

1. Navigate to "Backtest" page
2. Click "Run New Backtest"
3. Configure backtest parameters:
   ```
   Strategy: Select from dropdown
   Symbol: BTC/USDT
   Timeframe: 1h
   Initial Capital: $10,000
   Start Date: 2024-01-01
   End Date: 2024-03-01
   Commission: 0.1% (default)
   ```
4. Click "Run Backtest"
5. Wait for completion (progress shown)

**Via API:**

```bash
curl -X POST "http://localhost:8000/api/backtests/run" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": 1,
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "initial_capital": 10000,
    "start_date": "2024-01-01",
    "end_date": "2024-03-01",
    "commission_percent": 0.1
  }'
```

**Via Telegram:**

```
/run_backtest 1
```

### Understanding Backtest Results

**Performance Metrics:**

- **Total Return:** Overall profit/loss percentage
  ```
  Example: +15.5% means you made 15.5% profit
  ```

- **Total Trades:** Number of completed trades
  ```
  Example: 45 trades executed
  ```

- **Win Rate:** Percentage of winning trades
  ```
  Example: 62.2% means 28 wins out of 45 trades
  ```

- **Profit Factor:** Ratio of gross profits to gross losses
  ```
  > 1.0 = Profitable strategy
  Example: 1.85 means $1.85 profit for every $1 loss
  ```

- **Sharpe Ratio:** Risk-adjusted return
  ```
  > 1.0 = Good
  > 2.0 = Very good
  > 3.0 = Excellent
  ```

- **Max Drawdown:** Largest peak-to-trough decline
  ```
  Example: -8.5% means biggest loss from peak was 8.5%
  ```

- **Average Trade:** Average profit/loss per trade
  ```
  Example: $45.60 average profit per trade
  ```

**Trade History:**
- Entry/exit prices and times
- Position size
- Profit/loss per trade
- Duration of each trade

**Equity Curve:**
- Visual representation of capital over time
- Shows drawdown periods
- Identifies winning/losing streaks

### Interpreting Results

**Good Strategy Indicators:**
- ✅ Win rate > 50%
- ✅ Profit factor > 1.5
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 20%
- ✅ Consistent profits across different periods

**Warning Signs:**
- ⚠️ Win rate < 40%
- ⚠️ Profit factor < 1.2
- ⚠️ Large drawdowns (> 30%)
- ⚠️ Few trades (< 20)
- ⚠️ Profits only in bull markets

### Optimizing Strategy Parameters

1. **Start with defaults:**
   - Run initial backtest with default parameters

2. **Identify weak points:**
   - Too many losses? Adjust entry conditions
   - Large drawdowns? Tighten stop losses
   - Few trades? Relax entry conditions

3. **Test variations:**
   - Change one parameter at a time
   - Run backtest for each variation
   - Compare results

4. **Avoid overfitting:**
   - Don't optimize for one specific time period
   - Test on multiple time ranges
   - Use out-of-sample data for validation

5. **Forward testing:**
   - After optimization, test on recent unseen data
   - If results are similar, strategy is robust

## Live Trading

⚠️ **WARNING:** Live trading involves real money. Always start with testnet and small amounts!

### Starting Live Trading

**Prerequisites:**
1. ✅ Strategy tested and optimized via backtesting
2. ✅ Using Binance testnet initially (`BINANCE_TESTNET=true`)
3. ✅ Safety limits configured appropriately
4. ✅ Sufficient capital in exchange account
5. ✅ Telegram notifications enabled

**Via Web Dashboard:**

1. Navigate to "Live Trading" page
2. Review current bot status (should be "Stopped")
3. Click "Start New Bot"
4. Configure bot parameters:
   ```
   Strategy: Select tested strategy
   Symbol: BTC/USDT
   Timeframe: 1h
   Initial Capital: $1000 (start small!)

   Safety Limits:
   Max Position Size: $100
   Max Daily Loss: 5%
   Max Daily Trades: 10
   Max Open Positions: 3
   ```
5. Review safety limits carefully
6. Acknowledge warning: "⚠️ This will execute real trades"
7. Click "Start Trading"

**Via Telegram:**

```
/start_bot 1
```

### Monitoring Active Trading

**Web Dashboard:**
- Real-time bot status (Running/Paused/Stopped)
- Current position details
- Unrealized P&L
- Trade history
- Safety status

**Telegram Notifications:**
- 📊 Position opened
- ✅ Position closed (profit)
- ❌ Position closed (loss)
- ⚠️ Safety limit approaching
- 🛑 Emergency stop triggered

**Check Status:**
```
/status      # Overall bot status
/position    # Current position details
/pnl         # Profit and loss summary
```

### Controlling the Bot

**Pause Trading:**
```
Web: Click "Pause" button
Telegram: /pause
```
- Stops opening new positions
- Keeps existing positions open
- Can be resumed later

**Resume Trading:**
```
Web: Click "Resume" button
Telegram: /resume
```
- Resumes normal operation

**Stop Trading:**
```
Web: Click "Stop" button
Telegram: /stop_trading
```
- Closes all open positions at market price
- Stops the bot completely
- Requires restart to trade again

**Emergency Stop:**
```
Web: Click "EMERGENCY STOP" button
Telegram: /emergency
```
- **Immediate stop of all trading**
- Closes all positions instantly
- Sets global stop flag
- Use only in critical situations

### Understanding Bot States

1. **Stopped:**
   - No trading activity
   - No positions open
   - Safe state

2. **Starting:**
   - Bot initializing
   - Connecting to exchange
   - Loading strategy

3. **Running:**
   - Actively monitoring markets
   - Opening/closing positions
   - Following strategy rules

4. **Paused:**
   - Not opening new positions
   - Monitoring existing positions
   - Can be resumed

5. **Stopping:**
   - Closing all positions
   - Finalizing trades
   - Preparing to stop

6. **Error:**
   - Something went wrong
   - Check logs
   - May need manual intervention

## Telegram Bot

The Telegram bot provides full control of the platform from your phone.

### Getting Started

1. Find your bot in Telegram (username from @BotFather)
2. Send `/start`
3. You should see the main menu

### Available Commands

**Basic Commands:**
```
/start       - Start bot and show main menu
/help        - Show all available commands
/menu        - Display main menu with buttons
```

**Information Commands:**
```
/status      - Show bot status and statistics
/position    - View current position details
/pnl         - Show profit and loss summary
/strategies  - List available strategies
```

**Trading Commands:**
```
/start_bot <strategy_id>  - Start live trading with strategy
/stop_trading             - Stop trading and close positions
/pause                    - Pause trading (keep positions)
/resume                   - Resume trading
/emergency                - Emergency stop (⚠️ critical)
```

**Backtest Commands:**
```
/run_backtest <strategy_id>  - Run backtest with strategy
/results [backtest_id]       - View backtest results
```

### Using Interactive Menus

The bot provides inline keyboard menus for easy navigation:

**Main Menu:**
- 📊 Status - Check bot status
- 💼 Position - View current position
- 💰 P&L - Check profits/losses
- 📈 Strategies - List strategies
- 🎯 Backtest - Run backtest
- ▶️ Start - Start trading
- ⏸️ Pause - Pause trading
- ⏹️ Stop - Stop trading
- 🛑 Emergency - Emergency stop

**Navigation:**
- Tap buttons to execute commands
- Use "🔙 Back" to return to previous menu
- Use "🏠 Main Menu" to return to main menu

### Notifications

Enable notifications in .env:
```env
TELEGRAM_ENABLE_NOTIFICATIONS=true
```

**You'll receive notifications for:**
- 📊 New position opened
- ✅ Position closed with profit
- ❌ Position closed with loss
- ⚠️ Safety limit warning (80% of limit reached)
- 🛑 Emergency stop triggered
- ❌ Error occurred

### Tips for Telegram Bot

1. **Security:**
   - Never share your bot token
   - Only authorized user IDs can use the bot
   - Enable `TELEGRAM_REQUIRE_AUTH=true`

2. **Convenience:**
   - Pin important messages (like bot status)
   - Create quick shortcuts for common commands
   - Enable notifications for important events

3. **Monitoring:**
   - Check `/status` regularly
   - Review `/pnl` daily
   - Monitor position details with `/position`

## Monitoring & Safety

### Safety Features

The platform includes multiple safety mechanisms:

**1. Position Limits:**
```
MAX_POSITION_SIZE_USD=1000     # Max $ per position
MAX_OPEN_POSITIONS=3           # Max concurrent positions
```

**2. Loss Limits:**
```
MAX_DAILY_LOSS_PERCENT=5.0     # Max loss per day
MAX_TOTAL_LOSS_PERCENT=20.0    # Max total drawdown
```

**3. Trade Frequency:**
```
MAX_DAILY_TRADES=10            # Prevent overtrading
```

**4. Capital Requirements:**
```
MIN_CAPITAL_USD=100            # Minimum capital to start
```

**5. Emergency Stop:**
- Manual trigger via Web/Telegram
- Automatic trigger on critical errors
- Global stop flag prevents all trading

### Monitoring Best Practices

**Daily Checklist:**
- [ ] Check bot status (running/stopped)
- [ ] Review open positions
- [ ] Check daily P&L
- [ ] Verify safety limits not exceeded
- [ ] Review error logs (if any)

**Weekly Review:**
- [ ] Analyze trade history
- [ ] Calculate win rate
- [ ] Review drawdown
- [ ] Compare to backtest results
- [ ] Adjust parameters if needed

**Monthly Analysis:**
- [ ] Calculate monthly returns
- [ ] Compare to benchmarks (BTC buy-and-hold)
- [ ] Review strategy performance
- [ ] Consider strategy optimization
- [ ] Update safety limits if needed

### Logs and Debugging

**View Logs:**
```bash
# Docker installation
docker-compose logs backend -f
docker-compose logs telegram_bot -f

# Manual installation
# Check app logs in console
```

**Log Levels:**
- **INFO:** Normal operations, trade executions
- **WARNING:** Safety limits approaching, non-critical issues
- **ERROR:** Failed trades, API errors, need attention
- **CRITICAL:** Emergency stops, system failures, immediate action required

**Common Log Messages:**
```
INFO: Position opened: BTC/USDT LONG @ 40000
INFO: Position closed: BTC/USDT +2.5% profit
WARNING: Daily loss limit approaching (80%)
ERROR: Failed to execute order: Insufficient balance
CRITICAL: Emergency stop triggered: Max daily loss exceeded
```

## Best Practices

### For Beginners

1. **Start with Testnet:**
   - Use Binance testnet for learning
   - Make mistakes without losing money
   - Get comfortable with the platform

2. **Understand the Strategy:**
   - Read strategy documentation
   - Run backtests on different time periods
   - Understand entry/exit conditions

3. **Use Small Amounts:**
   - Start with $100-500 when going live
   - Test with 1-2% of your total capital
   - Gradually increase as you gain confidence

4. **Conservative Settings:**
   - Tight stop losses (0.5-1%)
   - Small position sizes (5-10% of capital)
   - Low daily trade limit (5-10 trades)

5. **Monitor Closely:**
   - Check status several times per day
   - Enable Telegram notifications
   - Review all trades immediately

### For Advanced Users

1. **Multiple Strategies:**
   - Run different strategies simultaneously
   - Diversify across symbols
   - Balance aggressive and conservative strategies

2. **Parameter Optimization:**
   - Regular backtest analysis
   - A/B testing of parameter variations
   - Out-of-sample validation

3. **Risk Management:**
   - Portfolio-level risk limits
   - Correlation analysis between strategies
   - Dynamic position sizing based on volatility

4. **Performance Analysis:**
   - Track detailed metrics (Sharpe, Sortino, Calmar ratios)
   - Compare to benchmarks
   - Identify and fix weaknesses

5. **Automation:**
   - Use API for custom integrations
   - Automate reporting and alerts
   - Build custom analysis tools

### Common Mistakes to Avoid

1. **❌ Over-optimization:**
   - Don't fit strategy perfectly to historical data
   - Use out-of-sample testing
   - Accept that no strategy wins 100%

2. **❌ Ignoring Safety Limits:**
   - Always set appropriate stop losses
   - Respect daily loss limits
   - Don't disable safety features

3. **❌ Emotional Trading:**
   - Don't manually interfere with bot
   - Trust the strategy (if backtested well)
   - Don't revenge trade after losses

4. **❌ Poor Money Management:**
   - Don't risk more than 1-2% per trade
   - Don't use excessive leverage
   - Keep sufficient capital reserve

5. **❌ Neglecting Monitoring:**
   - Check bot daily at minimum
   - Review all trades
   - Act on warning signs quickly

## Getting Help

### Documentation

- [Installation Guide](INSTALLATION.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Strategy Examples](STRATEGY_EXAMPLES.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Security Best Practices](SECURITY.md)

### Support Channels

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Questions and community help
- **Telegram Community:** Real-time chat and support
- **API Docs:** http://localhost:8000/docs

### Troubleshooting

See [Installation Guide - Troubleshooting](INSTALLATION.md#troubleshooting) for common issues.

---

**Previous:** [Installation Guide](INSTALLATION.md) | **Next:** [Strategy Examples](STRATEGY_EXAMPLES.md)
