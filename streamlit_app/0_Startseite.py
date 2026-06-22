import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# Seiten-Konfiguration (muss der allererste Streamlit-Befehl sein)
st.set_page_config(

    page_title="Startseite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für eine professionelle Landing Page
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #1E90FF, #00CC96);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .highlight-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        border-left: 5px solid #1E90FF;
        height: 100%;
    }
    .dark-mode .highlight-box {
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">End-to-End Data Science Pipeline</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Von der Datensimulation über Machine Learning bis zum Cloud-Deployment.</p>', unsafe_allow_html=True)

st.markdown("""
**Willkommen zu meinem Abschlussprojekt.** 
Dieses Dashboard ist das Frontend einer vollautomatisierten Daten-Pipeline für ein fiktives hybrides Geschäftsmodell (Fahrradverkauf & Werkstatt). 
Es demonstriert die nahtlose Integration von **Data Engineering, API-Automatisierung (n8n), Machine Learning und interaktiver Datenvisualisierung**.
""")

if st.button("🔄 Livedaten & ML-Modelle aktualisieren", type="primary"):
    st.rerun()

st.divider()

# Pfade definieren
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALES_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sales.parquet')
CUSTOMERS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'ml_customers.parquet')
BOOKINGS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'bookings.parquet')

try:
    # Daten laden
    df_sales = pd.read_parquet(SALES_PATH)
    df_customers = pd.read_parquet(CUSTOMERS_PATH)
    
    try:
        df_bookings = pd.read_parquet(BOOKINGS_PATH)
        total_bookings = len(df_bookings)
    except FileNotFoundError:
        total_bookings = 0
    
    # Berechnungen für globale KPIs
    total_revenue = df_sales['price'].sum()
    total_customers = len(df_customers)
    total_items = len(df_sales)
    
    # RFM Metriken für Quick-Stats
    active_customers = len(df_customers[df_customers['days_since_last_purchase'] <= 180])
    customer_retention = (active_customers / total_customers * 100) if total_customers > 0 else 0

    st.subheader("📊 Executive Summary (Echtzeit-Datenbank)")
    
    # 4 Spalten für Quick KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Simulierter Gesamtumsatz", f"{total_revenue:,.2f} €")
    kpi2.metric("👥 Datenbank-Kunden", f"{total_customers}")
    kpi3.metric("📈 Customer Retention", f"{customer_retention:.1f} %")
    kpi4.metric("🔧 Werkstatt-Operationen", f"{total_bookings}")
    
    st.divider()



    st.subheader("🧬 Architektur & Implementierte Module (Kapitel)")
    st.markdown("Nutze die **linke Seitenleiste**, um in die funktionalen Data-Science-Module abzutauchen. Die Präsentation baut sich systematisch auf:")




    # 3x2 Grid für saubere Kacheln (inklusive Modul 5)
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    
    with row1_col1:
        st.info("""





        ### 💰 1. Finanzen
        **Technologie:** Random Forest, Moving Averages
        - Interaktive Zeitreihenanalyse
        - ML: Dynamische Prognose zukünftiger Tagesumsätze
        """)
    
    with row1_col2:
        st.success("""





        ### 👥 2. Kunden CRM
        **Technologie:** RFM-Analyse, n8n Webhooks
        - Mathematische Kundensegmentierung
        - ML: Churn-Prediction inkl. n8n-Rückgewinnung
        """)


        
    with row1_col3:
        st.warning("""





        ### 🔧 3. Werkstatt
        **Technologie:** Regression, Kapazitätslimits
        - Service-Mix-Analyse (Profitabilität)
        - ML: Prognose der erwarteten Mechaniker-Auslastung
        """)
        

    with row2_col1:
        st.error("""





        ### 📦 4. Lagerbestand
        **Technologie:** Pareto (80/20), Days-of-Supply
        - ABC-Klassifizierung des Inventars
        - Automatischer n8n-Bestell-Trigger bei Engpässen
        """)
        
    with row2_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); padding: 1.5rem; border-radius: 10px; color: black; height: 100%;">
        <h3 style="color: black; margin-top:0;">🌤️ 5. Wetterdaten & ML-Strategie</h3>
        <b>Das Finale:</b> Hier fließen alle Teilbereiche zusammen. 
        Ein übergreifendes ML-Modell nutzt simulierte API-Daten (OpenWeatherMap via n8n), um tagesaktuelle Handlungsanweisungen für Lager und Personal zu berechnen.
        </div>
        """, unsafe_allow_html=True)
        
    with row2_col3:
        st.markdown("""
        <div style="background-color: #262730; padding: 1.5rem; border-radius: 10px; height: 100%; border-left: 5px solid #FF9900;">
        <h3 style="color: #FF9900; margin-top:0;">☁️ Phase 6: Cloud Deployment</h3>
        <b>AWS EC2 Infrastruktur:</b>
        <ul style="color: #bbb; padding-left: 1.2rem; margin-top: 0.5rem;">
            <li>Dockerisierte System-Architektur</li>
            <li>Googles OAuth2-Tunneling via n8n</li>
            <li><b>Zero-Touch:</b> Nächtliche CRON-Jobs automatisieren die ETL-Pipeline und das ML-Retraining.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)










except FileNotFoundError:
    st.warning("⚠️ Bisher wurden keine Daten gefunden.")
    st.info("""
    **💡 So startest du das Projekt lokal:**
    1. Generiere Testdaten im Terminal: `python data_generator/generator.py`
    2. Führe die ETL-Pipeline aus: `python etl_pipeline/load.py`
    3. Trainiere die Basis-Modelle: `python machine_learning/predict.py` (oder spezifische Skripte)
    4. Klicke oben auf **Livedaten aktualisieren**.
    """)