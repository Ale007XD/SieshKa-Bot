# Руководство по развертыванию

## Системные требования

- **OS**: Linux (Ubuntu 20.04+), macOS, или Windows с WSL2
- **RAM**: минимум 2GB (рекомендуется 4GB)
- **Disk**: минимум 10GB свободного места
- **Docker**: 20.10+ и Docker Compose 2.0+

## Подготовка к развертыванию

### 1. Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# macOS
# Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop
```

### 2. Получение Telegram Bot Token

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 3. Получение вашего Telegram ID

1. Откройте [@userinfobot](https://t.me/userinfobot) в Telegram
2. Бот покажет ваш ID
3. Сохраните его для настройки администратора

## Развертывание Production

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd food-delivery-bot
```

### Шаг 2: Настройка окружения

Создайте файл `.env`:

```bash
cp .env.example .env
nano .env  # или используйте ваш редактор
```

Заполните обязательные переменные:

```env
# Обязательные
BOT_TOKEN=your_bot_token_here
POSTGRES_USER=food_delivery
POSTGRES_PASSWORD=generate_strong_password
POSTGRES_DB=food_delivery
SECRET_KEY=generate_random_string_min_32_chars
ADMIN_TELEGRAM_IDS=your_telegram_id,another_admin_id
TIMEZONE=Europe/Moscow

# Базы данных
DATABASE_URL=postgresql+asyncpg://food_delivery:password@postgres:5432/food_delivery
REDIS_URL=redis://redis:6379/0

# Бэкапы (опционально)
BACKUP_ENABLED=true
BACKUP_TG_CHAT_ID=-1001234567890  # ID группы для бэкапов
BACKUP_MAX_TG_MB=45
```

### Шаг 3: Запуск приложения

```bash
# Сборка и запуск
make prod-build
make prod

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps
```

### Шаг 4: Создание администратора

```bash
make create-admin TELEGRAM_ID=your_telegram_id
```

### Шаг 5: Проверка работоспособности

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Должно появиться приветственное сообщение и меню

## Обновление приложения

```bash
# Получение обновлений
git pull

# Пересборка и перезапуск
make prod-down
make prod-build
make prod
```

## Мониторинг

### Просмотр логов

```bash
# Все сервисы
make prod-logs

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f api
```

### Проверка здоровья

```bash
# Health check API
curl http://localhost/api/v1/health
```

## Резервное копирование

См. [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md)

## Откат изменений

```bash
# Остановка
make prod-down

# Восстановление из бэкапа
make restore FILE=backup_file.dump.gz

# Перезапуск
make prod
```

## SSL/TLS (рекомендуется)

Для production рекомендуется настроить HTTPS:

1. Получите сертификат (Let's Encrypt):
```bash
certbot certonly --standalone -d your-domain.com
```

2. Настройте nginx для использования SSL
3. Обновите docker-compose.prod.yml

## Масштабирование

Для увеличения производительности:

1. Увеличьте количество worker'ов API:
```yaml
# docker-compose.prod.yml
api:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 8
```

2. Увеличьте ресурсы сервера
3. Настройте репликацию PostgreSQL (для высокой нагрузки)

## Безопасность

- Не храните `.env` файл в git
- Используйте сложные пароли
- Ограничьте доступ к портам через firewall
- Регулярно обновляйте зависимости
- Настройте fail2ban для защиты от брутфорса

## Поддержка

При проблемах смотрите [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
