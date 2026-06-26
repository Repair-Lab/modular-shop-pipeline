# 🚀 Abschlusspräsentation: Modular Shop Pipeline

**Dauer:** ca. 30 Minuten
**Zielgruppe:** Dozenten, Prüfer, Data-Science-Fachpublikum
**Zielsetzung:** Demonstration einer End-to-End Datenpipeline – von lokaler Simulation über Data Engineering und ML-Modellierung bis hin zum Cloud-Deployment.

---

## ⏱️ Zeitplan & Agenda

1. **Einleitung & Projektvision** (3 Min)
2. **Phase 1 & 2: Datensimulation und Automatisierung** (5 Min)
3. **Phase 3: Data Engineering (ETL-Pipeline)** (5 Min)
4. **Phase 4 & 5: Data Science & Dashboarding (Die 5 Module)** (12 Min)
5. **Phase 6: Cloud-Infrastruktur & AWS Deployment** (3 Min)
6. **Fazit & Q&A** (2 Min)

---

## 🎙️ Präsentations-Skript (Roter Faden)

### 1. Einleitung & Projektvision (3 Min)
* **Hook:** "Stellen Sie sich vor, Sie betreiben einen hybriden Fahrradladen (Verkauf + Werkstatt). Ihr Problem: Daten liegen in Silos, Personal wird falsch geplant, Kapital ist in Ladenhütern gebunden."
* **Lösung:** "Mein Abschlussprojekt ist eine komplette **End-to-End Datenpipeline**. Kein reines Jupyter-Notebook-Projekt, sondern ein produktionsnahes System."
* **Der Tech-Stack:** Kurz die Architekturgrafik/Tools erwähnen (Python, PostgreSQL, n8n, Scikit-Learn, Streamlit, Docker, AWS, Google cloud).

### 2. Phase 1 & 2: Datensimulation und Automatisierung (5 Min)
* **Die Herausforderung:** "Ich hatte keine echten Unternehmensdaten. Also musste ich das Unternehmen *simulieren*."
* **Der Data-Generator:** Erklären, wie das Skript realistische Kunden, Produktverkäufe und Werkstattbuchungen erzeugt (inkl. simuliertem Kaufverhalten und Rauschen).
* **Die Systemintegration (n8n):** 
  * "Ich wollte zeigen, dass das System mit der Außenwelt kommunizieren kann."
  * **Live-Demo/Screenshot:** Zeigen, wie der Generator einen Werkstatt-Termin via Webhook an n8n sendet und n8n diesen per API in einen echten Google Calendar einträgt.

### 3. Phase 3: Data Engineering (ETL-Pipeline) (5 Min)
* **Warum ETL?** "Rohdaten aus der PostgreSQL sind nicht ML-ready."
* **Extract:** Ziehen der generierten Daten.
* **Transform (Das Herzstück):** "Hier passiert das Feature-Engineering."
  * Beispiel geben: Berechnung der Recency (Tage seit dem letzten Kauf), Aggregation von Umsätzen.
* **Load:** Speicherung als `.parquet` Dateien. "Warum Parquet? Weil es spaltenbasiert, stark komprimiert und blitzschnell für das Streamlit-Dashboard und ML-Modelle auszulesen ist."

### 4. Phase 4 & 5: Data Science & Dashboarding (12 Min)
*(Hier wechseln Sie idealerweise ins Live-Dashboard und zeigen die Seiten der Reihe nach)*

* **Modul 1: Finanzen (2 Min):**
  * Zeigen des interaktiven Moving-Averages (Glättung von Wochenend-Effekten).
  * Erklären der Random-Forest-Regression, die den Trend der nächsten Tage voraussagt.
* **Modul 2: Kunden & CRM (3 Min):**
  * Erklären der **RFM-Analyse** (Recency, Frequency, Monetary). Wie das System Kunden automatisch segmentiert.
  * **Highlight:** Das Churn-Radar. Zeigen Sie den Button, der eine simulierte n8n-Rückgewinnungs-Kampagne auslöst. "Actionable Data Science".
