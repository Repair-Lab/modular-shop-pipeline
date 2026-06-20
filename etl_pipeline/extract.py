import pandas as pd
from sqlalchemy import create_engine
import os

# Datenbank-Verbindung (lokale PostgreSQL aus Docker)
DB_URI = "postgresql://shop_user:shop_password@localhost:5432/shop_db"

def extract_data():
    """Extrahiert die Rohdaten (Kunden, Käufe, Termine) aus der Datenbank."""
    print("📥 Starte Daten-Extraktion (Extract)...")
    engine = create_engine(DB_URI)
    
    try:
        # SQL-Abfragen, um die kompletten Tabellen in Pandas DataFrames zu laden
        df_customers = pd.read_sql("SELECT * FROM customers", engine)
        df_sales = pd.read_sql("SELECT * FROM sales", engine)
        df_bookings = pd.read_sql("SELECT * FROM bookings", engine)
        
        print("✅ Extraktion erfolgreich!")
        print(f"   - Kunden: {len(df_customers)} Datensätze gefunden")
        print(f"   - Käufe: {len(df_sales)} Datensätze gefunden")
        print(f"   - Termine: {len(df_bookings)} Datensätze gefunden")
        
        return df_customers, df_sales, df_bookings
        
    except Exception as e:
        print(f"❌ Fehler bei der Extraktion: {e}")
        return None, None, None

if __name__ == "__main__":
    extract_data()