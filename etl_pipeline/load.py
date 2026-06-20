import os
import sys

# Das Hauptverzeichnis zum Python-Pfad hinzufügen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from etl_pipeline.extract import extract_data
from etl_pipeline.transform import transform_data

def load_data(df_ml_customers, df_sales, df_bookings):
    """Speichert die bereinigten Daten als .parquet-Dateien für das Machine Learning."""
    print("\n💾 Starte Daten-Ladeprozess (Load)...")
    
    if df_ml_customers is None:
        print("❌ Keine Daten zum Speichern vorhanden.")
        return False

    # Zielordner 'data/processed' im Hauptverzeichnis erstellen
    output_dir = os.path.join(BASE_DIR, 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Als Parquet speichern (sehr effizient für Machine Learning)
        df_ml_customers.to_parquet(os.path.join(output_dir, 'ml_customers.parquet'), index=False)
        df_sales.to_parquet(os.path.join(output_dir, 'sales.parquet'), index=False)
        df_bookings.to_parquet(os.path.join(output_dir, 'bookings.parquet'), index=False)
        
        print(f"✅ Daten erfolgreich im Ordner gespeichert: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Daten: {e}")
        print("💡 Tipp: Möglicherweise fehlt die 'pyarrow' Bibliothek. Installiere sie mit: pip install pyarrow")
        return False

def run_etl_pipeline():
    """Führt die komplette ETL-Pipeline (Extract -> Transform -> Load) aus."""
    print("🚀 Starte vollständige ETL-Pipeline...\n")
    
    # 1. Extract
    df_c, df_s, df_b = extract_data()
    
    # 2. Transform
    df_ml_c, df_ml_s, df_ml_b = transform_data(df_c, df_s, df_b)
    
    # 3. Load
    load_data(df_ml_c, df_ml_s, df_ml_b)
    
    print("\n🎉 ETL-Pipeline erfolgreich abgeschlossen!")

if __name__ == "__main__":
    run_etl_pipeline()