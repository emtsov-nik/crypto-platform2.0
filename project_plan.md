# План разработки проекта бэктестинга и live-торговли криптовалютными стратегиями

## 1. Обзор проекта

### Цель
Создание платформы для тестирования и запуска торговых стратегий на фьючерсном рынке Binance с визуализацией результатов и управлением через веб-интерфейс и Telegram-бота.

### Ключевые возможности
- Бэктестинг стратегий на исторических данных
- Визуализация входов/выходов, стоп-лоссов и тейк-профитов на графиках
- Выбор различных таймфреймов (1m, 5m, 15m, 1h, 4h, 1d)
- Управление через веб-интерфейс и Telegram
- Live-торговля в реальном времени
- Управление рисками и позициями

---

## 2. Архитектура системы

### 2.1 Технологический стек

#### Backend
- **Python 3.11+**
- **FastAPI** - REST API и WebSocket для real-time данных
- **SQLAlchemy + PostgreSQL** - хранение данных (сделки, состояние бота)
- **Redis** - кеширование и очереди задач
- **Celery** - фоновые задачи (бэктестинг, live-торговля)
- **ccxt** - унифицированный API для Binance
- **python-binance** - специализированная библиотека для Binance
- **pandas** - обработка данных
- **numpy** - вычисления
- **ta** или **pandas-ta** - технические индикаторы

#### Frontend
- **React 18+** с TypeScript
- **Vite** - сборка
- **TradingView Lightweight Charts** - графики
- **TanStack Query** - управление состоянием сервера
- **Zustand** - локальное состояние
- **Tailwind CSS + shadcn/ui** - UI компоненты
- **Socket.io-client** - real-time обновления

#### Telegram Bot
- **python-telegram-bot** - взаимодействие с Telegram API
- Интеграция с основным backend через API

#### Infrastructure
- **Docker + Docker Compose** - контейнеризация
- **Nginx** - reverse proxy
- **Prometheus + Grafana** - мониторинг (опционально)

---

## 3. Структура проекта

