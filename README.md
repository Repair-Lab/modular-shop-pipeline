# 🚲 Modular Shop Pipeline: Premium-Fahrradladen & ML Dashboard

Ein End-to-End Data-Science- und Data-Engineering-Projekt, demonstriert am Use-Case eines hybriden Geschäftsmodells (Premium-Fahrradladen mit Verkauf und Werkstatt). 

Dieses Repository beinhaltet eine vollständige Daten-Pipeline: von der simulierten Datengenerierung über Systemintegration (n8n & Google Kalender) und ETL-Prozesse bis hin zu drei spezialisierten Machine-Learning-Modellen. Das System wird in einem interaktiven Multi-Page-Dashboard (Streamlit) visualisiert, ist vollständig via Docker containerisiert und für ein speichereffizientes Deployment auf AWS (Free Tier) optimiert.

---

## 🛠 Tech Stack

* **Sprache:** Python 3.10+
* **Automatisierung & Integration:** n8n (selbst gehostet), Google Calendar API
* **Frontend:** Streamlit (Multi-Page App)
* **Data Engineering:** Pandas, SQLAlchemy, PostgreSQL / SQLite
* **Machine Learning:** Scikit-Learn (Klassifikation, Regression, Zeitreihen)
* **Infrastruktur:** Docker, Docker-Compose, AWS EC2 (t2.micro)

---

## 📁 Projektstruktur

