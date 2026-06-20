import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Pfade definieren
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'bookings.parquet')
MODEL_DIR = os.path.join(BASE_DIR, 'machine_learning', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'capacity_model.pkl')

def load_data():
    """Lädt die aufbereiteten Werkstatt-Termine."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Daten nicht gefunden: {DATA_PATH}. Bitte zuerst ETL-Pipeline ausführen.")
    return pd.read_parquet(DATA_PATH)

def prepare_data(df):
    """Aggregiert die gebuchten Minuten pro Tag."""
    # Nur das Datum aus dem Zeitstempel extrahieren
    df['date'] = pd.to_datetime(df['datetime']).dt.date
    df['date'] = pd.to_datetime(df['date'])
    
    # Auslastung in Minuten pro Tag summieren
    daily_capacity = df.groupby('date')['duration_minutes'].sum().reset_index()
    
    # Zeit-Features für das ML-Modell bauen
    daily_capacity['day_of_week'] = daily_capacity['date'].dt.dayofweek
    daily_capacity['month'] = daily_capacity['date'].dt.month
    daily_capacity['is_weekend'] = daily_capacity['day_of_week'].isin([5, 6]).astype(int)
    
    return daily_capacity

def train_model():
    print("🚀 Starte Training für Werkstatt-Auslastung (Capacity Prediction)...")
    
    df = load_data()
    daily_capacity = prepare_data(df)
    
    if len(daily_capacity) < 10:
        print("⚠️ Info: Dein Datensatz ist noch recht klein. Nutze 'generator.py' öfter für bessere ML-Ergebnisse!")
        
    # X (Features) und y (Zielvariable = gebuchte Minuten)
    X = daily_capacity[['day_of_week', 'month', 'is_weekend']]
    y = daily_capacity['duration_minutes']
    
    if len(y) < 2:
        print("⚠️ Warnung: Nicht genug Datenpunkte vorhanden. Bitte generiere mehr Termine.")
        return
        
    # Train/Test Split (angepasst für kleine Datensätze)
    test_size = 0.2 if len(daily_capacity) >= 5 else 0.5
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    print("🧠 Trainiere Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Modell auswerten & speichern
    predictions = model.predict(X_test)
    print(f"✅ Training abgeschlossen!")
    print(f"⏱️ Durchschnittliche Abweichung (MAE): {mean_absolute_error(y_test, predictions):.1f} Minuten pro Tag")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Modell gespeichert unter: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()