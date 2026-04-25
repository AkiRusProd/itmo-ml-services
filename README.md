# Apartment Price Service

ML-сервисс предсказания стоимости квартир.

## Обзор

Проект реализует ML-сервис для предсказания стоимости квартир со следующими возможностями:
- JWT-аутентификация
- внутренний биллинг на основе кредитов
- асинхронная обработка предсказаний через `Celery + Redis`
- PostgreSQL для постоянного хранения данных
- мониторинг через `Prometheus + Grafana`
- пользовательский аналитический дашборд на `Streamlit`

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Запуск через Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Сервисы:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5173`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Celery worker: фоновая обработка предсказаний
- Prometheus: `http://127.0.0.1:9090`
- Grafana: `http://127.0.0.1:3000` (`admin` / `admin`)
- Streamlit dashboard: `http://127.0.0.1:8501`

Чтобы локально создать демо-администратора и промокод:

```bash
.venv/bin/python scripts/seed_demo_data.py
```

Если сидирование выполняется внутри Docker Compose:

```bash
docker compose exec api python scripts/seed_demo_data.py
```

Чтобы отдельно запустить frontend локально:

```bash
cd frontend
npm install
npm run dev
```

## Доступные эндпоинты

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET /api/v1/wallet`
- `POST /api/v1/wallet/top-up`
- `GET /api/v1/wallet/transactions`
- `POST /api/v1/promo-codes`
- `POST /api/v1/promo-codes/redeem`
- `POST /api/v1/predictions`
- `GET /api/v1/predictions`
- `GET /api/v1/predictions/{id}`
- `GET /api/v1/models/current`
- `GET /api/v1/metrics`

## Архитектура

Основные сервисы:
- `api` — приложение FastAPI с auth, billing, prediction-эндпоинтами и Swagger
- `worker` — Celery worker, который обрабатывает поставленные в очередь prediction-задачи
- `db` — база данных PostgreSQL
- `redis` — broker/backend для Celery
- `prometheus` — сбор метрик
- `grafana` — дашборды метрик
- `dashboard` — аналитическое приложение на Streamlit

Основные сущности хранения:
- `users`
- `wallets`
- `transactions`
- `prediction_requests`
- `prediction_results`
- `promo_codes`
- `promo_code_activations`
- `ml_models`

## Пример запроса

```json
{
  "MedInc": 8.3252,
  "HouseAge": 41.0,
  "AveRooms": 6.9841,
  "AveBedrms": 1.0238,
  "Population": 322.0,
  "AveOccup": 2.5556,
  "Latitude": 37.88,
  "Longitude": -122.23
}
```

## Аутентификация

1. Зарегистрируйте пользователя:

```json
{
  "email": "user@example.com",
  "password": "strongpass123",
  "full_name": "Rustam User"
}
```

2. Выполните логин и получите `access_token`.
3. Передайте `Authorization: Bearer <token>` в защищенный эндпоинт.

## Предсказания

`POST /api/v1/predictions` сохраняет:
- входящий запрос на предсказание со статусом и входным payload;
- итоговое значение предсказания и метаданные модели.

Предсказания выполняются через `Celery + Redis`:
- API создает `prediction_request` со статусом `queued`;
- worker забирает задачу и обновляет статус на `processing/completed/failed`;
- клиент опрашивает `GET /api/v1/predictions` или `GET /api/v1/predictions/{id}`.

Для локальных smoke-тестов можно принудительно включить синхронное выполнение:

```bash
CELERY_TASK_ALWAYS_EAGER=true uvicorn app.main:app --reload
```

## Логика биллинга

Биллинг построен на внутренних кредитах.

Реализованные правила:
- каждый новый пользователь получает welcome-бонус;
- пополнение кошелька создает запись о транзакции;
- активация промокода создает запись о транзакции;
- кредиты списываются только после успешного завершения предсказания;
- неуспешное предсказание не должно создавать транзакцию списания;
- все изменения баланса можно восстановить по истории транзакций.

Основные типы транзакций:
- `bonus`
- `top_up`
- `promo_code`
- `prediction_charge`

Такая схема соответствует требованию брифа о прозрачном и аудируемом биллинге.

## База данных и миграции

По умолчанию приложение использует локальную SQLite через `DATABASE_URL=sqlite:///./app.db`.
Позже можно переключиться на PostgreSQL, переопределив `DATABASE_URL`.

В проект добавлен Alembic:

```bash
alembic upgrade head
```

Для Docker Compose по умолчанию используется PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://app_user:app_password@db:5432/apartment_service
REDIS_URL=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=false
```

## Мониторинг

Prometheus собирает метрики с API-эндпоинта:

- `GET /api/v1/metrics`

Grafana автоматически настраивается с:
- datasource для Prometheus
- обзорным дашбордом по request rate, latency, prediction outcomes, queue depth и кредитам

## Аналитический дашборд

Streamlit-дашборд доступен по адресу:

- `http://127.0.0.1:8501`

Он показывает:
- общее количество пользователей
- общее количество и число успешных предсказаний
- списанные кредиты, пополнения и начисления по промокодам
- активность предсказаний по дням
- поток кредитов по дням
- последние предсказания и транзакции

## Метаданные модели

Информация о текущей активной модели доступна через:

- `GET /api/v1/models/current`

Эндпоинт возвращает имя активной модели, версию, путь к артефакту, target и ожидаемые признаки.

## Тесты

Запуск unit-тестов:

```bash
.venv/bin/pytest tests/unit -q
```

Запуск полного набора тестов:

```bash
.venv/bin/pytest tests -q
```

Вместе с проектом приложен [BUSINESS_PLAN.md](BUSINESS_PLAN.md).
