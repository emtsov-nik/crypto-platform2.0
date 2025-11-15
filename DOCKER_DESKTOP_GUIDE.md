# 🐳 Docker Desktop Guide

## Запуск с Docker Desktop (Windows/Mac/Linux)

Docker Desktop - это **САМЫЙ ПРОСТОЙ** способ запустить приложение!

### Преимущества Docker Desktop

✅ Не нужно устанавливать PostgreSQL, Redis, Python, Node.js
✅ Всё работает в изолированных контейнерах
✅ Одинаково работает на Windows, Mac, Linux
✅ Легко запускать и останавливать
✅ Автоматическое управление зависимостями

## 🚀 Quick Start

### 1. Установите Docker Desktop

**Windows/Mac:**
- Скачайте с https://www.docker.com/products/docker-desktop
- Установите и запустите Docker Desktop
- Убедитесь что Docker Desktop запущен (иконка в трее)

**Linux:**
```bash
# Docker уже установлен на большинстве систем
sudo systemctl start docker
sudo systemctl enable docker

# Или установите Docker Desktop для Linux
# https://docs.docker.com/desktop/install/linux-install/
```

### 2. Клонируйте репозиторий

```bash
git clone https://github.com/emtsov-nik/crypto-platform2.0.git
cd crypto-platform2.0
```

### 3. Создайте .env файл

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте (опционально для тестирования)
# nano .env  # или любой редактор
```

Минимальная конфигурация в `.env`:
```env
# Оставьте значения по умолчанию для тестирования
BINANCE_TESTNET=true

# Добавьте API ключи если хотите live данные
# BINANCE_API_KEY=your_key
# BINANCE_API_SECRET=your_secret
```

### 4. Запустите всё одной командой!

```bash
docker-compose up -d
```

Или используйте Docker Desktop GUI:
1. Откройте Docker Desktop
2. Найдите проект в списке
3. Нажмите "Start"

### 5. Откройте в браузере

```
http://localhost:3000
```

**Важно:** При запуске через Docker, frontend работает на порту **3000** (не 5173)!

## 📋 Доступные сервисы

После запуска `docker-compose up -d`:

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:3000 | Web интерфейс |
| Backend | http://localhost:8000 | API сервер |
| API Docs | http://localhost:8000/docs | Swagger документация |
| PostgreSQL | localhost:5432 | База данных |
| Redis | localhost:6379 | Кэш |

## 🎛️ Управление контейнерами

### Запуск

```bash
# Запустить все сервисы
docker-compose up -d

# Запустить только backend и зависимости
docker-compose up -d postgres redis backend

# Запустить с просмотром логов
docker-compose up
```

### Остановка

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (все данные!)
docker-compose down -v
```

### Перезапуск

```bash
# Перезапустить все
docker-compose restart

# Перезапустить только backend
docker-compose restart backend
```

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только frontend
docker-compose logs -f frontend

# Последние 100 строк
docker-compose logs --tail=100 backend
```

### Проверка статуса

```bash
# Список контейнеров
docker-compose ps

# Подробная информация
docker ps
```

## 🔧 Работа с Docker Desktop GUI

### В Docker Desktop вы можете:

1. **Запускать/останавливать сервисы**
   - Containers → trading_backend → Start/Stop

2. **Смотреть логи**
   - Кликните на контейнер → Logs tab

3. **Проверять ресурсы**
   - Вкладка Stats показывает CPU/Memory usage

4. **Открывать терминал**
   - Кликните на контейнер → CLI button
   - Или: `docker exec -it trading_backend /bin/bash`

5. **Проверять volumes**
   - Volumes tab показывает postgres_data и redis_data

## 🛠️ Development с Docker

### Hot Reload работает!

Оба сервиса поддерживают hot reload:
- **Backend**: Изменения в `backend/` автоматически перезагружают сервер
- **Frontend**: Изменения в `frontend/` обновляются в браузере

### Установка новых зависимостей

**Backend (Python):**
```bash
# Войти в контейнер
docker exec -it trading_backend /bin/bash

# Установить пакет
pip install new-package

# Добавить в requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Выйти и пересобрать
exit
docker-compose build backend
docker-compose up -d backend
```

**Frontend (npm):**
```bash
# Войти в контейнер
docker exec -it trading_frontend /bin/sh

# Установить пакет
npm install new-package

# Выйти и перезапустить
exit
docker-compose restart frontend
```

### Запуск тестов

```bash
# Backend тесты
docker exec -it trading_backend pytest

# С покрытием
docker exec -it trading_backend pytest --cov=app

# Конкретный тест
docker exec -it trading_backend pytest tests/test_market.py
```

### Подключение к базе данных

```bash
# Через Docker
docker exec -it trading_postgres psql -U trading_user -d trading_db

# Через localhost (если PostgreSQL установлен локально)
psql -h localhost -U trading_user -d trading_db
```

### Миграции базы данных

```bash
# Создать новую миграцию
docker exec -it trading_backend alembic revision --autogenerate -m "description"