```
crypto-trading-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI приложение
│   │   ├── config.py                  # Конфигурация
│   │   ├── database.py                # Подключение к БД
│   │   ├── models/                    # SQLAlchemy модели
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py
│   │   │   ├── backtest.py
│   │   │   ├── trade.py
│   │   │   └── bot_state.py
│   │   ├── schemas/                   # Pydantic схемы
│   │   │   ├── __init__.py
│   │   │   ├── strategy.py
│   │   │   ├── backtest.py
│   │   │   └── trade.py
│   │   ├── api/                       # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── strategies.py
│   │   │   ├── backtests.py
│   │   │   ├── trading.py
│   │   │   └── websocket.py
│   │   ├── services/                  # Бизнес-логика
│   │   │   ├── __init__.py
│   │   │   ├── binance_service.py     # Работа с Binance API
│   │   │   ├── backtest_engine.py     # Движок бэктестинга
│   │   │   ├── strategy_executor.py   # Выполнение стратегии
│   │   │   ├── live_trading.py        # Live торговля
│   │   │   ├── data_fetcher.py        # Получение данных
│   │   │   └── indicators.py          # Технические индикаторы
│   │   ├── strategies/                # Торговые стратегии
│   │   │   ├── __init__.py
│   │   │   ├── base_strategy.py       # Базовый класс
│   │   │   ├── rsi_bb_strategy.py     # Ваша стратегия
│   │   │   └── strategy_loader.py     # Загрузчик стратегий
│   │   ├── utils/                     # Утилиты
│   │   │   ├── __init__.py
│   │   │   ├── calculations.py
│   │   │   └── validators.py
│   │   └── celery_app.py              # Celery конфигурация
│   ├── telegram_bot/
│   │   ├── __init__.py
│   │   ├── bot.py                     # Главный файл бота
│   │   ├── handlers/                  # Обработчики команд
│   │   │   ├── __init__.py
│   │   │   ├── start.py
│   │   │   ├── strategy.py
│   │   │   ├── trading.py
│   │   │   └── status.py
│   │   └── keyboards.py               # Клавиатуры
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_backtest.py
│   │   ├── test_strategies.py
│   │   └── test_api.py
│   ├── alembic/                       # Миграции БД
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chart/
│   │   │   │   ├── TradingChart.tsx   # График с отметками
│   │   │   │   └── ChartControls.tsx
│   │   │   ├── Strategy/
│   │   │   │   ├── StrategyEditor.tsx
│   │   │   │   ├── StrategyList.tsx
│   │   │   │   └── StrategyUploader.tsx
│   │   │   ├── Backtest/
│   │   │   │   ├── BacktestPanel.tsx
│   │   │   │   ├── BacktestResults.tsx
│   │   │   │   └── BacktestStats.tsx
│   │   │   ├── Trading/
│   │   │   │   ├── LiveTradingPanel.tsx
│   │   │   │   ├── PositionInfo.tsx
│   │   │   │   └── OrderHistory.tsx
│   │   │   └── ui/                    # Переиспользуемые компоненты
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Strategies.tsx
│   │   │   ├── Backtest.tsx
│   │   │   └── LiveTrading.tsx
│   │   ├── hooks/
│   │   │   ├── useBacktest.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useTrades.ts
│   │   ├── services/
│   │   │   ├── api.ts                 # API клиент
│   │   │   └── websocket.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   └── chartHelpers.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 4. Детальный план разработки

### Фаза 1: Инфраструктура и базовая архитектура (1-2 недели)

#### Задачи:
1. **Настройка окружения**
   - Создание структуры проекта
   - Настройка Docker Compose (PostgreSQL, Redis, backend, frontend)
   - Конфигурация переменных окружения
   - Настройка git репозитория

2. **Backend: Базовая инфраструктура**
   - Инициализация FastAPI приложения
   - Настройка SQLAlchemy + PostgreSQL
   - Создание базовых моделей (Strategy, BotState, Trade, Backtest)
   - Настройка Alembic для миграций
   - Подключение Redis
   - Настройка Celery для фоновых задач

3. **Frontend: Базовая структура**
   - Создание React приложения с Vite
   - Настройка роутинга
   - Подключение UI библиотеки (shadcn/ui)
   - Создание базового layout

4. **Deliverables:**
   - Запускаемое приложение в Docker
   - Базовые API endpoints (health check)
   - Пустой frontend с роутингом

---

### Фаза 2: Получение и обработка данных (1-2 недели)

#### Задачи:
1. **Binance Integration**
   - Создать `BinanceService` для работы с API
   - Реализовать получение исторических данных (OHLCV)
   - Реализовать получение информации о символах
   - Добавить кеширование данных в Redis
   - Обработка ошибок и rate limits

2. **Технические индикаторы**
   - Создать модуль для расчета индикаторов
   - Реализовать: RSI, Bollinger Bands, Moving Averages, Volume
   - Создать pipeline для обработки данных с индикаторами

3. **API endpoints для данных**
   - `GET /api/symbols` - список доступных пар
   - `GET /api/klines` - получение OHLCV данных
   - `GET /api/indicators` - данные с индикаторами

4. **Frontend: Отображение графиков**
   - Интеграция TradingView Lightweight Charts
   - Компонент для отображения OHLCV
   - Выбор символа и таймфрейма
   - Загрузка и отображение данных

5. **Deliverables:**
   - Работающее получение данных с Binance
   - График с OHLCV данными
   - Выбор таймфрейма (1m, 5m, 15m, 1h, 4h, 1d)

---

### Фаза 3: Система стратегий (1-2 недели)

#### Задачи:
1. **Базовая архитектура стратегий**
   - Создать абстрактный класс `BaseStrategy`
   - Определить интерфейс стратегии (методы: initialize, signal, calculate_qty, etc.)
   - Создать систему для динамической загрузки стратегий

2. **Реализация вашей стратегии**
   - Портировать существующую стратегию на новую архитектуру
   - Добавить валидацию параметров
   - Создать конфигурационный файл для параметров

3. **API для стратегий**
   - `POST /api/strategies` - загрузка стратегии
   - `GET /api/strategies` - список стратегий
   - `GET /api/strategies/{id}` - детали стратегии
   - `PUT /api/strategies/{id}` - обновление параметров
   - `DELETE /api/strategies/{id}` - удаление

4. **Frontend: Управление стратегиями**
   - Страница со списком стратегий
   - Загрузка файла стратегии (.py)
   - Редактор параметров стратегии
   - Визуализация логики стратегии

5. **Deliverables:**
   - Работающая система загрузки и управления стратегиями
   - UI для работы со стратегиями
   - Сохранение стратегий в БД

---

### Фаза 4: Движок бэктестинга (2-3 недели)

#### Задачи:
1. **BacktestEngine**
   - Создать класс `BacktestEngine`
   - Реализовать event-driven архитектуру
   - Симуляция исполнения ордеров (market, limit)
   - Учет комиссий и слиппиджа
   - Управление позициями (усреднение, закрытие)
   - Расчет стоп-лосса и тейк-профита

2. **Метрики и статистика**
   - Total PnL, Win Rate, Sharpe Ratio
   - Maximum Drawdown
   - Average Trade Duration
   - Profit Factor
   - Количество сделок (выигрышных/проигрышных)

3. **Celery задачи**
   - Асинхронный запуск бэктестов
   - Прогресс-бар выполнения
   - Сохранение результатов в БД

4. **API для бэктестинга**
   - `POST /api/backtests` - запуск бэктеста
   - `GET /api/backtests/{id}` - результаты
   - `GET /api/backtests/{id}/trades` - список сделок
   - `GET /api/backtests/{id}/progress` - прогресс выполнения

5. **Frontend: Результаты бэктеста**
   - Запуск бэктеста с выбором параметров
   - Отображение статистики
   - График с отметками входов/выходов
   - Визуализация стоп-лоссов и тейк-профитов
   - Таблица сделок
   - Экспорт результатов

6. **Визуализация на графике**
   - Маркеры Long Entry (зеленый треугольник вверх)
   - Маркеры Short Entry (красный треугольник вниз)
   - Линии Stop Loss (красные пунктирные)
   - Линии Take Profit (зеленые пунктирные)
   - Прямоугольники для отображения позиций
   - Всплывающие подсказки с деталями сделок

7. **Deliverables:**
   - Полностью рабочий бэктестинг
   - Детальная визуализация на графиках
   - Сохранение и просмотр результатов

---

### Фаза 5: Live-торговля (2-3 недели)

#### Задачи:
1. **LiveTradingEngine**
   - Создать класс `LiveTradingEngine`
   - Real-time получение данных через WebSocket
   - Выполнение реальных ордеров через Binance API
   - Управление состоянием бота (BotState)
   - Система безопасности (max позиция, daily loss limit)

2. **Управление ордерами**
   - Размещение market/limit ордеров
   - Отслеживание статуса ордеров
   - Установка стоп-лоссов и тейк-профитов
   - Отмена ордеров
   - Управление margin и leverage

3. **Мониторинг и логирование**
   - Детальные логи всех операций
   - Уведомления о важных событиях
   - Отслеживание ошибок

4. **API для live-торговли**
   - `POST /api/trading/start` - запуск бота
   - `POST /api/trading/stop` - остановка бота
   - `POST /api/trading/pause` - пауза
   - `GET /api/trading/status` - текущий статус
   - `GET /api/trading/position` - текущая позиция
   - `GET /api/trading/orders` - активные ордера
   - WebSocket для real-time обновлений

5. **Frontend: Live-торговля**
   - Панель управления ботом (Start/Stop/Pause)
   - Real-time график с текущей позицией
   - Отображение текущих ордеров
   - История сделок
   - Статистика PnL
   - Алерты и уведомления

6. **Система безопасности**
   - Подтверждение перед запуском live-торговли
   - Emergency stop button
   - Автоматическая остановка при критических ошибках
   - Лимиты на максимальную позицию

7. **Deliverables:**
   - Рабочая live-торговля с real-time обновлениями
   - Безопасное управление позициями
   - UI для мониторинга и управления

---

### Фаза 6: Telegram Bot (1-2 недели)

#### Задачи:
1. **Базовая структура бота**
   - Настройка python-telegram-bot
   - Создание handlers для команд
   - Интеграция с backend API
   - Аутентификация пользователей

2. **Команды и функционал**
   - `/start` - приветствие и регистрация
   - `/status` - текущий статус бота
   - `/position` - информация о позиции
   - `/pnl` - прибыль/убыток
   - `/backtest` - запуск бэктеста
   - `/start_trading` - запуск live-торговли
   - `/stop_trading` - остановка торговли
   - `/pause` - пауза торговли
   - `/settings` - настройки

3. **Уведомления**
   - Уведомления о входе в позицию
   - Уведомления о выходе из позиции
   - Уведомления о срабатывании SL/TP
   - Алерты об ошибках
   - Ежедневная сводка

4. **Inline клавиатуры**
   - Управление ботом через кнопки
   - Быстрый доступ к функциям
   - Подтверждение критических операций

5. **Deliverables:**
   - Полностью функциональный Telegram бот
   - Интеграция со всеми функциями системы

---

### Фаза 7: Тестирование и оптимизация (1-2 недели)

#### Задачи:
1. **Unit тесты**
   - Тесты для стратегий
   - Тесты для backtest engine
   - Тесты для calculations
   - Тесты для API endpoints

2. **Integration тесты**
   - Полный цикл бэктеста
   - Полный цикл live-торговли
   - WebSocket соединения

3. **Нагрузочное тестирование**
   - Тестирование на больших объемах данных
   - Параллельные бэктесты
   - Оптимизация запросов к БД

4. **Оптимизация производительности**
   - Профилирование кода
   - Оптимизация расчетов индикаторов
   - Кеширование часто используемых данных
   - Оптимизация frontend (lazy loading, memoization)

5. **Bug fixing**
   - Исправление найденных багов
   - Улучшение обработки ошибок

6. **Deliverables:**
   - Стабильная работающая система
   - Покрытие тестами > 70%
   - Документация по найденным issues

---

### Фаза 8: Документация и deployment (1 неделя)

#### Задачи:
1. **Документация**
   - README с инструкциями по установке
   - API документация (Swagger/OpenAPI)
   - Руководство пользователя
   - Документация для разработчиков
   - Примеры стратегий

2. **Deployment**
   - Настройка production окружения
   - CI/CD pipeline (опционально)
   - Мониторинг и логирование
   - Backup стратегия

3. **Deliverables:**
   - Полная документация
   - Production-ready приложение

---

## 5. Детальная структура ключевых компонентов

### 5.1 BaseStrategy (базовый класс для стратегий)

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.validate_params()
    
    @abstractmethod
    def validate_params(self):
        """Валидация параметров стратегии"""
        pass
    
    @abstractmethod
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Добавление индикаторов к данным"""
        pass
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame, index: int) -> Optional[str]:
        """Генерация сигнала: 'long', 'short' или None"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, capital: float, price: float, 
                                step: int) -> float:
        """Расчет размера позиции"""
        pass
    
    @abstractmethod
    def calculate_exit_prices(self, avg_price: float, 
                             side: str) -> tuple[float, float]:
        """Расчет цен для TP и SL"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Метаданные стратегии"""
        return {
            "name": self.__class__.__name__,
            "params": self.params
        }
```

