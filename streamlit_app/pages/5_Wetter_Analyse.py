import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
import sys
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression

# Projekt-Root zum Python-Pfad hinzufügen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALES_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sales.parquet')
BOOKINGS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'bookings.parquet')

st.set_page_config(page_title="Master-Plan", page_icon="🌤️", layout="wide")
st.title("🌤️ Wetter-Masterplan: Umsatz, Personal & Lager")

st.markdown("""
**Die ganzheitliche Shop-Logik:** Der prognostizierte Umsatz ist nur ein *Potenzial*. 
Du erreichst dieses Potenzial an heißen/regnerischen Tagen **nur dann**, wenn du genau die richtigen Artikel vorrätig hast und das nötige Werkstatt-Personal für die zu erwartende Laufkundschaft (Walk-Ins) einplanst.
""")

# --- n8n INFOBOX ---
with st.expander("⚙️ Datenversorgung (n8n Automatisierung)"):
    st.markdown("""
    1. **Trigger:** Täglich 06:00 Uhr.
    2. **API:** Fetch OpenWeatherMap (7-Tage Live-Prognose).
    3. **Datenbank:** PostgreSQL Upsert.
    4. **ML:** Streamlit berechnet daraus dynamisch den Ressourcen-Bedarf.
    """)

try:
    # Daten laden
    df_sales = pd.read_parquet(SALES_PATH)
    df_sales['date'] = pd.to_datetime(df_sales['date']).dt.date
    
    df_bookings = pd.read_parquet(BOOKINGS_PATH)
    df_bookings['date'] = pd.to_datetime(df_bookings['datetime']).dt.date
    
    # Aggregieren
    daily_revenue = df_sales.groupby('date')['price'].sum().reset_index()
    daily_revenue.columns = ['date', 'revenue']
    
    daily_work = df_bookings.groupby('date')['duration_minutes'].sum().reset_index()
    daily_work.columns = ['date', 'work_mins']
    
    df_master = pd.merge(daily_revenue, daily_work, on='date', how='outer').fillna(0)
    
    # Simuliertes Wetter an die historischen Daten hängen
    np.random.seed(42)
    max_rev = df_master['revenue'].max()
    min_rev = df_master['revenue'].min()
    normalized_rev = (df_master['revenue'] - min_rev) / (max_rev - min_rev + 1)
    
    df_master['temp'] = 5 + (normalized_rev * 25) + np.random.normal(0, 3, len(df_master))
    df_master['temp'] = df_master['temp'].clip(lower=-5, upper=35).round(1)
    
    df_master['rain'] = 20 - (normalized_rev * 20) + np.random.normal(0, 2, len(df_master))
    df_master['rain'] = df_master['rain'].clip(lower=0, upper=30).round(1)

    # --- SIDEBAR: ML INPUTS ---
    st.sidebar.header("🌤️ Wetter-Trend für nächste Woche")
    sim_temp = st.sidebar.slider("Ø Temperatur (°C)", min_value=-5.0, max_value=35.0, value=25.0, step=0.5)
    sim_rain = st.sidebar.slider("Ø Regenfall (mm)", min_value=0.0, max_value=30.0, value=0.0, step=0.5)
    
    # --- ML MODELLE TRAINIEREN ---
    X = df_master[['temp', 'rain']]
    model_rev = LinearRegression().fit(X, df_master['revenue'])
    # Für Walk-Ins nehmen wir an, dass gutes Wetter = mehr Spontankunden (ähnliche Korrelation wie Umsatz)
    model_walkins = LinearRegression().fit(X, df_master['revenue'] * 0.15) # Proxy für Walk-In Minuten
    
    # --- 7-TAGE PROGNOSE GENERIEREN ---
    np.random.seed(None)
    forecast_dates = [(date.today() + timedelta(days=i)) for i in range(1, 8)]
    sim_temps = np.random.normal(sim_temp, 2.0, 7).clip(min=-5, max=35).round(1)
    sim_rains = np.random.normal(sim_rain, 1.0, 7).clip(min=0, max=30).round(1)
    
    X_pred = pd.DataFrame({'temp': sim_temps, 'rain': sim_rains})
    pred_rev = np.clip(model_rev.predict(X_pred), a_min=0, a_max=None)
    pred_walkins = np.clip(model_walkins.predict(X_pred), a_min=0, a_max=None)
    
    df_forecast = pd.DataFrame({
        'Datum': forecast_dates,
        'Temp (°C)': sim_temps,
        'Regen (mm)': sim_rains,
        'Umsatz_Potenzial': pred_rev,
        'Spontan_Minuten': pred_walkins
    })
    
    # Personalbedarf berechnen (1 Mechaniker = 480 Min/Tag, wir rechnen mit 80% Effizienz = ca 380 Min)
    df_forecast['Benötigte_Mechaniker'] = np.ceil(df_forecast['Spontan_Minuten'] / 380).astype(int)

    # --- MASTER CHART (Doppelte Y-Achse) ---
    st.divider()
    st.subheader("📈 Das Master-Szenario: Umsatzpotenzial vs. Personalbedarf")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Balken: Umsatz
    fig.add_trace(
        go.Bar(x=df_forecast['Datum'], y=df_forecast['Umsatz_Potenzial'], name="Umsatzpotenzial (€)", marker_color="#00CC96"),
        secondary_y=False,
    )
    
    # Linie: Benötigtes Personal
    fig.add_trace(
        go.Scatter(x=df_forecast['Datum'], y=df_forecast['Benötigte_Mechaniker'], name="Extra Mechaniker (Walk-Ins)", mode="lines+markers", line=dict(color="#EF553B", width=4), marker=dict(size=10)),
        secondary_y=True,
    )
    
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        margin=dict(t=30, b=0)
    )
    fig.update_yaxes(title_text="Umsatz (€)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Benötigte Mechaniker", secondary_y=True, tick0=0, dtick=1, showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

    # --- TÄGLICHER AKTIONSPLAN (Lager & Werkstatt) ---
    st.divider()
    st.subheader("📅 Tägliche Handlungsanweisung (Voraussetzung für Umsatzziel)")
    
    def generate_action_plan(row):
        t = row['Temp (°C)']
        r = row['Regen (mm)']
        
        # Lager Logik
        if t > 25:
            lager = "🚨 Fokus: Trinkflaschen, Sommerbekleidung, E-Bike Akkus auffüllen."
        elif t < 10:
            lager = "❄️ Fokus: Winterhandschuhe, Lichtsets, Thermobekleidung vorn platzieren."
        elif r > 5:
            lager = "🌧️ Fokus: Schutzbleche, Regenjacken, Bremsbeläge sofort nachbestellen."
        else:
            lager = "✅ Standard-Verschleißteile prüfen (Schläuche, Ketten)."
            
        # Werkstatt Logik
        mech = row['Benötigte_Mechaniker']
        if mech >= 2:
            werkstatt = f"⚠️ {mech} Mechaniker exklusiv für Spontankunden (Plattfüße) abstellen! Keine großen Inspektionen annehmen."
        elif r > 5 or t < 10:
            werkstatt = "🔧 Kaum Laufkundschaft. Personal zu 100% für planbare Inspektionen und E-Bike Updates nutzen."
        else:
            werkstatt = f"⚖️ {mech} Mechaniker für Walk-Ins, Rest für reguläre Termine."
            
        return pd.Series([lager, werkstatt])

    df_forecast[['Lager_Bedingung', 'Werkstatt_Bedingung']] = df_forecast.apply(generate_action_plan, axis=1)
    
    # Schön formatierte Tabelle
    display_df = df_forecast[['Datum', 'Temp (°C)', 'Regen (mm)', 'Umsatz_Potenzial', 'Lager_Bedingung', 'Werkstatt_Bedingung']].copy()
    display_df['Datum'] = pd.to_datetime(display_df['Datum']).dt.strftime('%A, %d.%m.')
    display_df['Umsatz_Potenzial'] = display_df['Umsatz_Potenzial'].apply(lambda x: f"{x:,.0f} €")
    
    # Streamlit Dataframe Configuration für bessere Lesbarkeit
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Lager_Bedingung": st.column_config.TextColumn("Voraussetzung: Lagerbestand", width="large"),
            "Werkstatt_Bedingung": st.column_config.TextColumn("Voraussetzung: Werkstatt", width="large"),
            "Umsatz_Potenzial": st.column_config.TextColumn("Ziel-Umsatz")
        }
    )

except FileNotFoundError:
    st.error("Daten nicht gefunden. Bitte führe die ETL-Pipeline aus.")