```text
.
├── .gitignore               # Ignoriert lokale Daten/Passwörter für Git
├── README.md                # Dokumentation des Projekts
├── config/                  
│   └── shop_config.json     # Definiert Fahrrad-Produkte, Preise und Werkstatt-Services
├── data_generator/          
│   ├── generator.py         # Faker-Skript zur Live-Simulation von Kunden, Käufen & Wetter
│   └── requirements.txt
├── automation/              
│   ├── docker-compose.yml   # Startet n8n und lokale DBs
│   └── workflows/           # Backups der n8n-Automatisierungen (JSON)
├── etl_pipeline/            
│   ├── extract.py           # Zieht Rohdaten (Verkäufe, Termine)
│   ├── transform.py         # Bereinigt Daten und berechnet ML-Features (Saisonalität etc.)
│   └── load.py              # Speichert finale Tabellen (z.B. als .parquet)
├── machine_learning/        
│   ├── train_revenue.py     # Trainiert Modell 1: Umsatzvorhersage
│   ├── train_churn.py       # Trainiert Modell 2: Kundenabwanderung (Inspektion)
│   ├── train_capacity.py    # Trainiert Modell 3: Werkstatt-Auslastung
│   ├── predict.py           # Hilfsskript für neue Vorhersagen
│   └── models/              # Ablage für trainierte Modelle (.pkl)
└── streamlit_app/           
    ├── app.py               # Main Dashboard (KPI-Übersicht)
    ├── requirements.txt     
    └── pages/
        ├── 1_Finanzen.py    # Visualisierung: Umsatz, Marge & Random-Forest-Prognosen
        ├── 2_Kunden.py      # Visualisierung: CRM, RFM-Segmente & Churn Prediction
        ├── 3_Werkstatt.py   # Visualisierung: Ressourcen-Management & Kapazitäts-Prognosen
        ├── 4_Lagerbestand.py # Visualisierung: ABC-Analyse, Pareto & Bestandsüberwachung
        └── 5_Wetter_Analyse.py # Visualisierung: Wetter-Korrelationen & n8n Live-Data Mocks





🧠 Machine Learning Modelle
Das Projekt löst drei reale geschäftliche Herausforderungen:
- **Finanz-Prognose (1_Finanzen.py):** Sagt die Einnahmen der kommenden Wochen voraus, basierend auf historischen Verkäufen und saisonalen Effekten (Gleitende Durchschnitte & Random Forest Regression).
- **Inspektions-Churn (2_Kunden.py):** Ein Klassifikationsmodell, das die Wahrscheinlichkeit berechnet, mit der ein E-Bike-Käufer nicht zur Jahresinspektion zurückkehrt. Ergänzt durch RFM-Kunden-Segmentierung. Ermöglicht automatisierte Rabatt-Kampagnen via n8n.
- **Werkstatt-Auslastung (3_Werkstatt.py):** Ein Regressionsmodell zur Berechnung der zu erwartenden Kalender-Auslastung der Mechaniker für die nächste Woche. Warnt vor drohenden Überlastungen.

*(Zusätzlich implementiert: Ein datengesteuertes Lager-Management mit ABC-Analyse und dynamischer Reichweitenberechnung in `4_Lagerbestand.py`)*

🗺️ Projekt Roadmap (A bis Z)
Diese Checkliste dient als Entwicklungs-Leitfaden von der ersten Zeile Code bis zum Cloud-Deployment.

**Phase 1: Fundament & Datensimulation**
- [x] config/shop_config.json befüllen (Kategorien: E-Bikes, Bio-Bikes, Zubehör, Werkstatt, Ersatzteile).
- [x] data_generator/generator.py programmieren, um realistische Käufe und Werkstattbuchungen zu simulieren.
- [x] Requirements für den Generator installieren und erste Testdaten erzeugen.

**Phase 2: Automatisierung (n8n & Google)**
- [x] automation/docker-compose.yml ausführen, um n8n und PostgreSQL lokal zu starten.
- [x] Google Calendar API Credentials generieren.
- [x] n8n-Workflow erstellen: Webhook empfängt simulierte Termine vom generator.py und trägt diese automatisch in den Google Kalender ein.

**Phase 3: Data Engineering (ETL)**
- [x] Lokale Datenbank zur Speicherung der generierten Daten aufsetzen.
- [x] etl_pipeline/extract.py: Lese-Logik für Rohdaten implementieren.
- [x] etl_pipeline/transform.py: Daten bereinigen und Features bauen (z.B. Tage seit dem letzten Kauf/Service).
- [x] etl_pipeline/load.py: Transformierte Daten für das Machine Learning effizient als .parquet abspeichern.

**Phase 4: Machine Learning**
- [x] train_revenue.py schreiben, Modell trainieren und als .pkl speichern.
- [x] train_churn.py schreiben, Modell trainieren und als .pkl speichern.
- [x] train_capacity.py schreiben, Modell trainieren und als .pkl speichern.
- [x] predict.py als universelle Schnittstelle für die Modelle einrichten.

**Phase 5: Dashboarding (Streamlit)**
- [x] streamlit_app/app.py als Landing-Page (Command Center) mit Meta-KPIs aufbauen.
- [x] Seite 1_Finanzen.py mit interaktiven Zeitfiltern, Moving-Averages und kombiniertem KI-Trend ausstatten.
- [x] Seite 2_Kunden.py mit Bubble-Charts, RFM-Filterung und automatisierten n8n-Massenmail-Mocks ausstatten.
- [x] Seite 3_Werkstatt.py mit Ampel-Kapazitätsauslastung, Service-Mix-Scatterplot und Suchfunktion ausstatten.
- [x] Seite 4_Lagerbestand.py mit dynamischer ABC/Pareto-Analyse, Reichweitenberechnung und Bestellwesen aufbauen.
- [x] Seite 5_Wetter_Analyse.py mit n8n-API Mock, ML-gesteuerter Wetter-Umsatz-Prognose und Korrelationsmatrix ausstatten.

**Phase 6: Cloud Deployment (AWS)**
- [ ] AWS-Konto prüfen und eine t2.micro EC2-Instanz starten.
- [ ] SSH-Verbindung herstellen und 2 GB Swap-Space konfigurieren (verhindert RAM-Limitierung).
- [ ] Docker und Docker-Compose auf dem Server installieren.
- [ ] Repository via Git klonen.
- [ ] Container (n8n, Streamlit, DB) auf AWS hochfahren und live testen.
🚀 Lokaler Entwicklungsstart
Klone das Repository:
Bash
   git clone <dein-repo-url>
   cd modular-shop-pipeline
Starte die Infrastruktur (n8n):
Bash
   cd automation && docker-compose up -d
Generiere Testdaten:
Bash
   python data_generator/generator.py
Starte das Dashboard:
Bash
   streamlit run streamlit_app/app.py