### 5.2 BacktestEngine (движок бэктестинга)

```python
class BacktestEngine:
    def __init__(self, strategy: BaseStrategy, data: pd.DataFrame,
                 initial_capital: float, fee_rate: float):
        self.strategy = strategy
        self.data = strategy.prepare_data(data)
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.fee_rate = fee_rate
        self.position = None
        self.trades = []
        self.equity_curve = []
    
    def run(self) -> Dict[str, Any]:
        """Запуск бэктеста"""
        for i in range(len(self.data)):
            self._process_bar(i)
        
        return self._calculate_metrics()
    
    def _process_bar(self, index: int):
        """Обработка одного бара"""
        # Проверка выходов (SL/TP)
        if self.position:
            self._check_exits(index)
        
        # Генерация нового сигнала
        if not self.position:
            signal = self.strategy.generate_signal(self.data, index)
            if signal:
                self._open_position(index, signal)
    
    def _open_position(self, index: int, side: str):
        """Открытие позиции"""
        pass
    
    def _close_position(self, index: int, reason: str):
        """Закрытие позиции"""
        pass
    
    def _check_exits(self, index: int):
        """Проверка условий выхода"""
        pass
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Расчет метрик"""
        return {
            "total_pnl": self.capital - self.initial_capital,
            "total_return_pct": ((self.capital / self.initial_capital) - 1) * 100,
            "num_trades": len(self.trades),
            "win_rate": self._calculate_win_rate(),
            "sharpe_ratio": self._calculate_sharpe(),
            "max_drawdown": self._calculate_max_drawdown(),
            "trades": self.trades
        }
```

