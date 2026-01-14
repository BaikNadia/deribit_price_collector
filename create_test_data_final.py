import sys

sys.path.append('.')

from app.db.session import SessionLocal
from app.db.models import PriceTick
import time

db = SessionLocal()

# Удаляем старые данные (опционально)
try:
    db.query(PriceTick).delete()
    db.commit()
    print("Старые данные удалены")
except:
    db.rollback()

# Создаем тестовые данные
test_records = []
now = int(time.time())

# BTC данные (последние 5 минут)
for i in range(5):
    record = PriceTick(
        ticker="btc_usd",
        price=45000.00 + i * 100.50,  # Растущая цена
        timestamp=now - (300 - i * 60),  # Последние 5 минут
    )
    test_records.append(record)

# ETH данные (последние 5 минут)
for i in range(5):
    record = PriceTick(
        ticker="eth_usd",
        price=2500.00 + i * 25.75,  # Растущая цена
        timestamp=now - (300 - i * 60),  # Последние 5 минут
    )
    test_records.append(record)

# Добавляем все записи
for record in test_records:
    db.add(record)

db.commit()

# Проверяем
btc_count = db.query(PriceTick).filter(PriceTick.ticker == "btc_usd").count()
eth_count = db.query(PriceTick).filter(PriceTick.ticker == "eth_usd").count()

print("✅ Тестовые данные созданы:")
print(f"   BTC записей: {btc_count}")
print(f"   ETH записей: {eth_count}")
print(f"   Всего записей: {btc_count + eth_count}")

# Покажем последние записи
print("\nПоследние записи:")
for ticker in ["btc_usd", "eth_usd"]:
    latest = db.query(PriceTick)\
        .filter(PriceTick.ticker == ticker)\
        .order_by(PriceTick.timestamp.desc())\
        .first()
    if latest:
        print(f"   {ticker}: ${latest.price} (timestamp: {latest.timestamp})")

db.close()
