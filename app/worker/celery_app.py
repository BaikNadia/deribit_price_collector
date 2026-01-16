from celery import Celery

from app.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "price_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],
)

# Настройки для Windows
celery_app.conf.update(
    # Основные настройки
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # КРИТИЧЕСКО ВАЖНО для Windows
    worker_pool="solo",  # Используем solo pool (Windows не поддерживает fork)
    worker_concurrency=1,  # Один процесс
    # Настройки для надежности
    broker_connection_retry_on_startup=True,  # Исправляет предупреждение
    task_track_started=True,
    task_time_limit=300,  # 5 минут лимит на задачу
    task_soft_time_limit=240,  # 4 минуты мягкий лимит
    # Настройки Redis
    broker_transport_options={
        "visibility_timeout": 3600,  # 1 час
        "socket_keepalive": True,
        "retry_on_timeout": True,
    },
    # Настройки очередей
    task_default_queue="celery",
    task_queues={
        "celery": {
            "exchange": "celery",
            "routing_key": "celery",
        }
    },
    # Настройки результатов
    result_expires=3600,  # Результаты хранятся 1 час
    # Логирование
    worker_hijack_root_logger=False,
    worker_redirect_stdouts=True,
    worker_redirect_stdouts_level="INFO",
)

# УПРОЩЕННОЕ РАСПИСАНИЕ для тестирования
celery_app.conf.beat_schedule = {
    # Тестовая задача каждые 30 секунд (для отладки)
    "fetch-prices-test": {
        "task": "app.worker.tasks.fetch_and_store_prices",
        "schedule": 30.0,  # Каждые 30 секунд
        "args": (),
        "options": {
            "queue": "celery",
            "expires": 25,  # Истекает через 25 секунд
        },
    },
}

# Для тестирования
if __name__ == "__main__":
    print("=" * 60)
    print("Celery Configuration Test")
    print("=" * 60)
    print(f"Broker URL: {celery_app.conf.broker_url}")
    print(f"Result Backend: {celery_app.conf.result_backend}")
    print(f"Timezone: {celery_app.conf.timezone}")
    print(f"Worker Pool: {celery_app.conf.worker_pool}")
    print(f"Beat Schedule: {list(celery_app.conf.beat_schedule.keys())}")
