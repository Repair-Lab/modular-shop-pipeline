import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Pfade definieren
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'ml_customers.parquet')
MODEL_DIR = os.path.join(BASE_DIR, 'machine_learning', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'churn_model.pkl')

def load_data():
    """Lädt die aufbereiteten Kundendaten."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Daten nicht gefunden: {DATA_PATH}. Bitte zuerst ETL-Pipeline ausführen.")
    return pd.read_parquet(DATA_PATH)

def prepare_data(df):
    """Bereitet die Daten für die Churn-Klassifikation vor."""
    # Wir definieren "Churn" (Abwanderung) als: Kunde hat seit über 180 Tagen nichts gekauft
    df['is_churned'] = (df['days_since_last_purchase'] > 180).astype(int)
    
    # Wir füllen eventuelle NaN-Werte bei total_spent und purchase_count
    df['total_spent'] = df['total_spent'].fillna(0)
    df['purchase_count'] = df['purchase_count'].fillna(0)
    
    return df

def train_model():
    print("🚀 Starte Training für Churn Prediction (Kundenabwanderung)...")
    
    df = load_data()
    df_prepared = prepare_data(df)
    
    if len(df_prepared) < 10:
        print("⚠️ Info: Dein Datensatz ist sehr klein. Nutze 'generator.py' öfter für bessere Ergebnisse!")
        
    # X (Features) und y (Zielvariable) trennen
    # Wir nutzen Umsatz und Anzahl der Käufe, um vorherzusagen, ob jemand abwandert
    X = df_prepared[['total_spent', 'purchase_count']]
    y = df_prepared['is_churned']
    
    # Prüfen, ob wir überhaupt beide Klassen (0 und 1) in den Daten haben
    if len(y.unique()) < 2:
        print("⚠️ Warnung: Es gibt aktuell nur Kunden EINER Klasse (entweder alle abgewandert oder keiner).")
        print("Bitte generiere mehr Daten mit generator.py und lass die ETL-Pipeline nochmal laufen.")
        return
        
    # In Trainings- und Testdaten aufteilen (80% Training, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("🧠 Trainiere Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Modell auswerten
    predictions = model.predict(X_test)
    print(f"✅ Training abgeschlossen!")
    print(f"🎯 Genauigkeit (Accuracy): {accuracy_score(y_test, predictions):.2%}")
    
    # Modell speichern
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"💾 Modell gespeichert unter: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()