import json
import random
import os
import uuid
import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from faker import Faker

# Faker initialisieren (Deutsche Lokalisierung für realistische Namen/Orte)
fake = Faker('de_DE')

# Pfade dynamisch definieren, damit das Skript von überall ausgeführt werden kann
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'shop_config.json')

# N8n Webhook URL (Platzhalter für Phase 2)
WEBHOOK_URL = "http://localhost:5678/webhook/workshop-booking"

# Datenbank-Verbindung (aus der docker-compose.yml)
DB_URI = "postgresql://shop_user:shop_password@localhost:5432/shop_db"

def load_config():
    """Lädt die Shop-Konfiguration."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_customer():
    """Generiert einen zufälligen Kunden."""
    return {
        "customer_id": str(uuid.uuid4()),
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "city": fake.city()
    }

def generate_sale(customer, config):
    """Simuliert einen Produktkauf (Fahrrad, Zubehör oder Ersatzteile)."""
    # Alle Kategorien außer der Werkstatt auslesen
    product_categories = [cat for cat in config['categories'].keys() if cat != 'Werkstatt']
    chosen_category = random.choice(product_categories)
    item = random.choice(config['categories'][chosen_category])
    
    # Kaufdatum in der Vergangenheit (letzte 3 Jahre)
    purchase_date = fake.date_time_between(start_date='-3y', end_date='now')
    
    # Versanddaten simulieren
    shipping_date = purchase_date + timedelta(days=random.randint(1, 4))
    shipping_status = random.choices(["Zugestellt", "Versendet", "In Bearbeitung"], weights=[0.8, 0.15, 0.05])[0]
    
    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": customer["customer_id"],
        "date": purchase_date.isoformat(),
        "item_id": item["id"],
        "item_name": item["name"],
        "price": item["price"],
        "margin": item.get("margin", 0.0),
        "category": chosen_category,
        "shipping_date": shipping_date.isoformat(),
        "shipping_status": shipping_status
    }

def generate_booking(customer, config):
    """Simuliert eine Werkstattbuchung für die Zukunft."""
    service = random.choice(config['categories']['Werkstatt'])
    
    # Termin in der Zukunft (nächste 14 Tage)
    booking_date = fake.date_time_between(start_date='now', end_date='+14d')
    
    return {
        "booking_id": str(uuid.uuid4()),
        "customer_id": customer["customer_id"],
        "customer_name": customer["name"],
        "customer_email": customer["email"],
        "service_id": service["id"],
        "service_name": service["name"],
        "duration_minutes": service["duration_minutes"],
        "price": service["price"],
        "datetime": booking_date.isoformat()
    }

def send_booking_to_n8n(booking):
    """Sendet die Werkstattbuchung via Webhook an n8n."""
    try:
        # Kurzer Timeout, damit das Skript nicht blockiert, falls n8n offline ist
        response = requests.post(WEBHOOK_URL, json=booking, timeout=2)
        if response.status_code == 200:
            print(f"✅ Webhook Erfolg: Termin für {booking['customer_name']} übermittelt.")
        else:
            print(f"⚠️ Webhook Warnung ({response.status_code}): Wurde der Workflow in n8n aktiviert?")
    except requests.exceptions.RequestException:
        print(f"❌ Webhook nicht erreichbar. n8n läuft noch nicht. URL: {WEBHOOK_URL}")

def send_email_notification(email, subject, body):
    """Simuliert den Versand einer E-Mail (z.B. Terminbestätigung oder Versand)."""
    print(f"\n📧 --- E-MAIL VERSAND AN: {email} ---")
    print(f"Betreff: {subject}")
    print(f"{body}")
    print("------------------------------------------------")

def save_to_db(customers, sales, bookings):
    """Speichert die generierten Daten in der PostgreSQL-Datenbank."""
    engine = create_engine(DB_URI)
    try:
        pd.DataFrame(customers).to_sql('customers', engine, if_exists='append', index=False)
        pd.DataFrame(sales).to_sql('sales', engine, if_exists='append', index=False)
        pd.DataFrame(bookings).to_sql('bookings', engine, if_exists='append', index=False)
        print("✅ Daten erfolgreich in PostgreSQL gespeichert!")
    except Exception as e:
        print(f"❌ Fehler beim Speichern in die Datenbank: {e}")

if __name__ == "__main__":
    print("🚀 Starte Data Generator...\n")
    config = load_config()
    
    # 1. Großen Kundenstamm generieren
    print("👥 Generiere 300 Kunden (für 3 Jahre Historie)...")
    customers = [generate_customer() for _ in range(300)]
    
    # 2. Historische Käufe generieren
    print("🛒 Generiere historische Käufe (kann einen Moment dauern)...")
    all_sales = []
    for customer in customers:
        for _ in range(random.randint(1, 15)): # 1 bis 15 Käufe pro Kunde
            sale = generate_sale(customer, config)
            all_sales.append(sale)
    print(f"✅ {len(all_sales)} Käufe generiert!")
    
    # Simuliere eine Kauf- & Versand-E-Mail für den letzten Kauf
    last_sale = all_sales[-1]
    last_customer = next(c for c in customers if c["customer_id"] == last_sale["customer_id"])
    send_email_notification(
        last_customer["email"],
        f"Ihre Bestellung ist {last_sale['shipping_status']}!",
        f"Hallo {last_customer['name']},\n\nVielen Dank für deinen Kauf von: {last_sale['item_name']} ({last_sale['price']} €).\nDer Status deiner Lieferung ist: {last_sale['shipping_status']}.\nVoraussichtliches Lieferdatum: {last_sale['shipping_date'][:10]}.\n\nGute Fahrt!"
    )
            
    # 3. Zukünftige Werkstattbuchungen generieren & senden
    print("\n🔧 Generiere Werkstatt-Termine für 60 Kunden (nächste 14 Tage)...")
    all_bookings = []
    for customer in random.sample(customers, k=60): # Wähle 60 zufällige Kunden für Werkstatt
        booking = generate_booking(customer, config)
        all_bookings.append(booking)
        send_booking_to_n8n(booking)
        
        # Simuliere Terminbestätigungs-E-Mail
        send_email_notification(
            booking["customer_email"],
            "Dein Werkstatt-Termin ist gebucht",
            f"Hallo {booking['customer_name']},\n\nDein Termin für '{booking['service_name']}' am {booking['datetime'][:10]} um {booking['datetime'][11:16]} Uhr ist bestätigt.\n\nWir freuen uns auf dich!"
        )

    # 4. In PostgreSQL speichern
    print("\n💾 Speichere generierte Daten in PostgreSQL...")
    save_to_db(customers, all_sales, all_bookings)