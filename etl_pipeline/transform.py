import pandas as pd
import os
import sys
from datetime import datetime

# Das Hauptverzeichnis zum Python-Pfad hinzufügen, damit wir 'extract' importieren können
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from etl_pipeline.extract import extract_data

def transform_data(df_customers, df_sales, df_bookings):
    """Bereinigt die Daten und baut ML-Features (Feature Engineering)."""
    print("\n⚙️ Starte Daten-Transformation (Transform)...")
    
    if df_customers is None or df_sales is None or df_bookings is None:
        print("❌ Keine Daten zum Transformieren gefunden.")
        return None, None, None

    # 1. Datumskonvertierungen (Texte in echte Datums-Objekte umwandeln)
    df_sales['date'] = pd.to_datetime(df_sales['date'])
    df_bookings['datetime'] = pd.to_datetime(df_bookings['datetime'])

    # 2. ML Feature Engineering: Kunden-Features für Churn Prediction (Abwanderung)
    print("   - Berechne Kunden-Metriken (Umsatz, Kauf-Frequenz, Letzter Kauf...)")
    
    # Aggregation der Verkäufe pro Kunde
    customer_sales = df_sales.groupby('customer_id').agg(
        total_spent=('price', 'sum'),
        purchase_count=('transaction_id', 'count'),
        last_purchase_date=('date', 'max')
    ).reset_index()

    # Merge mit den Stammdaten der Kunden
    df_ml_customers = pd.merge(df_customers, customer_sales, on='customer_id', how='left')
    
    # Fehlende Werte auffüllen (falls Kunden noch nichts gekauft haben)
    df_ml_customers['total_spent'] = df_ml_customers['total_spent'].fillna(0)
    df_ml_customers['purchase_count'] = df_ml_customers['purchase_count'].fillna(0)
    
    # "Tage seit letztem Kauf" berechnen (Recency) - extrem wichtig für Machine Learning!
    today = pd.to_datetime('today').tz_localize(None) # Aktuelles Datum ohne Zeitzone
    df_ml_customers['last_purchase_date'] = df_ml_customers['last_purchase_date'].dt.tz_localize(None)
    
    df_ml_customers['days_since_last_purchase'] = (today - df_ml_customers['last_purchase_date']).dt.days
    df_ml_customers['days_since_last_purchase'] = df_ml_customers['days_since_last_purchase'].fillna(9999) # 9999 = Hat noch nie gekauft

    print("✅ Transformation erfolgreich abgeschlossen!")
    return df_ml_customers, df_sales, df_bookings

if __name__ == "__main__":
    # Zum Testen rufen wir zuerst den Extraktions-Schritt auf und übergeben die Daten dann
    df_c, df_s, df_b = extract_data()
    df_ml_c, df_ml_s, df_ml_b = transform_data(df_c, df_s, df_b)
    
    if df_ml_c is not None:
        print("\n📊 Vorschau der neuen Machine-Learning-Features für Kunden:")
        print(df_ml_c[['name', 'total_spent', 'purchase_count', 'days_since_last_purchase']].head())