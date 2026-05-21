# Лампочки — микросервисы

Три независимых микросервиса на FastAPI + SQLite и панель управления (React).

```
lampochki_microservices/
├── auth_service/       # порт 8002 — JWT-аутентификация
├── products_service/   # порт 8000 — товары
└── orders_service/     # порт 8001 — заказы
```

---

## Запуск

Запустите все три сервиса, затем frontend.

```bash
# Терминал 1 — аутентификация
cd auth_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Терминал 2 — товары
cd products_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Терминал 3 — заказы
cd orders_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Терминал 4 — панель управления (frontend)
cd lampochki-frontend
npm install
npm run dev
```

Swagger UI:
- http://localhost:8002/docs — аутентификация
- http://localhost:8000/docs — товары
- http://localhost:8001/docs — заказы

Frontend: http://localhost:5173

---

## Учётные данные администратора

| Логин | Пароль   |
|-------|----------|
| admin | admin123 |

Вход: http://localhost:5173/login → панель http://localhost:5173/admin

---

## JWT и авторизация

1. **auth_service** (8002) — `POST /auth/login` или `POST /login` принимает `{ "login": "admin", "password": "admin123" }`, возвращает JWT.
2. **products_service** (8000) — все `/admin/products*` требуют заголовок `Authorization: Bearer <token>`.
3. **orders_service** (8001) — все `/admin/orders*` требуют тот же JWT.

Публичные эндпоинты (без токена):
- `GET /products`, `GET /products/{id}` — каталог
- `POST /orders/` — оформление заказа клиентом

---

## Эндпоинты — аутентификация (порт 8002)

| Метод | URL          | Описание              |
|-------|--------------|-----------------------|
| POST  | /login       | Получить JWT-токен    |
| POST  | /auth/login  | Получить JWT-токен    |

---

## Эндпоинты — товары (порт 8000)

| Метод  | URL                               | JWT | Описание                        |
|--------|-----------------------------------|-----|---------------------------------|
| GET    | /products                         | —   | Список всех товаров             |
| GET    | /products/{id}                    | —   | Товар по ID                     |
| PATCH  | /internal/products/{id}/stock     | —   | Изменить остаток (внутренний)   |
| GET    | /admin/products                   | ✓   | Список товаров (админ)          |
| POST   | /admin/products                   | ✓   | Добавить товар (админ)          |
| PUT    | /admin/products/{id}              | ✓   | Изменить товар (админ)          |
| DELETE | /admin/products/{id}              | ✓   | Удалить товар (админ)           |

---

## Эндпоинты — заказы (порт 8001)

| Метод  | URL                        | JWT | Описание                    |
|--------|----------------------------|-----|-----------------------------|
| POST   | /orders/                   | —   | Создать заказ               |
| GET    | /admin/orders/             | ✓   | Список заказов (админ)      |
| GET    | /admin/orders/{id}         | ✓   | Детали заказа (админ)       |
| PUT    | /admin/orders/{id}/status  | ✓   | Обновить статус (админ)     |

---

## Статусы заказа

- `new` — новый
- `processing` — в обработке
- `shipped` — отправлен
- `delivered` — доставлен
- `cancelled` — отменён
