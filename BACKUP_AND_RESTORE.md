# Руководство по резервному копированию

## Автоматическое резервное копирование

В production окружении бэкапы создаются автоматически:
- **Частота**: раз в день в 2:00 ночи
- **Хранение**: 7 дней (настраивается)
- **Формат**: PostgreSQL custom format + gzip
- **Отправка**: Telegram (если файл < 50MB)

## Ручное создание бэкапа

```bash
make backup
```

Или через Docker:
```bash
docker-compose -f docker-compose.prod.yml exec backup /app/scripts/backup/run_backup.sh
```

## Расположение бэкапов

Бэкапы хранятся в директории `./backups/`:
- `backup_food_delivery_20240205_020000.dump.gz`

## Восстановление из бэкапа

### Шаг 1: Остановка сервисов

```bash
make prod-down
```

### Шаг 2: Восстановление

```bash
make restore FILE=backup_food_delivery_20240205_020000.dump.gz
```

Или вручную:

```bash
# Копируем бэкап в контейнер
docker cp backup_file.dump.gz food_delivery_db_prod:/tmp/

# Восстанавливаем
docker-compose -f docker-compose.prod.yml exec postgres bash -c "
  gunzip /tmp/backup_file.dump.gz && 
  pg_restore -U food_delivery -d food_delivery --clean /tmp/backup_file.dump
"
```

### Шаг 3: Перезапуск

```bash
make prod
```

## Проверка целостности бэкапа

```bash
# Проверка gzip
gzip -t backup_file.dump.gz

# Проверка pg_restore
pg_restore --list backup_file.dump.gz
```

## Перенос на другой сервер

1. Создайте бэкап на старом сервере
2. Скопируйте файл на новый сервер:
   ```bash
   scp backup_file.dump.gz user@new-server:/path/
   ```
3. Разверните приложение на новом сервере
4. Восстановите бэкап

## Настройка бэкапов в Telegram

Укажите в `.env`:
```env
BACKUP_ENABLED=true
BACKUP_TG_CHAT_ID=-1001234567890
BACKUP_TG_THREAD_ID=123  # опционально
BACKUP_MAX_TG_MB=45
```

## Ротация бэкапов

Старые бэкапы удаляются автоматически по настройке `BACKUP_RETENTION_DAYS`.

## Устранение проблем

**Бэкап не создается:**
- Проверьте права на директорию `./backups`
- Проверьте подключение к PostgreSQL

**Файл слишком большой для Telegram:**
- Уменьшите `BACKUP_MAX_TG_MB`
- Файл останется локально

**Ошибка восстановления:**
- Убедитесь, что PostgreSQL запущен
- Проверьте целостность файла
