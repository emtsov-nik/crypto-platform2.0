# Crypto Trading Platform 🚀

Full-featured cryptocurrency trading platform with backtesting, live trading, and Telegram bot integration.

[![Tests](https://github.com/emtsov-nik/crypto-trading-platform/workflows/Tests/badge.svg)](https://github.com/emtsov-nik/crypto-trading-platform/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

### 📊 Trading Core
- **Multiple Trading Strategies** - RSI + Bollinger Bands strategy included, easy to add custom strategies
- **Backtesting Engine** - Event-driven backtesting with detailed metrics (PnL, Sharpe Ratio, Win Rate, Drawdown)
- **Live Trading** - Real-time trading on Binance with comprehensive safety controls
- **Safety Manager** - Multi-layered risk management system with position limits and emergency stop

### 📈 Market Data
- Real-time market data from Binance
- Technical indicators (RSI, Bollinger Bands, SMA, EMA, MACD, ATR, VWAP)
- Multiple timeframes support (1m, 5m, 15m, 1h, 4h, 1d)
- Historical data fetching and caching with Redis

### 💻 User Interfaces
- **Web Dashboard** - React-based UI with TradingView charts and real-time updates
- **Telegram Bot** - Full control via Telegram with inline keyboards and notifications
- **REST API** - Complete FastAPI backend with interactive Swagger documentation

### 🛡️ Safety & Monitoring
- Position size limits
- Daily loss limits
- Trade frequency limits
- Emergency stop functionality
- Comprehensive logging and error handling
- User authentication for Telegram bot

### 🧪 Testing & Quality
- 66+ unit and integration tests
- 80%+ code coverage
- Automated CI/CD with GitHub Actions
- Linting, formatting, and security checks

## 🚀 Quick Start

Choose your preferred method:

### 🐳 Docker Desktop (Easiest - Recommended!)

**Best for: Windows, Mac, or anyone who wants the simplest setup**

```bash
./docker-start.sh
```

Then open http://localhost:3000

> See [DOCKER_DESKTOP_GUIDE.md](DOCKER_DESKTOP_GUIDE.md) for details

### ⚡ Automated Local Setup

**Best for: Linux developers who want local installation**

```bash
./setup.sh   # Install and configure everything
./run.sh     # Start the application
```

Then open http://localhost:5173

> See [QUICKSTART.md](QUICKSTART.md) for details

### 🔧 Manual Setup

#### Prerequisites

- Docker & Docker Compose OR
- Python 3.11+ and Node.js 18+ (for local development)
- Binance API keys ([Get them here](https://www.binance.com/en/my/settings/api-management))

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/emtsov-nik/crypto-trading-platform.git
cd crypto-trading-platform
```

2. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Binance API (get from Binance)
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_TESTNET=true  # Use testnet for testing!

# Telegram Bot (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_USER_IDS=your_telegram_id  # Get from @userinfobot
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- 🌐 Web UI: http://localhost:3000
- 📚 API Docs: http://localhost:8000/docs
- 💬 Telegram Bot: Search for your bot in Telegram (`/start`)
- ❤️ Health Check: http://localhost:8000/api/health

> **Note**: For local development without Docker, see [Local Development Setup](DEVELOPMENT_LOCAL.md)

## 📖 Documentation

### Getting Started
- [🐳 Docker Desktop Guide](DOCKER_DESKTOP_GUIDE.md) - **Easiest!** Works on Windows/Mac/Linux
- [⚡ Quick Start Guide](QUICKSTART.md) - Automated local setup in 5 minutes
- [🔧 Local Development Setup](DEVELOPMENT_LOCAL.md) - Manual setup without Docker
- [📋 Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions

### Using the Platform
- [User Guide](docs/USER_GUIDE.md) - How to use the platform
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Development setup and architecture
- [Strategy Examples](docs/STRATEGY_EXAMPLES.md) - How to create custom strategies
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger docs
- [Testing Guide](backend/tests/README.md) - Running and writing tests
- [Telegram Bot Guide](backend/telegram_bot/README.md) - Telegram bot setup

## 🏗️ Architecture

```
crypto-trading-platform/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   ├── strategies/   # Trading strategies
│   │   ├── backtesting/  # Backtest engine
│   │   └── trading/      # Live trading & safety
│   ├── telegram_bot/     # Telegram bot
│   └── tests/            # Test suite (66+ tests)
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Application pages
│   │   └── services/     # API client
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml    # Docker configuration
```

## 🎯 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** + **PostgreSQL** - ORM and database
- **Celery** + **Redis** - Async task queue and caching
- **ccxt** - Unified exchange API
- **pandas** + **numpy** - Data processing
- **ta** - Technical analysis indicators
- **python-telegram-bot** - Telegram integration

### Frontend
- **React 18** + **TypeScript** - UI framework
- **Vite** - Build tool
- **TanStack Query** - Server state management
- **TradingView Lightweight Charts** - Chart visualization
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

### Infrastructure
- **PostgreSQL 15** - Relational database
- **Redis 7** - Cache and message broker
- **Docker** + **Docker Compose** - Containerization
- **GitHub Actions** - CI/CD automation

## 📊 Project Status

### ✅ Completed Phases

- ✅ **Phase 1:** Infrastructure (Docker, PostgreSQL, Redis, FastAPI, React)
- ✅ **Phase 2:** Market Data (Binance integration, indicators)
- ✅ **Phase 3:** Strategy System (BaseStrategy, RSI+BB strategy)
- ✅ **Phase 4:** Backtesting Engine (Event-driven, metrics, visualization)
- ✅ **Phase 5:** Live Trading (LiveTradingEngine, SafetyManager)
- ✅ **Phase 6:** Telegram Bot (Commands, inline keyboards, notifications)
- ✅ **Phase 7:** Testing & CI/CD (66+ tests, GitHub Actions)
- 🔄 **Phase 8:** Documentation & Deployment (In Progress)

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Database
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=trading_db

# Redis
REDIS_URL=redis://redis:6379/0

# Binance API
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_TESTNET=true

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
TELEGRAM_REQUIRE_AUTH=true

# Security
SECRET_KEY=your_secret_key_min_32_chars
ENVIRONMENT=development
DEBUG=true
```

See [.env.example](.env.example) for complete configuration options.

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit -v

# Run only integration tests
pytest tests/integration -v

# Run specific test markers
pytest -m strategy    # Strategy tests
pytest -m backtest    # Backtest tests
pytest -m safety      # Safety manager tests
```

Coverage report: `backend/htmlcov/index.html`

## 📈 Usage Examples

### 1. Creating a Custom Strategy

```python
from app.strategies.base_strategy import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def initialize(self):
        self.indicator_period = self.params.get('period', 14)

    def generate_signal(self, df: pd.DataFrame, index: int) -> str:
        if index < self.indicator_period:
            return None

        # Your custom trading logic
        current_price = df.iloc[index]['close']
        indicator_value = df.iloc[index]['my_indicator']

        if indicator_value > 70:
            return 'short'
        elif indicator_value < 30:
            return 'long'

        return None

    def calculate_position_size(self, capital: float, price: float) -> float:
        position_percent = self.params.get('position_size_percent', 10)
        return (capital * position_percent / 100) / price

    def calculate_tp_sl(self, entry_price: float, side: str):
        tp_percent = self.params.get('tp_percent', 2.0)
        sl_percent = self.params.get('sl_percent', 1.0)

        if side == 'long':
            tp = entry_price * (1 + tp_percent / 100)
            sl = entry_price * (1 - sl_percent / 100)
        else:
            tp = entry_price * (1 - tp_percent / 100)
            sl = entry_price * (1 + sl_percent / 100)

        return tp, sl
```

### 2. Running a Backtest via API

```bash
curl -X POST "http://localhost:8000/api/backtests/run" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": 1,
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "initial_capital": 10000,
    "start_date": "2024-01-01",
    "end_date": "2024-03-01"
  }'
```

### 3. Telegram Bot Commands

```
Basic Commands:
/start - Start the bot and show main menu
/help - Show all available commands
/menu - Display main menu

Trading Commands:
/status - Show bot status and statistics
/position - View current position details
/pnl - Show profit and loss summary
/start_bot <strategy_id> - Start live trading
/stop_trading - Stop the trading bot
/pause - Pause trading operations
/resume - Resume trading
/emergency - Emergency stop (⚠️ critical)

Strategy & Backtest:
/strategies - List available strategies
/run_backtest <strategy_id> - Run a backtest
/results [backtest_id] - View backtest results
```

### 4. Starting Live Trading via Web UI

1. Navigate to **Live Trading** page
2. Click **Start New Bot**
3. Select strategy and configure parameters:
   - Capital: $1000
   - Max Position Size: $100
   - Max Daily Loss: 5%
   - Max Daily Trades: 10
4. Confirm and start ⚠️ **Real money trading!**

## 🔐 Security

⚠️ **Important Security Notes:**

1. **API Keys:**
   - Never commit API keys to version control
   - Use `.env` file for sensitive data
   - Restrict API key permissions (no withdrawals)
   - Enable IP whitelisting on Binance

2. **Telegram Bot:**
   - Add your Telegram ID to `ALLOWED_USER_IDS`
   - Enable `REQUIRE_AUTH=true`
   - Never share your bot token

3. **Production:**
   - Use strong `SECRET_KEY` (min 32 characters)
   - Set `BINANCE_TESTNET=false` only when ready
   - Enable HTTPS/SSL
   - Configure firewall rules
   - Regular security audits

4. **Trading:**
   - Start with testnet
   - Use small capital initially
   - Set conservative safety limits
   - Monitor logs regularly

See [docs/SECURITY.md](docs/SECURITY.md) for detailed security guidelines.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Run tests
cd backend
pytest
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Write/update tests
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add AmazingFeature'`)
7. Push to branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This software is for educational purposes only.**

- **Trading cryptocurrencies involves substantial risk of loss**
- Past performance is not indicative of future results
- The developers are not responsible for any financial losses
- Use at your own risk
- Always test on testnet first
- Start with small amounts

## 🙏 Acknowledgments

- [ccxt](https://github.com/ccxt/ccxt) - Cryptocurrency exchange integration
- [TradingView](https://www.tradingview.com/) - Charting library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram bot framework
- [React](https://react.dev/) - UI library
- [Binance](https://www.binance.com/) - Cryptocurrency exchange

## 📞 Support & Community

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/emtsov-nik/crypto-trading-platform/issues)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/emtsov-nik/crypto-trading-platform/discussions)
- 📖 **Documentation:** [Full Docs](docs/)
- 💬 **Telegram:** [@CryptoTradingPlatform](https://t.me/your_community_channel)

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ All 7 phases completed
- ✅ Production-ready infrastructure
- ✅ Comprehensive testing
- ✅ Full documentation

### Future Versions

**v1.1 - Advanced Features:**
- [ ] WebSocket for real-time updates
- [ ] Multiple exchange support
- [ ] Portfolio management
- [ ] Advanced charting tools

**v2.0 - AI/ML Integration:**
- [ ] Machine learning strategies
- [ ] Sentiment analysis
- [ ] Price prediction models
- [ ] Automated strategy optimization

**v3.0 - Enterprise Features:**
- [ ] Multi-user support
- [ ] Role-based access control
- [ ] Advanced reporting
- [ ] Mobile app (iOS/Android)

## 📊 Project Statistics

- **Total Lines of Code:** ~15,000+
- **Backend:** ~10,000 lines
- **Frontend:** ~3,000 lines
- **Tests:** ~2,000 lines
- **Test Coverage:** 80%+
- **Test Cases:** 66+
- **Phases Completed:** 7/8
- **Commits:** 100+

---

<div align="center">

**Made with ❤️ by crypto traders, for crypto traders**

⭐ **Star this repository if you find it useful!** ⭐

[Report Bug](https://github.com/emtsov-nik/crypto-trading-platform/issues) · [Request Feature](https://github.com/emtsov-nik/crypto-trading-platform/discussions) · [Documentation](docs/)

</div>
