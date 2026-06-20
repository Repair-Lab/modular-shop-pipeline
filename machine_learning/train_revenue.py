import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Pfade definieren
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sales.parquet')
MODEL_DIR = os.path.join(BASE_DIR, 'machine_learning', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'revenue_model.pkl')

def load_data():
    """Lädt die aufbereiteten Verkaufsdaten."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Daten nicht gefunden: {DATA_PATH}. Bitte zuerst ETL-Pipeline ausführen.")
    return pd.read_parquet(DATA_PATH)

def prepare_data(df):
    """Aggregiert Umsätze auf Tagesebene und extrahiert Zeit-Features."""
    df['date'] = pd.to_datetime(df['date'])
    
    # Umsatz pro Tag summieren
    daily_revenue = df.groupby(df['date'].dt.date)['price'].sum().reset_index()
    daily_revenue.columns = ['date', 'revenue']
    daily_revenue['date'] = pd.to_datetime(daily_revenue['date'])
    
    # Features bauen: Das Modell soll lernen, wie Wochentage und Monate den Umsatz beeinflussen
    daily_revenue['day_of_week'] = daily_revenue['date'].dt.dayofweek
    daily_revenue['month'] = daily_revenue['date'].dt.month
    daily_revenue['is_weekend'] = daily_revenue['day_of_week'].isin([5, 6]).astype(int)
    
    return daily_revenue

def train_model():
    print("🚀 Starte Training für Umsatzvorhersage (Revenue Prediction)...")
    
    df = load_data()
    daily_revenue = prepare_data(df)
    
    if len(daily_revenue) < 10:
        print("⚠️ Info: Dein Datensatz ist noch recht klein. Nutze 'generator.py' öfter für bessere ML-Ergebnisse!")
        
    # X (Features) und y (Zielvariable) trennen
    X = daily_revenue[['day_of_week', 'month', 'is_weekend']]
    y = daily_revenue['revenue']
    
    # In Trainings- und Testdaten aufteilen (80% Training, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("🧠 Trainiere Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Modell auswerten
    predictions = model.predict(X_test)
    print(f"✅ Training abgeschlossen!")
    print(f"📊 Durchschnittliche Abweichung (MAE): {mean_absolute_error(y_test, predictions):.2f} € pro Tag")
    
    # Modell speichern
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Modell gespeichert unter: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()