# Руководство разработчика

## Структура проекта

```
food-delivery-bot/
├── app/
│   ├── api/           # REST API endpoints
│   ├── handlers/      # Telegram handlers
│   ├── keyboards/     # Telegram keyboards
│   ├── middlewares/   # Aiogram middlewares
│   ├── models/        # SQLAlchemy models
│   ├── services/      # Business logic
│   ├── states/        # FSM states
│   ├── tasks/         # Celery tasks
│   ├── utils/         # Utilities
│   ├── bot.py         # Bot entry point
│   ├── config.py      # Configuration
│   ├── database.py    # Database setup
│   └── main.py        # API entry point
├── migrations/        # Alembic migrations
├── scripts/           # Utility scripts
├── tests/             # Test suite
└── docs/              # Documentation
```

## Настройка окружения разработки

### 1. Клонирование

```bash
git clone <repository-url>
cd food-delivery-bot
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env
```

### 5. Запуск с Docker

```bash
make up
make migrate
```

## Запуск тестов

```bash
make test
```

Или с coverage:
```bash
pytest --cov=app tests/
```

## Работа с миграциями

Создание миграции:
```bash
alembic revision --autogenerate -m "description"
```

Применение миграций:
```bash
alembic upgrade head
```

Откат миграции:
```bash
alembic downgrade -1
```

## Стандарты кода

### Именование

- `snake_case` для переменных и функций
- `PascalCase` для классов
- `UPPER_CASE` для констант

### Импорты

```python
# 1. Стандартная библиотека
import os
from datetime import datetime

# 2. Сторонние библиотеки
from aiogram import Router
from sqlalchemy import select

# 3. Локальные импорты
from app.config import settings
from app.models import User
```

### Типизация

Используйте type hints:

```python
from typing import Optional, List

async def get_user(user_id: int) -> Optional[User]:
    ...
```

## Архитектура

### Service Layer

Бизнес-логика в `app/services/`:

```python
class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_order(self, ...):
        # Business logic here
        pass
```

### Handlers

Тонкие handlers, толстые services:

```python
@router.message(Command("order"))
async def cmd_order(message: Message, session):
    service = OrderService(session)
    order = await service.create_order(...)
    await message.answer("Order created!")
```

## Отладка

### Логирование

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error occurred", exc_info=True)
```

### Точки останова

Используйте `pdb`:
```python
import pdb; pdb.set_trace()
```

## Полезные команды

```bash
# Форматирование кода
make format

# Проверка линтером
make lint

# Запуск конкретного теста
pytest tests/test_services.py::TestOrderService -v

# Подключение к БД
make psql

# Redis CLI
make redis-cli
```

## Внесение изменений

1. Создайте ветку: `git checkout -b feature/my-feature`
2. Внесите изменения
3. Запустите тесты: `make test`
4. Зафиксируйте: `git commit -m "Add feature"`
5. Отправьте: `git push origin feature/my-feature`
6. Создайте Pull Request
