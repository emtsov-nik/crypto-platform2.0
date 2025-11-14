# Developer Guide

Technical guide for developers working on the Crypto Trading Platform.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Contributing](#contributing)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - TradingView Charts  - Strategy Management  - Live Control │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  - REST Endpoints  - Request Validation  - Authentication    │
└────┬──────────────────┬──────────────────┬─────────────────┘
     │                  │                  │
┌────▼──────┐  ┌───────▼────────┐  ┌─────▼────────┐
│ Services  │  │  Background    │  │  Telegram   │
│ Layer     │  │  Tasks         │  │  Bot         │
│           │  │  (Celery)      │  │             │
└────┬──────┘  └───────┬────────┘  └─────┬────────┘
     │                 │                  │
┌────▼─────────────────▼──────────────────▼───────────┐
│              Core Business Logic                     │
│  - Strategy Engine  - Backtest Engine  - Trading    │
│  - Safety Manager   - Market Data     - Indicators  │
└────┬──────────────────┬───────────────────────────┬─┘
     │                  │                           │
┌────▼─────┐  ┌────────▼─────────┐  ┌─────────────▼──┐
│PostgreSQL│  │     Redis         │  │  Binance API   │
│(Trades,  │  │(Cache, Queue)     │  │  (ccxt)        │
│Strategies│  │                   │  │                │
└──────────┘  └───────────────────┘  └────────────────┘
```

### Architecture Patterns

**1. Layered Architecture:**
- **API Layer:** Request handling, validation, authentication
- **Service Layer:** Business logic, orchestration
- **Domain Layer:** Core trading logic, strategies
- **Data Layer:** Database models, repositories

**2. Event-Driven Backtesting:**
- Candle-by-candle simulation
- Realistic order execution
- Position tracking and P&L calculation

**3. Strategy Pattern:**
- Abstract `BaseStrategy` class
- Concrete strategy implementations
- Strategy registry and factory

**4. Safety-First Design:**
- Multiple safety checks before every trade
- Emergency stop mechanism
- Comprehensive logging and monitoring

## Tech Stack

### Backend

**Core Framework:**
- **FastAPI 0.104+** - Modern Python web framework
  - Automatic OpenAPI documentation
  - Type validation with Pydantic
  - Async support
  - Dependency injection

**Database:**
- **PostgreSQL 15** - Primary database
  - Stores strategies, backtests, trades
  - ACID compliance for critical data
- **SQLAlchemy 2.0** - ORM
  - Declarative models
  - Async support
  - Migration management (Alembic)

**Caching & Queuing:**
- **Redis 7** - In-memory data store
  - Market data caching
  - Celery message broker
  - Session storage
- **Celery** - Distributed task queue
  - Async backtest execution
  - Scheduled market data updates

**Trading:**
- **ccxt 4.0+** - Unified exchange API
  - Multi-exchange support
  - Order execution
  - Market data fetching
- **python-binance** - Binance-specific features

**Data Processing:**
- **pandas 2.0+** - Data manipulation
  - OHLCV data handling
  - Indicator calculation
- **numpy** - Numerical computations
- **ta** - Technical analysis indicators

**Telegram:**
- **python-telegram-bot 20.0+** - Bot framework
  - Async handlers
  - Inline keyboards
  - Notification system

**Testing:**
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting

### Frontend

**Core Framework:**
- **React 18** - UI library
  - Functional components
  - Hooks for state management
  - Context API
- **TypeScript 5** - Type safety
  - Strict type checking
  - Interface definitions

**Build Tools:**
- **Vite 5** - Fast build tool
  - Hot module replacement
  - Optimized production builds

**State Management:**
- **TanStack Query (React Query) 5** - Server state
  - Automatic caching
  - Background refetching
  - Optimistic updates

**UI & Styling:**
- **Tailwind CSS 3** - Utility-first CSS
  - Responsive design
  - Custom components
- **TradingView Lightweight Charts** - Financial charts
  - Candlestick charts
  - Technical indicators overlay

**HTTP Client:**
- **Axios** - Promise-based HTTP client
  - Request/response interceptors
  - Type-safe API calls

## Project Structure

```
crypto-trading-platform/
├── backend/                      # Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection
│   │   │
│   │   ├── api/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── health.py        # Health check endpoint
│   │   │   ├── market.py        # Market data endpoints
│   │   │   ├── strategies.py   # Strategy CRUD endpoints
│   │   │   ├── backtests.py    # Backtest endpoints
│   │   │   └── trading.py      # Live trading control
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py     # Strategy model
│   │   │   ├── backtest.py     # Backtest model
│   │   │   ├── trade.py        # Trade model
│   │   │   └── bot_state.py    # Bot state model
│   │   │
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py     # Strategy request/response
│   │   │   ├── backtest.py     # Backtest request/response
│   │   │   └── trading.py      # Trading request/response
│   │   │
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── market_data.py  # Market data service
│   │   │   ├── strategy_service.py
│   │   │   ├── backtest_service.py
│   │   │   └── trading_service.py
│   │   │
│   │   ├── strategies/          # Trading strategies
│   │   │   ├── __init__.py
│   │   │   ├── base_strategy.py        # Abstract base
│   │   │   ├── rsi_bb_strategy.py     # RSI + BB strategy
│   │   │   └── strategy_registry.py   # Strategy factory
│   │   │
│   │   ├── backtesting/         # Backtesting engine
│   │   │   ├── __init__.py
│   │   │   └── backtest_engine.py     # Core engine
│   │   │
│   │   ├── trading/             # Live trading
│   │   │   ├── __init__.py
│   │   │   ├── live_trading_engine.py # Trading engine
│   │   │   └── safety_manager.py      # Safety system
│   │   │
│   │   └── utils/               # Utilities
│   │       ├── __init__.py
│   │       ├── indicators.py    # Technical indicators
│   │       └── logger.py        # Logging setup
│   │
│   ├── telegram_bot/            # Telegram bot
│   │   ├── __init__.py
│   │   ├── bot.py              # Main bot file
│   │   ├── config.py           # Bot configuration
│   │   ├── api_client.py       # Backend API client
│   │   ├── keyboards.py        # Inline keyboards
│   │   └── handlers/           # Command handlers
│   │       ├── __init__.py
│   │       ├── start.py        # Basic commands
│   │       ├── status.py       # Info commands
│   │       ├── trading.py      # Trading commands
│   │       ├── backtest.py     # Backtest commands
│   │       └── callbacks.py    # Button handlers
│   │
│   ├── tests/                   # Test suite
│   │   ├── conftest.py         # Pytest configuration
│   │   ├── unit/               # Unit tests
│   │   │   ├── test_strategies.py
│   │   │   ├── test_backtest_engine.py
│   │   │   └── test_safety_manager.py
│   │   └── integration/        # Integration tests
│   │       └── test_backtest_flow.py
│   │
│   ├── requirements.txt         # Python dependencies
│   ├── pytest.ini              # Pytest configuration
│   └── Dockerfile              # Backend container
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── main.tsx            # Application entry
│   │   ├── App.tsx             # Root component
│   │   │
│   │   ├── components/         # React components
│   │   │   ├── Layout.tsx      # Main layout
│   │   │   ├── Navbar.tsx      # Navigation bar
│   │   │   └── ...
│   │   │
│   │   ├── pages/              # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── Strategies.tsx
│   │   │   ├── Backtest.tsx
│   │   │   ├── LiveTrading.tsx
│   │   │   └── MarketData.tsx
│   │   │
│   │   ├── services/           # API clients
│   │   │   └── api.ts          # Axios instance & API calls
│   │   │
│   │   ├── types/              # TypeScript types
│   │   │   └── index.ts        # Type definitions
│   │   │
│   │   └── utils/              # Utilities
│   │       └── formatters.ts   # Data formatters
│   │
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── vite.config.ts          # Vite configuration
│   └── Dockerfile              # Frontend container
│
├── docs/                        # Documentation
│   ├── INSTALLATION.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── STRATEGY_EXAMPLES.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md
│
├── .github/
│   └── workflows/
│       ├── tests.yml           # CI/CD pipeline
│       └── deploy.yml          # Deployment workflow
│
├── docker-compose.yml           # Docker orchestration
├── .env.example                # Environment template
├── README.md                   # Project overview
├── CONTRIBUTING.md             # Contribution guidelines
└── LICENSE                     # MIT License
```

## Development Setup

### Prerequisites

```bash
# Check versions
python3 --version  # 3.11+
node --version     # 18+
docker --version   # 20.10+
git --version      # 2.30+
```

### Clone Repository

```bash
git clone https://github.com/emtsov-nik/crypto-trading-platform.git
cd crypto-trading-platform
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov pytest-asyncio black flake8 isort mypy

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install dev dependencies (if not in package.json)
npm install --save-dev @types/node @types/react
```

### Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations (when implemented)
# alembic upgrade head
```

### Environment Configuration

```bash
# Copy template
cp .env.example .env

# Edit for development
nano .env
```

**Development .env:**
```env
DATABASE_URL=postgresql://trading_user:password@localhost:5432/trading_db
REDIS_URL=redis://localhost:6379/0
BINANCE_TESTNET=true
DEBUG=true
ENVIRONMENT=development
```

### Running Services

**Backend:**
```bash
cd backend
source venv/bin/activate

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In separate terminal: Run Celery worker
celery -A app.celery_app worker --loglevel=info

# In separate terminal: Run Telegram bot
python -m telegram_bot.bot
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Backend Development

### Creating New API Endpoints

**1. Define Pydantic Schema (schemas/):**

```python
# schemas/example.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExampleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(..., gt=0)

class ExampleResponse(BaseModel):
    id: int
    name: str
    value: float
    created_at: datetime

    class Config:
        from_attributes = True
```

**2. Create Database Model (models/):**

```python
# models/example.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**3. Create Service Layer (services/):**

```python
# services/example_service.py
from sqlalchemy.orm import Session
from app.models.example import Example
from app.schemas.example import ExampleCreate
from typing import List, Optional

class ExampleService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ExampleCreate) -> Example:
        example = Example(**data.dict())
        self.db.add(example)
        self.db.commit()
        self.db.refresh(example)
        return example

    def get_all(self) -> List[Example]:
        return self.db.query(Example).all()

    def get_by_id(self, id: int) -> Optional[Example]:
        return self.db.query(Example).filter(Example.id == id).first()
```

**4. Create API Endpoint (api/):**

```python
# api/examples.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.example import ExampleCreate, ExampleResponse
from app.services.example_service import ExampleService

router = APIRouter()

@router.post("/", response_model=ExampleResponse, status_code=201)
def create_example(
    data: ExampleCreate,
    db: Session = Depends(get_db)
):
    """Create a new example."""
    service = ExampleService(db)
    return service.create(data)

@router.get("/", response_model=List[ExampleResponse])
def list_examples(db: Session = Depends(get_db)):
    """List all examples."""
    service = ExampleService(db)
    return service.get_all()

@router.get("/{example_id}", response_model=ExampleResponse)
def get_example(example_id: int, db: Session = Depends(get_db)):
    """Get example by ID."""
    service = ExampleService(db)
    example = service.get_by_id(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return example
```

**5. Register Router (main.py):**

```python
# main.py
from app.api import examples

app.include_router(
    examples.router,
    prefix="/api/examples",
    tags=["examples"]
)
```

### Creating New Strategy

**1. Extend BaseStrategy:**

```python
# strategies/my_strategy.py
from app.strategies.base_strategy import BaseStrategy
import pandas as pd
from typing import Optional, Tuple

class MyCustomStrategy(BaseStrategy):
    """My custom trading strategy."""

    def initialize(self):
        """Initialize strategy parameters."""
        self.period = self.params.get('period', 20)
        self.threshold = self.params.get('threshold', 0.5)

    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Generate trading signal.

        Args:
            df: DataFrame with OHLCV and indicators
            index: Current candle index

        Returns:
            'long', 'short', 'close', or None
        """
        if index < self.period:
            return None

        # Your signal logic here
        current_price = df.iloc[index]['close']
        indicator = df.iloc[index]['my_indicator']

        if self.position:
            # Check exit conditions
            if self._should_exit(df, index):
                return 'close'
        else:
            # Check entry conditions
            if indicator > self.threshold:
                return 'long'
            elif indicator < -self.threshold:
                return 'short'

        return None

    def calculate_position_size(
        self,
        capital: float,
        price: float
    ) -> float:
        """Calculate position size.

        Args:
            capital: Available capital
            price: Current price

        Returns:
            Position size in base currency
        """
        position_percent = self.params.get('position_size_percent', 10)
        size = (capital * position_percent / 100) / price
        return round(size, 8)

    def calculate_tp_sl(
        self,
        entry_price: float,
        side: str
    ) -> Tuple[float, float]:
        """Calculate take profit and stop loss.

        Args:
            entry_price: Entry price
            side: 'long' or 'short'

        Returns:
            (take_profit, stop_loss)
        """
        tp_percent = self.params.get('tp_percent', 2.0)
        sl_percent = self.params.get('sl_percent', 1.0)

        if side == 'long':
            tp = entry_price * (1 + tp_percent / 100)
            sl = entry_price * (1 - sl_percent / 100)
        else:
            tp = entry_price * (1 - tp_percent / 100)
            sl = entry_price * (1 + sl_percent / 100)

        return tp, sl

    def _should_exit(self, df: pd.DataFrame, index: int) -> bool:
        """Check if should exit position."""
        # Your exit logic
        return False
```

**2. Register Strategy:**

```python
# strategies/strategy_registry.py
from app.strategies.my_strategy import MyCustomStrategy

STRATEGY_REGISTRY = {
    "rsi_bb": RSIBBStrategy,
    "my_custom": MyCustomStrategy,  # Add here
}
```

### Adding Technical Indicators

```python
# utils/indicators.py
import pandas as pd
import ta

def add_my_indicator(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Add custom indicator to dataframe.

    Args:
        df: DataFrame with OHLCV data
        period: Calculation period

    Returns:
        DataFrame with added indicator column
    """
    df = df.copy()

    # Your indicator calculation
    df['my_indicator'] = calculate_indicator(df['close'], period)

    return df

def calculate_indicator(series: pd.Series, period: int) -> pd.Series:
    """Calculate indicator values."""
    # Implementation
    pass
```

### Async Operations

```python
# Example async service method
async def fetch_market_data_async(self, symbol: str) -> dict:
    """Fetch market data asynchronously."""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}") as response:
            return await response.json()

# Example async endpoint
@router.get("/async-example")
async def async_example():
    """Async endpoint example."""
    result = await some_async_operation()
    return result
```

### Error Handling

```python
# Custom exceptions
class TradingException(Exception):
    """Base trading exception."""
    pass

class InsufficientCapitalException(TradingException):
    """Raised when capital is insufficient."""
    pass

class SafetyLimitException(TradingException):
    """Raised when safety limit is exceeded."""
    pass

# Usage in endpoints
@router.post("/trade")
def execute_trade(data: TradeRequest):
    try:
        result = trading_service.execute(data)
        return result
    except InsufficientCapitalException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SafetyLimitException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Frontend Development

### Creating New Page

**1. Create Page Component:**

```typescript
// pages/MyPage.tsx
import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../services/api'

export default function MyPage() {
  const [data, setData] = useState<any[]>([])

  // Fetch data with React Query
  const { data: apiData, isLoading, error } = useQuery({
    queryKey: ['myData'],
    queryFn: async () => {
      const response = await api.get('/api/examples')
      return response.data
    },
    refetchInterval: 5000 // Refetch every 5 seconds
  })

  // Mutation example
  const createMutation = useMutation({
    mutationFn: async (newData: any) => {
      const response = await api.post('/api/examples', newData)
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['myData'] })
    }
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Page</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {apiData?.map(item => (
          <div key={item.id} className="p-4 border rounded">
            <h3>{item.name}</h3>
            <p>{item.value}</p>
          </div>
        ))}
      </div>

      <button
        onClick={() => createMutation.mutate({ name: 'Test', value: 123 })}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Create New
      </button>
    </div>
  )
}
```

**2. Add Route:**

```typescript
// App.tsx
import MyPage from './pages/MyPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="my-page" element={<MyPage />} />
          {/* ... other routes */}
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
```

**3. Add Navigation Link:**

```typescript
// components/Navbar.tsx
<Link to="/my-page" className="nav-link">
  My Page
</Link>
```

### TypeScript Types

```typescript
// types/index.ts
export interface Example {
  id: number
  name: string
  value: number
  created_at: string
}

export interface ExampleCreate {
  name: string
  value: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
```

### API Client

```typescript
// services/api.ts
import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API methods
export const exampleApi = {
  getAll: () => api.get<Example[]>('/api/examples'),
  getById: (id: number) => api.get<Example>(`/api/examples/${id}`),
  create: (data: ExampleCreate) => api.post<Example>('/api/examples', data),
  update: (id: number, data: Partial<Example>) =>
    api.put<Example>(`/api/examples/${id}`, data),
  delete: (id: number) => api.delete(`/api/examples/${id}`)
}
```

## Testing

See [backend/tests/README.md](../backend/tests/README.md) for comprehensive testing guide.

### Writing Unit Tests

```python
# tests/unit/test_my_feature.py
import pytest
from app.services.example_service import ExampleService

@pytest.mark.unit
class TestExampleService:
    def test_create_example(self, db_session):
        """Test creating an example."""
        service = ExampleService(db_session)
        data = ExampleCreate(name="Test", value=123.45)

        result = service.create(data)

        assert result.id is not None
        assert result.name == "Test"
        assert result.value == 123.45

    def test_get_all_examples(self, db_session, sample_examples):
        """Test getting all examples."""
        service = ExampleService(db_session)

        results = service.get_all()

        assert len(results) == len(sample_examples)
```

### Running Tests

```bash
# All tests
pytest

# Specific marker
pytest -m unit
pytest -m integration

# With coverage
pytest --cov=app --cov-report=html

# Specific file
pytest tests/unit/test_strategies.py -v

# Specific test
pytest tests/unit/test_strategies.py::TestRSIBBStrategy::test_signal_generation
```

## API Reference

Full interactive API documentation is available at http://localhost:8000/docs

### Key Endpoints

**Health:**
- `GET /api/health` - Health check

**Strategies:**
- `GET /api/strategies` - List all strategies
- `POST /api/strategies` - Create strategy
- `GET /api/strategies/{id}` - Get strategy by ID
- `PUT /api/strategies/{id}` - Update strategy
- `DELETE /api/strategies/{id}` - Delete strategy

**Backtests:**
- `POST /api/backtests/run` - Run backtest
- `GET /api/backtests` - List backtests
- `GET /api/backtests/{id}/results` - Get results
- `GET /api/backtests/{id}/trades` - Get trade history

**Trading:**
- `POST /api/trading/start` - Start trading bot
- `POST /api/trading/stop` - Stop trading
- `POST /api/trading/pause` - Pause trading
- `POST /api/trading/resume` - Resume trading
- `POST /api/trading/emergency-stop` - Emergency stop
- `GET /api/trading/status` - Get bot status

**Market Data:**
- `GET /api/market/ohlcv` - Get OHLCV data
- `GET /api/market/symbols` - List available symbols

## Database Schema

### Main Tables

**strategies:**
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50) NOT NULL,
    params JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**backtests:**
```sql
CREATE TABLE backtests (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    initial_capital NUMERIC(15, 2),
    final_capital NUMERIC(15, 2),
    total_trades INTEGER,
    win_rate NUMERIC(5, 2),
    profit_factor NUMERIC(10, 4),
    sharpe_ratio NUMERIC(10, 4),
    max_drawdown NUMERIC(10, 4),
    status VARCHAR(20) DEFAULT 'pending',
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**trades:**
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtests(id),
    bot_id INTEGER,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    entry_price NUMERIC(20, 8),
    exit_price NUMERIC(20, 8),
    quantity NUMERIC(20, 8),
    pnl NUMERIC(15, 2),
    pnl_percent NUMERIC(10, 4),
    entry_time TIMESTAMP WITH TIME ZONE,
    exit_time TIMESTAMP WITH TIME ZONE,
    exit_reason VARCHAR(50)
);
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

### Quick Start

1. Fork repository
2. Create feature branch
3. Make changes
4. Write tests
5. Run linters
6. Commit and push
7. Create pull request

### Code Style

**Python:**
```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Type check
mypy app/
```

**TypeScript:**
```bash
# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

---

**Previous:** [User Guide](USER_GUIDE.md) | **Next:** [Strategy Examples](STRATEGY_EXAMPLES.md)
