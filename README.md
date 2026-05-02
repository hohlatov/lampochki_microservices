# Лампочки — микросервисы

Два независимых микросервиса на FastAPI + SQLite.

```
lampochki/
├── products_service/   # порт 8000
│   ├── main.py         # HTTP-слой (роуты)
│   ├── service.py      # бизнес-логика
│   ├── crud.py         # работа с БД
│   ├── models.py       # SQLAlchemy-модели
│   ├── schemas.py      # Pydantic-схемы
│   ├── database.py     # подключение к БД
│   └── requirements.txt
└── orders_service/     # порт 8001
    ├── main.py
    ├── service.py      # бизнес-логика + взаимодействие с products_service
    ├── crud.py
    ├── models.py
    ├── schemas.py
    ├── database.py
    ├── products_client.py  # HTTP-клиент для products_service
    └── requirements.txt
```

---

## Запуск

Сначала запустить products_service, затем orders_service.

```bash
# Терминал 1
cd products_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Терминал 2
cd orders_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Swagger UI:
- http://localhost:8000/docs — товары
- http://localhost:8001/docs — заказы

---

## Архитектура взаимодействия

При создании заказа (`POST /orders/`) orders_service:

1. Для каждого товара вызывает `GET /products/{id}` на порту 8000
2. Получает **реальную цену** и **название** из products_service (клиент не передаёт цену)
3. Проверяет `stock >= quantity`, иначе возвращает **409 Conflict**
4. Уменьшает остаток через `PATCH /internal/products/{id}/stock`
5. Сохраняет заказ с зафиксированной ценой на момент покупки

---

## Эндпоинты — товары (порт 8000)

| Метод  | URL                               | Описание                        |
|--------|-----------------------------------|---------------------------------|
| GET    | /products                         | Список всех товаров             |
| GET    | /products/{id}                    | Товар по ID                     |
| POST   | /products/                        | Создать товар                   |
| PUT    | /products/{id}                    | Обновить товар                  |
| DELETE | /products/{id}                    | Удалить товар                   |
| PATCH  | /internal/products/{id}/stock     | Изменить остаток (внутренний)   |
| GET    | /admin/products                   | Список товаров (админ)          |
| POST   | /admin/products                   | Добавить товар (админ)          |
| PUT    | /admin/products/{id}              | Изменить товар (админ)          |
| DELETE | /admin/products/{id}              | Удалить товар (админ)           |

---

## Эндпоинты — заказы (порт 8001)

| Метод  | URL                        | Описание                    |
|--------|----------------------------|-----------------------------|
| POST   | /orders/                   | Создать заказ               |
| GET    | /orders/                   | Список всех заказов         |
| GET    | /orders/{id}               | Заказ по ID                 |
| PUT    | /orders/{id}/status        | Изменить статус             |
| GET    | /admin/orders/             | Список заказов (админ)      |
| GET    | /admin/orders/{id}         | Детали заказа (админ)       |
| PUT    | /admin/orders/{id}/status  | Обновить статус (админ)     |

---

## Пример создания заказа

```json
POST http://localhost:8001/orders/
{
  "customer_name": "Иван Иванов",
  "customer_phone": "+7 900 000-00-00",
  "delivery_address": "Москва, ул. Ленина, д.1",
  "payment_method": "card",
  "items": [
    { "product_id": "<uuid товара>", "quantity": 2 },
    { "product_id": "<uuid товара>", "quantity": 1 }
  ]
}
```

Цена берётся автоматически из products_service.

---

## Статусы заказа

- `new`        — новый
- `processing` — в обработке
- `shipped`    — отправлен
- `delivered`  — доставлен
- `cancelled`  — отменён