### 5.3 LiveTradingEngine

```python
class LiveTradingEngine:
    def __init__(self, strategy: BaseStrategy, binance_service: BinanceService,
                 bot_state: BotState, config: Dict[str, Any]):
        self.strategy = strategy
        self.binance = binance_service
        self.state = bot_state
        self.config = config
        self.running = False
    
    async def start(self):
        """Запуск live-торговли"""
        self.running = True
        await self._subscribe_to_klines()
    
    async def stop(self):
        """Остановка торговли"""
        self.running = False
    
    async def _subscribe_to_klines(self):
        """Подписка на real-time данные"""
        pass
    
    async def _on_kline_update(self, kline: Dict):
        """Обработка нового бара"""
        if not self.running:
            return
        
        # Обновление данных
        # Генерация сигнала
        # Исполнение ордеров
        pass
    
    async def _execute_order(self, side: str, quantity: float):
        """Исполнение ордера"""
        pass
    
    async def _place_exit_orders(self):
        """Установка SL и TP"""
        pass
```

---

## 6. API Endpoints

### Strategies
- `GET /api/strategies` - список всех стратегий
- `POST /api/strategies` - создание/загрузка стратегии
- `GET /api/strategies/{id}` - детали стратегии
- `PUT /api/strategies/{id}` - обновление параметров
- `DELETE /api/strategies/{id}` - удаление стратегии

