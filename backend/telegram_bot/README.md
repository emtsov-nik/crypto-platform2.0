# Telegram Bot

Telegram бот для управления торговой системой.

## Возможности

- 📊 Мониторинг статуса бота
- 💰 Просмотр текущих позиций и PnL
- 🚀 Управление live-торговлей (старт/стоп/пауза)
- 🔬 Запуск бэктестов
- 📋 Управление стратегиями
- ⚙️ Настройки безопасности

## Настройка

### 1. Создание бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните токен, который выдаст BotFather

### 2. Получение своего Telegram ID

1. Найдите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте `/start`
3. Сохраните ваш ID

### 3. Конфигурация

Добавьте в файл `.env`:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321  # Ваш Telegram ID (через запятую для нескольких)
TELEGRAM_REQUIRE_AUTH=true
TELEGRAM_ENABLE_NOTIFICATIONS=true
TELEGRAM_LOG_LEVEL=INFO
```

## Команды

### Базовые команды

- `/start` - Запуск бота и главное меню
- `/help` - Справка по командам
- `/menu` - Показать главное меню

### Торговые команды

- `/status` - Статус торгового бота
- `/position` - Текущая позиция
- `/pnl` - Прибыль и убыток
- `/start_bot <strategy_id>` - Запустить live-торговлю
- `/stop_trading` - Остановить бота
- `/pause` - Пауза торговли
- `/resume` - Возобновить торговлю
- `/emergency` - Экстренная остановка ⚠️

### Команды стратегий

- `/strategies` - Список доступных стратегий
- `/backtest` - Меню бэктеста
- `/run_backtest <strategy_id>` - Запустить бэктест
- `/results [backtest_id]` - Просмотр результатов

### Настройки

- `/settings` - Настройки бота

## Inline клавиатуры

Бот поддерживает удобные inline кнопки для всех основных операций. Используйте кнопки в меню для быстрого доступа к функциям.

## Безопасность

⚠️ **Важно:**

1. **Никогда не делитесь токеном бота** - это ключ доступа к вашему боту
2. **Добавьте свой Telegram ID в ALLOWED_USER_IDS** - только эти пользователи смогут управлять ботом
3. **Включите REQUIRE_AUTH=true** - для проверки авторизации
4. **Будьте осторожны с командами live-торговли** - они работают с реальными деньгами!

## Запуск

### С Docker Compose

Бот автоматически запускается с остальными сервисами:

```bash
docker-compose up -d
```

### Отдельно (для разработки)

```bash
cd backend
python -m telegram_bot.bot
```

## Логи

Просмотр логов бота:

```bash
docker-compose logs -f telegram_bot
```

## Архитектура

```
telegram_bot/
├── __init__.py
├── bot.py                 # Главный файл бота
├── config.py              # Конфигурация
├── api_client.py          # Клиент для backend API
├── keyboards.py           # Inline клавиатуры
├── handlers/              # Обработчики команд
│   ├── __init__.py
│   ├── start.py           # /start, /help
│   ├── status.py          # /status, /position, /pnl
│   ├── trading.py         # Команды управления торговлей
│   ├── backtest.py        # Команды бэктеста
│   └── callbacks.py       # Обработчики inline кнопок
└── README.md              # Эта документация
```

## Troubleshooting

### Бот не отвечает

1. Проверьте, что бот запущен: `docker-compose ps`
2. Проверьте логи: `docker-compose logs telegram_bot`
3. Убедитесь, что токен бота корректный
4. Проверьте, что ваш ID в ALLOWED_USER_IDS

### Ошибка "Access Denied"

- Добавьте свой Telegram ID в переменную окружения `TELEGRAM_ALLOWED_USER_IDS`
- Убедитесь, что перезапустили контейнер после изменений

### Backend недоступен

- Проверьте, что backend запущен: `docker-compose ps backend`
- Проверьте BACKEND_API_URL в конфигурации
- Убедитесь, что все сервисы в одной сети Docker

## Дальнейшее развитие

Планируемый функционал:

- 🔔 Автоматические уведомления о сделках
- 📊 Графики и визуализация в Telegram
- ⚡ WebSocket для real-time обновлений
- 📅 Ежедневные отчеты
- 🔐 Двухфакторная аутентификация для критических операций
