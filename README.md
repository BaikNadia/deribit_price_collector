# 📊 Deribit Price Collector - Документация

## 📋 Оглавление
- [Обзор](#-обзор)
- [Архитектура](#-архитектура)
- [Установка](#-установка)
- [Запуск](#-запуск)
- [API Эндпоинты](#-api-эндпоинты)
- [Документация API](#-документация-api)
- [Компоненты](#-компоненты)
- [Улучшения](#-улучшения)
- [Тестирование](#-тестирование)
- [Мониторинг](#-мониторинг)

## 🎯 Обзор

**Deribit Price Collector** - это система для сбора, хранения и визуализации рыночных данных с криптовалютной биржи Deribit. Приложение предоставляет REST API и веб-дашборд для мониторинга цен в реальном времени.

**Основные возможности:**
- 📈 Сбор цен BTC-PERPETUAL и ETH-PERPETUAL каждые 30 секунд
- 💾 Автоматическое сохранение данных в PostgreSQL
- 🌐 REST API для доступа к историческим данным
- 📊 Веб-дашборд для визуализации данных
- 🔄 Фоновая обработка через Celery + Redis
- 🏗️ Модульная архитектура на FastAPI + SQLAlchemy

## 🏗️ Архитектура

```mermaid
graph TB
    A[Deribit API] --> B[Deribit Client]
    B --> C[Celery Worker]
    C --> D[PostgreSQL]
    D --> E[FastAPI Server]
    E --> F[Web Dashboard]
    G[Redis] --> C
    C --> G
    
    subgraph "Backend Services"
        B
        C
        D
        E
        G
    end
    
    subgraph "Frontend"
        F
    end
```

## 📦 Установка

### 1. Предварительные требования

```bash
# Python 3.8+
python --version

# PostgreSQL 12+
psql --version

# Redis
redis-server --version
```

### 2. Клонирование репозитория

```bash
git clone <repository-url>
cd deribit_price_collector
```

### 3. Настройка виртуального окружения

```bash
# Создание виртуального окружения
python -m venv .venv

# Активация (Windows)
.venv\Scripts\activate

# Активация (Linux/Mac)
source .venv/bin/activate
```

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 5. Настройка окружения

Создайте файл `.env` в корне проекта:

```env
# Deribit API
DERIBIT_BASE_URL=https://test.deribit.com/api/v2
DERIBIT_CLIENT_ID=your_client_id
DERIBIT_CLIENT_SECRET=your_client_secret

# Database
DATABASE_URL=postgresql://user:password@localhost/deribit_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### 6. Настройка базы данных

```bash
# Создание базы данных
createdb deribit_db

# Создание таблиц (если используется Alembic)
alembic upgrade head

# Или создание через Python
python -c "
from app.db.session import Base, engine
from app.db.models import Price
Base.metadata.create_all(bind=engine)
print('✅ Tables created successfully')
"
```

## 🚀 Запуск

### Вариант 1: Запуск всех компонентов (рекомендуется)

#### **Шаг 1: Запуск Redis** (новое окно терминала)
```bash
redis-server
```

#### **Шаг 2: Запуск Celery Worker** (новое окно терминала)
```bash
celery -A app.worker.tasks worker --loglevel=info --pool=solo
```

#### **Шаг 3: Запуск API сервера** (новое окно терминала)
```bash
python minimal_api.py
# или
uvicorn minimal_api:app --host 0.0.0.0 --port 8000 --reload
```

#### **Шаг 4: Запуск веб-дашборда** (новое окно терминала)
```bash
python web_dashboard.py
# или
uvicorn web_dashboard:app --host 0.0.0.0 --port 8080 --reload
```

#### **Шаг 5: Открытие приложений**
- 🌐 **Дашборд:** http://localhost:8080
- 📚 **API Docs:** http://localhost:8000/docs
- 📊 **API Health:** http://localhost:8000/health

### Вариант 2: Запуск через Docker Compose (если настроен)

```bash
docker-compose up -d
```

## 🔌 API Эндпоинты

### Основной API (порт 8000)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/` | Информация о API |
| `GET` | `/health` | Проверка состояния системы |
| `GET` | `/api/stats` | Статистика системы |
| `GET` | `/api/prices` | Последние цены |
| `GET` | `/api/prices/all` | Все цены по инструменту |
| `GET` | `/api/prices/latest` | Последняя цена инструмента |

### Дашборд API (порт 8080)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/` | Веб-интерфейс дашборда |
| `GET` | `/api/dashboard` | JSON данные для дашборда |

## 📚 Документация API

### 1. Получить статистику
```bash
curl http://localhost:8000/api/stats
```
**Ответ:**
```json
{
  "total_records": 164,
  "instruments_tracked": 2,
  "uptime": "100%",
  "last_update": "2026-01-14T20:00:00"
}
```

### 2. Получить последние цены
```bash
curl "http://localhost:8000/api/prices?limit=5"
```
**Ответ:**
```json
{
  "data": [
    {
      "time": "2026-01-14T20:00:00",
      "instrument": "BTC-PERPETUAL",
      "price": 97554.28,
      "24h_change": 1.23,
      "volume": 1250000.50,
      "source": "deribit"
    }
  ],
  "count": 1,
  "limit": 5
}
```

### 3. Получить все цены по инструменту
```bash
curl "http://localhost:8000/api/prices/all?instrument=BTC-PERPETUAL&limit=10"
```

### 4. Получить последнюю цену
```bash
curl "http://localhost:8000/api/prices/latest?instrument=BTC-PERPETUAL"
```

## 🧩 Компоненты

### 1. **Deribit Client** (`app/services/deribit_client.py`)
```python
class DeribitClient:
    """
    Клиент для работы с Deribit API.
    
    Методы:
    - get_public_ticker(): Получение данных по одному инструменту
    - get_multiple_tickers(): Параллельное получение данных
    - get_instruments(): Получение списка инструментов
    """
```

### 2. **Celery Tasks** (`app/worker/tasks.py`)
```python
@celery_app.task
def fetch_and_store_prices():
    """
    Фоновая задача для сбора и сохранения цен.
    Запускается каждые 30 секунд через Celery Beat.
    """
```

### 3. **Модели данных** (`app/db/models.py`)
```python
class Price(Base):
    """
    Модель для хранения цен с Deribit.
    
    Поля:
    - instrument_name: Название инструмента
    - price: Текущая цена
    - volume: Объем торгов за 24ч (USD)
    - timestamp: Время получения данных
    - additional_data: Полный ответ API
    """
```

### 4. **API Сервер** (`minimal_api.py`)
```python
app = FastAPI(title="Deribit Price Collector")
# Предоставляет REST API для доступа к данным
```

### 5. **Веб-дашборд** (`web_dashboard.py`)
```python
app = FastAPI(title="Deribit Price Collector Dashboard")
# Предоставляет веб-интерфейс для визуализации
```

## 🚀 Улучшения

### 1. **Расширение функциональности**

#### Добавить больше инструментов:
```python
# В tasks.py расширить список
instruments = [
    "BTC-PERPETUAL",
    "ETH-PERPETUAL",
    "SOL-PERPETUAL",  # ← Новые инструменты
    "XRP-PERPETUAL",
    "ADA-PERPETUAL"
]
```

#### Добавить опционы:
```python
# В DeribitClient добавить метод
async def get_options(self, currency: str):
    """Получение опционных контрактов"""
    params = {"currency": currency, "kind": "option"}
    return await self._make_request("get_instruments", params)
```

### 2. **Улучшение производительности**

#### Кэширование:
```python
# Добавить Redis кэш
from redis import Redis
redis = Redis(host='localhost', port=6379, db=0)

@app.get("/api/prices/latest")
@cache(expire=60)  # Кэш на 60 секунд
async def get_latest_price(instrument: str, db: Session = Depends(get_db)):
    # ...
```

#### Пагинация:
```python
# В API добавить пагинацию
@app.get("/api/prices/history")
async def get_price_history(
    instrument: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size
    # ...
```

### 3. **Улучшение мониторинга**

#### Добавить метрики:
```python
# Prometheus метрики
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

#### Health checks:
```python
# Расширенный health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": await check_db(),
        "redis": await check_redis(),
        "deribit_api": await check_deribit(),
        "uptime": get_uptime(),
        "version": "1.0.0"
    }
```

### 4. **Улучшение безопасности**

#### Аутентификация:
```python
# JWT аутентификация
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

@app.get("/api/admin/stats")
async def get_admin_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Проверка токена
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token")
    # ...
```

#### Rate limiting:
```python
# Ограничение запросов
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/prices")
@limiter.limit("100/minute")
async def get_prices(request: Request, ...):
    # ...
```

### 5. **Улучшение дашборда**

#### Графики:
```html
<!-- Добавить Chart.js -->
<canvas id="priceChart"></canvas>
<script>
    var ctx = document.getElementById('priceChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: 'BTC Price',
                data: prices,
                borderColor: 'rgb(75, 192, 192)'
            }]
        }
    });
</script>
```

#### Уведомления:
```javascript
// WebSocket для real-time обновлений
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

### 6. **Деплой и оркестрация**

#### Docker Compose:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: deribit_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    
  api:
    build: .
    command: uvicorn minimal_api:app --host 0.0.0.0 --port 8000
    depends_on:
      - postgres
      - redis

  celery:
    build: .
    command: celery -A app.worker.tasks worker --loglevel=info
    depends_on:
      - redis
      - postgres

  dashboard:
    build: .
    command: uvicorn web_dashboard:app --host 0.0.0.0 --port 8080
    depends_on:
      - api
```

#### Kubernetes:
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deribit-collector
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: deribit-collector:latest
        ports:
        - containerPort: 8000
```

## 🧪 Тестирование

### 1. Тестирование клиента Deribit
```bash
python app/services/deribit_client.py
```

### 2. Запуск unit-тестов
```bash
pytest tests/ -v
```

### 3. Интеграционные тесты
```bash
# Тест всей системы
python tests/integration_test.py
```

### 4. Нагрузочное тестирование
```bash
# Используя locust
locust -f tests/locustfile.py
```

## 📊 Мониторинг

### 1. Логирование
```python
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deribit_collector.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Метрики
```bash
# Prometheus метрики
curl http://localhost:8000/metrics
```

### 3. Health checks
```bash
# Проверка состояния
curl http://localhost:8000/health
```

### 4. Мониторинг очереди
```bash
# Просмотр очереди Celery
redis-cli -n 0 LLEN celery
```

## 🔧 Устранение неполадок

### 1. Проблема: "No price data available"
```bash
# Проверьте Celery worker
celery -A app.worker.tasks inspect active

# Проверьте базу данных
python -c "from app.db.models import Price; from app.db.session import SessionLocal; db = SessionLocal(); print(f'Records: {db.query(Price).count()}'); db.close()"
```

### 2. Проблема: API недоступен
```bash
# Проверьте порты
netstat -an | grep "8000\|8080"

# Перезапустите сервисы
pkill -f "uvicorn"
python minimal_api.py
python web_dashboard.py
```

### 3. Проблема: Redis не подключен
```bash
# Проверьте Redis
redis-cli ping
# Должен ответить PONG
```

## 📈 Производительность

### Бенчмарки:
- API Response Time: < 100ms
- Data Collection Interval: 30 seconds
- Maximum Records: 1M+ (с пагинацией)
- Concurrent Users: 100+ (с rate limiting)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для фичи
3. Закоммитьте изменения
4. Отправьте pull request

## 📄 Лицензия

MIT License

---

## 🎯 Быстрый старт (TL;DR)

```bash
# 1. Установка
git clone <repo>
cd deribit_price_collector
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. Настройка БД
createdb deribit_db
# Создайте .env файл

# 3. Запуск (в разных терминалах)
redis-server
celery -A app.worker.tasks worker --loglevel=info --pool=solo
python minimal_api.py
python web_dashboard.py

# 4. Открыть
# Дашборд: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

---