### Market Data
- `GET /api/symbols` - список торговых пар
- `GET /api/klines?symbol=BTCUSDT&timeframe=1h&start=...&end=...` - OHLCV данные

### Backtesting
- `POST /api/backtests` - запуск бэктеста
- `GET /api/backtests` - список бэктестов
- `GET /api/backtests/{id}` - результаты бэктеста
- `GET /api/backtests/{id}/trades` - сделки бэктеста
- `DELETE /api/backtests/{id}` - удаление результатов

### Live Trading
- `POST /api/trading/start` - запуск торговли
- `POST /api/trading/stop` - остановка
- `POST /api/trading/pause` - пауза
- `GET /api/trading/status` - текущий статус
- `GET /api/trading/position` - текущая позиция
- `GET /api/trading/orders` - активные ордера
- `GET /api/trading/history` - история сделок

### WebSocket
- `ws://api/ws/trading` - real-time обновления торговли
- `ws://api/ws/klines/{symbol}/{timeframe}` - real-time свечи

---

## 7. Модели данных (PostgreSQL)

### Strategy
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    params JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Backtest
```sql
CREATE TABLE backtests (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    initial_capital DECIMAL(20, 8),
    final_capital DECIMAL(20, 8),
    total_return DECIMAL(10, 4),
    num_trades INTEGER,
    win_rate DECIMAL(5, 2),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    results JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Trade
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtests(id),
    side VARCHAR(10) NOT NULL, -- 'long' or 'short'
    entry_time TIMESTAMP NOT NULL,
    entry_price DECIMAL(20, 8) NOT NULL,
    exit_time TIMESTAMP,
    exit_price DECIMAL(20, 8),
    quantity DECIMAL(20, 8) NOT NULL,
    pnl DECIMAL(20, 8),
    pnl_pct DECIMAL(10, 4),
    exit_reason VARCHAR(50), -- 'tp', 'sl', 'signal'
    fees DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### BotState
```sql
CREATE TABLE bot_states (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10), -- 'long', 'short', null
    steps_opened INTEGER DEFAULT 0,
    avg_price DECIMAL(20, 8),
    total_qty DECIMAL(20, 8),
    last_signal_ts BIGINT,
    paused BOOLEAN DEFAULT FALSE,
    is_live BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Order
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    bot_state_id INTEGER REFERENCES bot_states(id),
    binance_order_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'market', 'limit', 'stop_loss', etc.
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    status VARCHAR(20) NOT NULL, -- 'pending', 'filled', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    filled_at TIMESTAMP
);
```

---

## 8. Frontend структура страниц

### Dashboard
- Обзор активных стратегий
- Краткая статистика по бэктестам
- Статус live-торговли
- Recent trades

### Strategies Page
- Список загруженных стратегий
- Кнопка загрузки новой стратегии
- Редактирование параметров
- Удаление стратегий

### Backtest Page
- Выбор стратегии
- Настройка параметров бэктеста (символ, таймфрейм, даты, капитал)
- Кнопка запуска
- График с результатами
- Статистика
- Таблица сделок

### Live Trading Page
- Панель управления (Start/Stop/Pause)
- Real-time график
- Текущая позиция
- Активные ордера
- История сделок
- PnL статистика

---

## 9. Особенности реализации

### 9.1 Визуализация сделок на графике

Для отображения входов/выходов используйте TradingView Lightweight Charts:

```typescript
// Добавление маркеров
const markers = trades.map(trade => ({
  time: trade.entry_time,
  position: trade.side === 'long' ? 'belowBar' : 'aboveBar',
  color: trade.side === 'long' ? '#26a69a' : '#ef5350',
  shape: trade.side === 'long' ? 'arrowUp' : 'arrowDown',
  text: `${trade.side.toUpperCase()} @ ${trade.entry_price}`
}));

