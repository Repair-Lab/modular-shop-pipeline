import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import date, timedelta

# Projekt-Root zum Python-Pfad hinzufügen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from machine_learning.predict import predict_capacity

st.set_page_config(page_title="Werkstatt", page_icon="🔧", layout="wide")
st.title("🔧 Werkstatt-Auslastung & Ressourcen")

DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'bookings.parquet')

try:
    # Daten laden und vorbereiten
    df_bookings = pd.read_parquet(DATA_PATH)
    df_bookings['datetime_obj'] = pd.to_datetime(df_bookings['datetime'])
    df_bookings['date'] = df_bookings['datetime_obj'].dt.date
    
    today = date.today()
    
    # --- SIDEBAR: FILTER & EINSTELLUNGEN ---
    st.sidebar.header("⚙️ Werkstatt-Steuerung")
    
    # Sicherer Date-Picker (verhindert Crash, wenn User nur Startdatum anklickt)
    default_start = today - timedelta(days=7)
    default_end = today + timedelta(days=14)
    date_selection = st.sidebar.date_input("Analyse-Zeitraum", value=(default_start, default_end))
    
    if len(date_selection) == 2:
        start_date, end_date = date_selection
    else:
        start_date = end_date = date_selection[0]
        
    search_query = st.sidebar.text_input("🔍 Suche (Kunde, Service, ID)")
    
    capacity_limit = st.sidebar.slider(
        "Tageskapazität (Minuten)", 
        min_value=120, max_value=1440, value=480, step=60,
        help="Definiert das Limit. 480 Min = 1 Vollzeit-Mechaniker (8h). Überbuchungen werden rot markiert."
    )
    
    # --- DATEN FILTERN ---
    mask_date = (df_bookings['date'] >= start_date) & (df_bookings['date'] <= end_date)
    df_filtered = df_bookings[mask_date].copy()
    
    if search_query:
        search_query = search_query.lower()
        df_filtered = df_filtered[
            df_filtered['customer_name'].str.lower().str.contains(search_query) |
            df_filtered['service_name'].str.lower().str.contains(search_query) |
            df_filtered['booking_id'].str.lower().str.contains(search_query)
        ]
    
    # --- TOP KPIs ---
    st.subheader("📊 Status-Quo (Echtzeit)")
    
    # Berechnungen für KPIs
    df_today = df_bookings[df_bookings['date'] == today]
    df_yesterday = df_bookings[df_bookings['date'] == (today - timedelta(days=1))]
    
    today_rev = df_today['price'].sum()
    yesterday_rev = df_yesterday['price'].sum()
    delta_rev = today_rev - yesterday_rev
    
    # Nächste 7 Tage
    next_7_days = [(today + timedelta(days=i)) for i in range(7)]
    df_next_7 = df_bookings[df_bookings['date'].isin(next_7_days)]
    next_7_bookings = len(df_next_7)
    next_7_mins = df_next_7['duration_minutes'].sum()
    
    max_weekly_cap = capacity_limit * 7
    utilization_pct = (next_7_mins / max_weekly_cap) * 100 if max_weekly_cap > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Umsatz Heute", f"{today_rev:,.2f} €", f"{delta_rev:+,.2f} € vs Gestern")
    kpi2.metric("Termine (Nächste 7 Tage)", f"{next_7_bookings}")
    
    # Farbige Delta-Logik für Auslastung
    if utilization_pct > 90:
        kpi3.metric("Auslastung (7 Tage)", f"{utilization_pct:.1f} %", "- Überlastungsgefahr", delta_color="inverse")
    elif utilization_pct < 40:
        kpi3.metric("Auslastung (7 Tage)", f"{utilization_pct:.1f} %", "Zu wenig Aufträge", delta_color="inverse")
    else:
        kpi3.metric("Auslastung (7 Tage)", f"{utilization_pct:.1f} %", "Gesundes Level", delta_color="normal")

    st.divider()

    # --- KOMBINIERTER GRAPH: BUCHUNGEN + LIMIT + KI ---
    st.subheader("📈 Kapazitäts-Planer & KI-Prognose")
    st.markdown("Vergleicht aktuell fixierte Termine mit dem Machbaren und der KI-Vorhersage.")
    
    # Tägliche Minuten aggregieren & fehlende Tage mit 0 auffüllen
    daily_cap = df_filtered.groupby('date')['duration_minutes'].sum().reset_index()
    all_dates = pd.date_range(start=start_date, end=end_date).date
    daily_cap = daily_cap.set_index('date').reindex(all_dates).fillna(0).reset_index()
    daily_cap.columns = ['date', 'minutes']
    
    # Ampel-Farben basierend auf dem Capacity-Slider
    marker_colors = ['#EF553B' if m > capacity_limit else '#00CC96' for m in daily_cap['minutes']]
    
    # KI-Prognose für den gleichen Zeitraum abrufen
    daily_cap['ai_prediction'] = [predict_capacity(d) for d in daily_cap['date']]
    
    fig_cap = go.Figure()
    
    # Echte Buchungen (Bar Chart)
    fig_cap.add_trace(go.Bar(
        x=daily_cap['date'], y=daily_cap['minutes'], 
        name="Fix gebucht", marker_color=marker_colors
    ))
    
    # KI Prognose (Line Chart)
    fig_cap.add_trace(go.Scatter(
        x=daily_cap['date'], y=daily_cap['ai_prediction'], 
        name="KI Erwartungswert", mode='lines',
        line=dict(color='#1E90FF', width=3, dash='dash')
    ))
    
    # Kapazitäts-Limit (Rote Linie)
    fig_cap.add_hline(
        y=capacity_limit, line_dash="solid", line_color="red", 
        annotation_text="Max. Tageskapazität", annotation_position="top right"
    )
    
    fig_cap.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Datum",
        yaxis_title="Arbeitslast (Minuten)",
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_cap, use_container_width=True)

    st.divider()

    # --- SERVICE-MIX ANALYSE ---
    st.subheader("🛠️ Service-Mix & Profitabilität")
    st.markdown("Welche Reparaturen bringen das meiste Geld bei geringstem Zeitaufwand?")
    
    if not df_filtered.empty:
        service_stats = df_filtered.groupby('service_name').agg(
            Anzahl=('booking_id', 'count'),
            Avg_Dauer=('duration_minutes', 'mean'),
            Avg_Preis=('price', 'mean'),
            Gesamt_Umsatz=('price', 'sum')
        ).reset_index()
        
        # Interaktives Bubble Chart
        fig_mix = px.scatter(
            service_stats, x='Avg_Dauer', y='Avg_Preis', size='Anzahl', color='Gesamt_Umsatz',
            hover_name='service_name', text='service_name',
            color_continuous_scale='Viridis',
            labels={
                'Avg_Dauer': 'Ø Dauer (Minuten)', 
                'Avg_Preis': 'Ø Preis (€)', 
                'Anzahl': 'Häufigkeit', 
                'Gesamt_Umsatz': 'Umsatz (€)'
            }
        )
        fig_mix.update_traces(textposition='top center', textfont_size=10)
        fig_mix.update_layout(template="plotly_white", height=500)
        st.plotly_chart(fig_mix, use_container_width=True)
    else:
        st.info("Für den gewählten Zeitraum und Filter liegen keine Service-Daten vor.")

    st.divider()

    # --- DATENTABELLE ---
    st.subheader("📋 Detaillierte Kalendereinträge")
    
    if not df_filtered.empty:
        # Schön formatierte Ansicht
        display_df = df_filtered[['datetime_obj', 'customer_name', 'service_name', 'duration_minutes', 'price']].sort_values('datetime_obj')
        display_df['datetime_obj'] = display_df['datetime_obj'].dt.strftime('%d.%m.%Y %H:%M')
        display_df.columns = ['Datum & Uhrzeit', 'Kunde', 'Service', 'Dauer (Min)', 'Umsatz (€)']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("Keine Termine gefunden.")
            
except FileNotFoundError:
    st.error("Daten nicht gefunden. Bitte führe die ETL-Pipeline aus.")