# Применить миграции
docker exec -it trading_backend alembic upgrade head

# Откатить миграцию
docker exec -it trading_backend alembic downgrade -1
```

## 🐛 Troubleshooting

### Порт уже занят

**Ошибка:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Решение:**
```bash
# Найти процесс использующий порт
lsof -ti:8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Убить процесс или изменить порт в .env
echo "BACKEND_PORT=8001" >> .env
docker-compose up -d
```

### Контейнер падает при старте

**Проверьте логи:**
```bash
docker-compose logs backend
```

**Частые причины:**
- База данных не готова → подождите 10-20 секунд
- Ошибка в коде → проверьте последние изменения
- Нехватка памяти → увеличьте в Docker Desktop Settings

### Frontend показывает Network Error

**1. Проверьте что backend запущен:**
```bash
docker-compose ps
# backend должен быть "Up"
```

**2. Проверьте логи backend:**
```bash
docker-compose logs backend
```

**3. Проверьте здоровье API:**
```bash
curl http://localhost:8000/api/health
# Должно вернуть: {"status":"ok"}
```

**4. Перезапустите контейнеры:**
```bash
docker-compose restart backend frontend
```

### База данных пуста после перезапуска

**Проблема:** Вы использовали `docker-compose down -v`

**Решение:** Не используйте флаг `-v` если хотите сохранить данные!
```bash
# Правильно:
docker-compose down

# Неправильно (удалит все данные):
docker-compose down -v
```

### Медленная работа на Windows/Mac

**Причина:** Docker на Windows/Mac использует виртуализацию

**Решения:**
1. Увеличьте ресурсы в Docker Desktop Settings
   - Memory: минимум 4GB, рекомендуется 8GB
   - CPU: минимум 2 cores, рекомендуется 4

2. Используйте WSL 2 backend (Windows)
   - Settings → General → Use WSL 2

3. Отключите ненужные сервисы
   ```bash
   # Запустить только необходимое
   docker-compose up -d postgres redis backend frontend
   ```

### Не устанавливаются npm пакеты

```bash
# Очистить node_modules и пересобрать
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### Пересборка всего проекта

```bash
# Остановить всё
docker-compose down

# Удалить образы
docker-compose rm -f

# Пересобрать без кэша
docker-compose build --no-cache

# Запустить заново
docker-compose up -d
```

## 📊 Мониторинг

### Использование ресурсов

```bash
# Статистика контейнеров
docker stats

# Docker Desktop GUI → вкладка Stats
```

### Проверка здоровья сервисов

```bash
# Статус всех контейнеров
docker-compose ps

# Проверка health checks
docker inspect trading_postgres | grep Health -A 10
```

## 🔄 Обновление

### Получить последние изменения

```bash
# Остановить контейнеры
docker-compose down

# Получить обновления из git
git pull

# Пересобрать образы (если были изменения в Dockerfile/requirements)
docker-compose build

# Запустить
docker-compose up -d

# Применить миграции БД
docker exec -it trading_backend alembic upgrade head
```

## 💡 Полезные команды

```bash
# Показать все контейнеры (включая остановленные)
docker ps -a

# Показать образы
docker images

# Очистить неиспользуемые ресурсы
docker system prune

# Очистить всё (ОПАСНО! Удалит все volumes!)
docker system prune -a --volumes

# Просмотр конфигурации
docker-compose config

# Только проверить compose файл (не запускать)
docker-compose config --quiet

# Показать переменные окружения
docker exec trading_backend env
```

## 🎯 Сравнение: Docker vs Локальная установка

| Характеристика | Docker Desktop | Локальная установка |
|---------------|----------------|---------------------|
| **Установка** | 1 команда | Множество команд |
| **Время установки** | 2-3 минуты | 10-30 минут |
| **Зависимости** | Не нужны | PostgreSQL, Redis, Python, Node.js |
| **Изоляция** | ✅ Полная | ❌ Нет |
| **Портативность** | ✅ Везде одинаково | ⚠️ Зависит от ОС |
| **Производительность** | ⚠️ Немного медленнее | ✅ Быстрее |
| **Использование ресурсов** | ⚠️ Больше RAM | ✅ Меньше RAM |
| **Отладка** | ⚠️ Сложнее | ✅ Проще |
| **Production** | ✅ Рекомендуется | ❌ Не рекомендуется |

## 🎉 Готово!

Теперь вы можете:
- ✅ Запускать приложение одной командой
- ✅ Не беспокоиться о зависимостях
- ✅ Легко останавливать и запускать сервисы
- ✅ Смотреть логи в реальном времени
- ✅ Работать одинаково на любой ОС

**Нужна помощь?**
- Проверьте [QUICKSTART.md](QUICKSTART.md) для альтернативных методов
- См. [README.md](README.md) для общей информации
- Откройте issue на GitHub