// Добавление линий SL/TP
const stopLossLine = {
  price: trade.stop_loss,
  color: '#ef5350',
  lineWidth: 2,
  lineStyle: 2, // dashed
  title: 'Stop Loss'
};

const takeProfitLine = {
  price: trade.take_profit,
  color: '#26a69a',
  lineWidth: 2,
  lineStyle: 2, // dashed
  title: 'Take Profit'
};
```

### 9.2 WebSocket для real-time обновлений

```python
# Backend
from fastapi import WebSocket

@app.websocket("/ws/trading")
async def trading_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Отправка обновлений
            data = {
                "type": "position_update",
                "position": current_position,
                "pnl": current_pnl
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except:
        pass
```

```typescript
// Frontend
const ws = new WebSocket('ws://localhost:8000/ws/trading');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'position_update') {
    updatePosition(data.position);
    updatePnL(data.pnl);
  }
};
```

### 9.3 Безопасность Binance API

```python
# Использование testnet для разработки
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true") == "true"

if BINANCE_TESTNET:
    client = Client(api_key, api_secret, testnet=True)
else:
    # Production keys с дополнительной проверкой
    client = Client(api_key, api_secret)

# IP whitelist
# Ограничение прав API ключа (только торговля, без вывода)
```

---

## 10. Конфигурация (.env файл)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trading_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Binance API
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_TESTNET=true

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Application
SECRET_KEY=your_secret_key
ENVIRONMENT=development
DEBUG=true

# Trading
MAX_POSITION_SIZE_USDT=1000
MAX_DAILY_LOSS_USDT=100
DEFAULT_LEVERAGE=1
```

---

## 11. Docker Compose конфигурация

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/trading_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/trading_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    command: celery -A app.celery_app worker --loglevel=info

  telegram_bot:
    build: ./backend
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./backend:/app
    command: python -m telegram_bot.bot

  frontend:
    build: ./frontend
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    command: npm run dev

volumes:
  postgres_data:
```

---

## 12. Приоритеты и рекомендации

### Высокий приоритет:
1. Надежная работа с Binance API (обработка ошибок, rate limits)
2. Точность бэктестинга (правильный учет комиссий, слиппиджа)
3. Безопасность live-торговли (лимиты, подтверждения)
4. Визуализация результатов на графиках

### Средний приоритет:
1. Telegram бот (можно добавить позже)
2. Оптимизация производительности
3. Расширенная статистика

### Низкий приоритет:
1. Мониторинг и алерты (Prometheus/Grafana)
2. CI/CD
3. Мультиязычность

---

## 13. Риски и меры по их снижению

### Риски:
1. **Изменения в Binance API** - использовать официальные библиотеки, следить за обновлениями
2. **Ошибки в бэктестинге** - тщательное тестирование, сравнение с известными результатами
3. **Потери в live-торговле** - начать с малых сумм, использовать testnet
4. **Перегрузка системы** - мониторинг, rate limiting
5. **Безопасность данных** - шифрование API ключей, secure storage

### Меры:
- Тестирование на testnet перед production
- Постепенное увеличение капитала
- Автоматические стоп-лоссы на уровне системы
- Регулярные backup'ы данных
- Логирование всех операций

---

## 14. Следующие шаги

1. **Создать git репозиторий**
2. **Настроить базовую структуру проекта**
3. **Развернуть Docker окружение**
4. **Начать с Фазы 1: Инфраструктура**

Следуя этому плану, вы создадите полнофункциональную платформу для тестирования и запуска торговых стратегий. Время реализации: **8-12 недель** при работе в одиночку, или **4-6 недель** с командой из 2-3 разработчиков.

Успехов в разработке! 🚀
