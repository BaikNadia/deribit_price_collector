import sys
import os

sys.path.insert(0, os.getcwd())

from app.db.session import SessionLocal
from app.db.models import Price
from sqlalchemy import desc, func
from datetime import datetime, timedelta

db = SessionLocal()
try:
    print("=" * 60)
    print("📊 Deribit Price Collector - Data Report")
    print("=" * 60)

    # Общая статистика
    total = db.query(Price).count()
    print(f"Всего записей: {total}")

    if total > 0:
        # Последние 5 записей
        print("\n📈 Последние 5 записей:")
        print("-" * 60)
        recent = db.query(Price).order_by(desc(Price.timestamp)).limit(5).all()
        for p in recent:
            time_str = p.timestamp.strftime("%H:%M:%S")
            print(f"{time_str} | {p.instrument_name:15} | ${p.price:10.2f}")

        # Статистика по инструментам
        print("\n📊 Статистика по инструментам:")
        print("-" * 60)
        stats = db.query(
            Price.instrument_name,
            func.count(Price.id).label('count'),
            func.min(Price.timestamp).label('first'),
            func.max(Price.timestamp).label('last'),
            func.min(Price.price).label('min_price'),
            func.max(Price.price).label('max_price'),
            func.avg(Price.price).label('avg_price')
        ).group_by(Price.instrument_name).all()

        for stat in stats:
            print(f"{stat.instrument_name:15}:")
            print(f"  Количество: {stat.count}")
            print(f"  Период: {stat.first.strftime('%H:%M')} - {stat.last.strftime('%H:%M')}")
            print(f"  Цена: ${stat.min_price:.2f} - ${stat.max_price:.2f} (avg: ${stat.avg_price:.2f})")
            print()

    else:
        print("\n⚠️  База данных пуста!")
        print("Убедитесь, что:")
        print("1. Модель Price создана в app/db/models.py")
        print("2. Выполнены миграции Alembic")
        print("3. Задачи Celery успешно сохраняют данные")

finally:
    db.close()
