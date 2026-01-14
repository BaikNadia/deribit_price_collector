from celery import Celery
from app.core.config import settings

# Создаем экземпляр Celery
celery_app = Celery(
    "price_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"]
)

# Конфигурация для Windows
celery_app.conf.update(
    # Основные настройки
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Важно для Windows
    worker_pool="solo",  # Используем solo pool вместо prefork (Windows не поддерживает fork)
    worker_concurrency=1,  # Один процесс

    # Настройки для надежности
    broker_connection_retry_on_startup=True,  # Исправляет предупреждение
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут лимит на задачу
    task_soft_time_limit=25 * 60,  # 25 минут мягкий лимит

    # Настройки Redis
    broker_transport_options={
        'visibility_timeout': 3600,  # 1 час
        'socket_keepalive': True,
        'retry_on_timeout': True,
    },

    # Настройки результатов
    result_expires=3600,  # Результаты хранятся 1 час
    result_backend_transport_options={
        'retry_policy': {
            'timeout': 5.0
        }
    },
)

# Расписание периодических задач
celery_app.conf.beat_schedule = {
    # Задача каждые 5 минут (измените на нужный интервал)
    'fetch-prices-every-5-minutes': {
        'task': 'app.worker.tasks.fetch_and_store_prices',
        'schedule': 300.0,  # 300 секунд = 5 минут
        'args': (),
        'kwargs': {},
        'options': {
            'expires': 240,  # Задача истекает через 4 минуты
            'queue': 'celery',
        }
    },

    # Пример дополнительной задачи (можно добавить позже)
    # 'cleanup-old-prices-daily': {
    #     'task': 'app.worker.tasks.cleanup_old_prices',
    #     'schedule': crontab(hour=3, minute=0),  # Каждый день в 3:00
    #     'args': (30,),  # Удалять записи старше 30 дней
    # },
}

# Альтернативный способ задания расписания (через crontab)
# celery_app.conf.beat_schedule = {
#     'fetch-prices-every-5-minutes': {
#         'task': 'app.worker.tasks.fetch_and_store_prices',
#         'schedule': crontab(minute='*/5'),  # Каждые 5 минут
#     },
# }

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks(['app.worker'])

# Для тестирования
if __name__ == "__main__":
    print("Celery app configuration:")
    print(f"  Broker: {celery_app.conf.broker_url}")
    print(f"  Backend: {celery_app.conf.result_backend}")
    print(f"  Timezone: {celery_app.conf.timezone}")
    print(f"  Worker pool: {celery_app.conf.worker_pool}")
    print("\nScheduled tasks:")
    for task_name, task_config in celery_app.conf.beat_schedule.items():
        print(f"  - {task_name}: {task_config['schedule']}")
