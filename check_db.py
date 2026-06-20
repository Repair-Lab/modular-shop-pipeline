import pandas as pd
from sqlalchemy import create_engine

# Verbindung zur Datenbank (gleiche Zugangsdaten wie im Generator)
DB_URI = "postgresql://shop_user:shop_password@localhost:5432/shop_db"
engine = create_engine(DB_URI)

print("🔍 Lese Daten aus PostgreSQL...\n")

print("👥 Tabelle 'customers' (Erste 3 Einträge):")
print(pd.read_sql("SELECT * FROM customers LIMIT 3", engine))

print("\n🛒 Tabelle 'sales' (Erste 3 Einträge):")
print(pd.read_sql("SELECT * FROM sales LIMIT 3", engine))

print("\n🔧 Tabelle 'bookings' (Erste 3 Einträge):")
print(pd.read_sql("SELECT * FROM bookings LIMIT 3", engine))