* **Modul 3: Werkstatt-Ressourcen (2 Min):**
  * Zeigen des Kapazitätslimits (die rote Linie) im Verhältnis zu fixen Buchungen und der KI-Prognose.
  * Kurzer Blick auf den Service-Mix (Profitabilität vs. Arbeitszeit).
* **Modul 4: Lager-Logik (2 Min):**
  * Erklären der automatischen **ABC-Analyse** und des **Pareto-Charts** (80/20 Regel).
  * "Das System berechnet die *Days of Supply* und triggert (via n8n) Bestellungen, bevor A-Artikel out-of-stock gehen."
* **Modul 5: Der Masterplan (Wetter-Korrelation) (3 Min):**
  * "Dies ist der finale Schritt: Die Zusammenführung von Silos."
  * Erklären, wie simulierte OpenWeatherMap-Daten genutzt werden.
  * **Live-Demo:** Ziehen Sie die Wetter-Slider (Temperatur hoch, Regen runter) und zeigen Sie dem Prüfer, wie sich die Strategie für Lager *und* Werkstatt dynamisch anpasst (Spontankunden vs. Planbare Inspektionen).

### 5. Phase 6: Cloud-Infrastruktur & AWS Deployment (3 Min)
* **Die Architektur:** "Die gesamte App läuft nicht nur auf meinem Laptop. Sie ist in Docker-Containern gekapselt und im Internet erreichbar."
* **AWS EC2:** "Ich habe das System auf einer AWS t2.micro (Free Tier) Instanz provisioniert. Um Googles strenge OAuth2-Sicherheitsrichtlinien zu umgehen, habe ich einen sicheren OAuth-Tunnel über n8n etabliert."
* **Das RAM-Problem:** "Da die Instanz nur 1GB RAM hat, kam es bei Datenbank-Operationen zu Engpässen. Ich habe dies gelöst, indem ich auf Ubuntu-Ebene einen **2GB Swap-Space** auf der SSD eingerichtet habe."
* **Zero-Touch Automation (CI/CD Gedanke):** 
  * "Eine berechtigte Frage ist: Muss ich die ML-Modelle jeden Tag manuell trainieren? **Nein.**"
  * "Ich habe auf dem Server einen **Linux CRON-Daemon** eingerichtet. Jeden Tag um 02:00 Uhr nachts zieht das ETL-Skript automatisch die neuen Daten. Um 02:05 Uhr werden die drei ML-Modelle automatisch neu trainiert. Wenn der Manager morgens das Dashboard öffnet, ist die KI bereits auf dem Stand von gestern."
* *(Falls live auf AWS: Link zum Dashboard `http://3.67.100.249:8501` im Browser öffnen).*

### 6. Fazit & Q&A (2 Min)
* **Zusammenfassung:** "Dieses Projekt beweist, dass moderne Daten-Architektur mehr ist als nur bunte Graphen. Es ist die Kombination aus Engineering (ETL), Automation (n8n) und Intelligence (ML), die echtes Business-Value generiert."
* **Offen für Fragen.**

---

## 💡 Tipps für den Vortrag
1. **Fokus auf Business-Value:** Prüfer lieben es, wenn man nicht nur über Python-Bibliotheken spricht, sondern erklärt, *warum* eine Funktion gebaut wurde (z.B. "Die ABC-Analyse senkt die Kapitalbindung im Lager").
2. **Die Fehler-Kultur:** Wenn Sie gefragt werden, was schwer war, erwähnen Sie das RAM-Limit auf AWS und die Lösung mit dem Swap-Space. Das zeigt tiefes technisches Verständnis.
3. **Flüssige Übergänge:** Navigieren Sie souverän durch die Streamlit-Tabs. Das Dashboard ist Ihr bester visueller Anker.