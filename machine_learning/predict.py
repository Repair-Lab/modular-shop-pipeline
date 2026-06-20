import os
import joblib
import pandas as pd
from datetime import datetime

# Pfade definieren
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'machine_learning', 'models')

def load_model(filename):
    """Lädt ein trainiertes Modell aus dem models-Ordner."""
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Modell {filename} nicht gefunden. Bitte trainiere es zuerst.")
    return joblib.load(path)

def predict_revenue(target_date):
    """Sagt den erwarteten Umsatz für ein bestimmtes Datum voraus."""
    model = load_model('revenue_model.pkl')
    dt = pd.to_datetime(target_date)
    features = pd.DataFrame([{
        'day_of_week': dt.dayofweek,
        'month': dt.month,
        'is_weekend': int(dt.dayofweek in [5, 6])
    }])
    return model.predict(features)[0]

def predict_churn(total_spent, purchase_count):
    """Sagt voraus, ob ein Kunde abwandert (1 = Ja, 0 = Nein)."""
    model = load_model('churn_model.pkl')
    features = pd.DataFrame([{
        'total_spent': total_spent,
        'purchase_count': purchase_count
    }])
    return model.predict(features)[0]

def predict_capacity(target_date):
    """Sagt die erwartete Werkstatt-Auslastung in Minuten voraus."""
    model = load_model('capacity_model.pkl')
    dt = pd.to_datetime(target_date)
    features = pd.DataFrame([{
        'day_of_week': dt.dayofweek,
        'month': dt.month,
        'is_weekend': int(dt.dayofweek in [5, 6])
    }])
    return model.predict(features)[0]

if __name__ == "__main__":
    print("🧪 Teste Machine Learning Vorhersage-Schnittstelle...\n")
    
    test_date = "2026-07-15"
    print(f"💰 Erwarteter Umsatz am {test_date}: {predict_revenue(test_date):.2f} €")
    print(f"🔧 Erwartete Werkstatt-Auslastung am {test_date}: {predict_capacity(test_date):.0f} Minuten")
    
    churn_pred = predict_churn(total_spent=1500.0, purchase_count=2)
    print(f"👥 Kunde (Ausgegeben: 1500€, Käufe: 2) -> Vorhersage: {'Abgewandert 🛑' if churn_pred == 1 else 'Aktiv ✅'}")