# API Reference

## Base URL

```
http://localhost/api/v1
```

## Authentication

API использует JWT токены для аутентификации.

### Получение токена

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

### Использование токена

```http
GET /orders
Authorization: Bearer <token>
```

## Endpoints

### Health

#### GET /health

Проверка работоспособности сервиса.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "ok",
    "database": "ok",
    "redis": "ok"
  }
}
```

### Menu

#### GET /menu/categories

Получить список категорий.

**Query Parameters:**
- `parent_id` (optional) - ID родительской категории
- `include_inactive` (optional) - включить неактивные

**Response:**
```json
[
  {
    "id": 1,
    "name": "Пицца",
    "description": "Итальянская пицца",
    "sort_order": 0,
    "is_active": true,
    "level": 1,
    "is_archived": false,
    "created_at": "2024-01-15T10:00:00"
  }
]
```

#### GET /menu/categories/{category_id}

Получить категорию по ID.

#### GET /menu/products

Получить список товаров.

**Query Parameters:**
- `category_id` (optional) - фильтр по категории
- `include_inactive` (optional) - включить неактивные
- `skip` (optional) - пагинация, количество пропускаемых
- `limit` (optional) - пагинация, количество на странице

#### GET /menu/products/{product_id}

Получить товар по ID.

### Orders

#### GET /orders

Получить список заказов (требуется авторизация).

**Query Parameters:**
- `status` (optional) - фильтр по статусу
- `user_id` (optional) - фильтр по пользователю
- `skip` (optional) - пагинация
- `limit` (optional) - пагинация

#### GET /orders/{order_id}

Получить заказ по ID (требуется авторизация).

#### POST /orders

Создать новый заказ.

**Request:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "modifiers": [{"name": "Большая", "price_adjustment": 100}]
    }
  ],
  "delivery_address": "ул. Ленина, 1",
  "delivery_phone": "+79123456789",
  "payment_method": "cash",
  "delivery_comment": "Позвоните за 10 минут"
}
```

#### GET /orders/{order_number}/status

Проверить статус заказа (публичный).

**Response:**
```json
{
  "order_number": "20240205-0001",
  "status": "IN_DELIVERY",
  "created_at": "2024-02-05T12:00:00"
}
```

### Settings

#### GET /settings

Получить настройки приложения.

#### GET /settings/payment-methods

Получить доступные способы оплаты.

**Response:**
```json
{
  "methods": [
    {"code": "cash", "name": "Наличные"},
    {"code": "card_courier", "name": "Картой курьеру"}
  ]
}
```

## Models

### OrderStatus

- `NEW` - Новый
- `CONFIRMED` - Подтвержден
- `PAID` - Оплачен
- `IN_PROGRESS` - Готовится
- `READY` - Готов
- `PACKED` - Упакован
- `ASSIGNED` - Назначен курьер
- `IN_DELIVERY` - В доставке
- `DELIVERED` - Доставлен
- `CANCELLED` - Отменен

### PaymentMethod

- `cash` - Наличные
- `card_courier` - Картой курьеру
- `transfer` - Перевод

## Error Codes

- `400` - Bad Request (неверные параметры)
- `401` - Unauthorized (требуется авторизация)
- `403` - Forbidden (нет доступа)
- `404` - Not Found (ресурс не найден)
- `422` - Validation Error (ошибка валидации)
- `500` - Internal Server Error (внутренняя ошибка)

## Rate Limiting

API имеет ограничение на количество запросов:
- 100 запросов в минуту для анонимных пользователей
- 1000 запросов в минуту для авторизованных пользователей
