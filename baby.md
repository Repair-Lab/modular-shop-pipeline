# 🍼 Baby-Steps: Das Projekt von Null starten

Diese Anleitung zeigt dir, wie du das Projekt nach einer Pause (oder offline) Schritt für Schritt wieder hochfährst.

---

### Schritt 1: Terminal vorbereiten
Öffne dein Terminal und wechsle in den Hauptordner des Projekts:
```bash
cd /Users/kayo/Projekt_aws
```

### Schritt 2: Python-Blase (venv) aktivieren
Damit Python weiß, wo unsere installierten Pakete (Pandas, Faker etc.) liegen, müssen wir das virtuelle Environment aktivieren:
```bash
source venv/bin/activate
```
*(Du erkennst, dass es geklappt hat, wenn vorne im Terminal `(venv)` steht!)*

### Schritt 3: Infrastruktur (Datenbank & n8n) starten
Stelle sicher, dass **Docker Desktop** auf dem Mac läuft (der kleine Wal oben rechts).
Starte dann unsere Container im Hintergrund:
```bash
cd automation
docker compose up -d
cd ..
```
*(Tipp: Das Web-Interface von n8n erreichst du jetzt wieder unter `http://localhost:5678`)*

### Schritt 4: Daten generieren (Der Shop "öffnet")
Lass uns Kunden, Verkäufe und Werkstatt-Termine simulieren. Die Termine gehen an n8n (und den Google Kalender), die restlichen Daten werden in unsere PostgreSQL-Datenbank geschrieben:
```bash
python data_generator/generator.py
```
*(Diesen Befehl kannst du beliebig oft wiederholen, um mehr historische Daten zu erzeugen!)*

### Schritt 5: ETL-Pipeline ausführen (Daten für ML aufbereiten)
Jetzt ziehen wir die Rohdaten aus der Datenbank, berechnen clevere Kennzahlen (z.B. Tage seit dem letzten Kauf) und speichern sie als `.parquet`-Dateien ab:
```bash
python etl_pipeline/load.py
```

### Schritt 6: Machine Learning Modelle trainieren (KI aktivieren)
Damit unsere Vorhersagen (Umsatz, Kundenabwanderung, Werkstatt-Auslastung) im Dashboard funktionieren, müssen wir die Modelle mit den frischen Daten trainieren:
```bash
python machine_learning/train_revenue.py
python machine_learning/train_churn.py
python machine_learning/train_capacity.py
```
*(Die trainierten Modelle werden als `.pkl`-Dateien im Ordner `machine_learning/models/` gespeichert.)*

### Schritt 7: Das Dashboard (Streamlit) öffnen
Jetzt bringen wir alles zusammen und starten die visuelle Oberfläche. Führe diesen Befehl aus:
```bash
streamlit run streamlit_app/app.py
```
*(Dein Browser sollte sich nun automatisch öffnen. Falls nicht, klicke auf den angezeigten Link im Terminal, meistens `http://localhost:8501`)*

---
### 🎉 Fertig!
Wenn du bis hierhin gekommen bist, läuft deine gesamte Infrastruktur inkl. KI-Modellen und Frontend lokal.
Für den nächsten großen Schritt (Deployment auf AWS) schau in die Haupt-`README.md` unter **Phase 6**.