import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import date, timedelta

# Add project root to python path for ML imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from machine_learning.predict import predict_revenue

st.set_page_config(page_title="Finanzen", page_icon="💰", layout="wide")
st.title("💰 Finanz-Übersicht & Prognosen")

DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sales.parquet')

try:
    df_sales = pd.read_parquet(DATA_PATH)
    df_sales['date'] = pd.to_datetime(df_sales['date'])
    
    # Base date for calculations (latest entry in dataset to ensure logic works with simulated data)
    max_date = df_sales['date'].max()
    
    # --- SIDEBAR: INTERACTIVE CONTROLS ---
    st.sidebar.header("⚙️ Analyse-Einstellungen")
    
    time_filter = st.sidebar.selectbox(
        "Historischer Zeitraum", 
        ["Letzte 30 Tage", "Letzte 90 Tage", "Dieses Jahr (YTD)", "Gesamte Historie"]
    )
    
    ma_window = st.sidebar.slider(
        "Gleitender Durchschnitt (Tage)", 
        min_value=3, max_value=365, value=7, step=1,
        help="Glättet die Tagesumsätze über die gewählten Tage, um Trends unabhängig von Wochenenden besser zu erkennen."
    )
    
    forecast_horizon = st.sidebar.slider(
        "KI-Prognose (Tage in die Zukunft)", 
        min_value=7, max_value=365, value=14, step=1,
        help="Bestimmt, wie weit in die Zukunft das Random Forest Modell den Chart zeichnen soll."
    )
    
    # --- DATA FILTERING ---
    if time_filter == "Letzte 30 Tage":
        start_date = max_date - pd.Timedelta(days=30)
    elif time_filter == "Letzte 90 Tage":
        start_date = max_date - pd.Timedelta(days=90)
    elif time_filter == "Dieses Jahr (YTD)":
        start_date = pd.to_datetime(f"{max_date.year}-01-01")
    else:
        start_date = df_sales['date'].min()
        
    df_filtered = df_sales[df_sales['date'] >= start_date].copy()
    
    # --- TOP KPIs & YOY / MOM TRENDS ---
    st.subheader("📊 Key Performance Indicators")
    
    # Calculate current vs previous month metrics
    curr_month_sales = df_sales[(df_sales['date'].dt.month == max_date.month) & (df_sales['date'].dt.year == max_date.year)]
    
    prev_month_date = max_date - pd.DateOffset(months=1)
    prev_month_sales = df_sales[(df_sales['date'].dt.month == prev_month_date.month) & (df_sales['date'].dt.year == prev_month_date.year)]
    
    curr_rev = curr_month_sales['price'].sum()
    prev_rev = prev_month_sales['price'].sum()
    delta_rev = ((curr_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
    
    curr_items = len(curr_month_sales)
    prev_items = len(prev_month_sales)
    delta_items = ((curr_items - prev_items) / prev_items * 100) if prev_items > 0 else 0
    
    avg_order_value = curr_rev / curr_items if curr_items > 0 else 0

    # Display KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Umsatz lfd. Monat", f"{curr_rev:,.2f} €", f"{delta_rev:.1f}% vs. Vormonat")
    kpi2.metric("Verkäufe lfd. Monat", f"{curr_items}", f"{delta_items:.1f}% vs. Vormonat")
    kpi3.metric("Durchschn. Bestellwert", f"{avg_order_value:,.2f} €")
    
    st.divider()
    
    # --- COMBINED CHART: HISTORY + MA + AI FORECAST ---
    st.subheader("📈 Umsatzentwicklung & KI-Trend")
    
    # Aggregate daily revenue and fill missing dates with 0
    daily_revenue = df_filtered.groupby(df_filtered['date'].dt.date)['price'].sum().reset_index()
    daily_revenue.columns = ['date', 'revenue']
    daily_revenue['date'] = pd.to_datetime(daily_revenue['date'])
    
    if not daily_revenue.empty:
        # Create a continuous date range to ensure missing sales days are recorded as 0
        full_date_range = pd.date_range(start=daily_revenue['date'].min(), end=daily_revenue['date'].max())
        daily_revenue = daily_revenue.set_index('date').reindex(full_date_range).fillna(0).reset_index()
        daily_revenue.columns = ['date', 'revenue']
        
        # Calculate Moving Average based on the slider
        daily_revenue['ma'] = daily_revenue['revenue'].rolling(window=ma_window, min_periods=1).mean()
        
        # Generate AI Forecast for the future
        future_dates = pd.date_range(start=max_date + pd.Timedelta(days=1), periods=forecast_horizon)
        forecasts = [{'date': d, 'prediction': predict_revenue(d)} for d in future_dates]
        df_forecast = pd.DataFrame(forecasts)
        
        # Build Multi-layer Plotly Figure
        fig = go.Figure()
        
        # Layer 1: Daily Historical Revenue (Light blue bars)
        fig.add_trace(go.Bar(
            x=daily_revenue['date'], y=daily_revenue['revenue'], 
            name="Tagesumsatz", marker_color='rgba(135, 206, 250, 0.5)'
        ))
        
        # Layer 2: Moving Average (Solid blue line) - Dropping NaN values so the line doesn't start at 0
        ma_valid = daily_revenue.dropna(subset=['ma'])
        fig.add_trace(go.Scatter(
            x=ma_valid['date'], y=ma_valid['ma'], 
            name=f"{ma_window}-Tage Durchschnitt", line=dict(color='#1E90FF', width=3)
        ))
        
        # Layer 3: AI Forecast (Dashed red line)
        fig.add_trace(go.Scatter(
            x=df_forecast['date'], y=df_forecast['prediction'], 
            name="KI-Prognose", line=dict(color='#FF4500', width=3, dash='dash')
        ))
        
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_title="Datum",
            yaxis_title="Umsatz (€)",
            template="plotly_white",
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Für diesen Zeitraum liegen keine Daten vor.")
        
    st.divider()
    
    # --- CATEGORY SPLIT & SINGLE PREDICTION ---
    col_donut, col_predict = st.columns([1, 1])
    
    with col_donut:
        st.subheader("🍩 Umsatz nach Kategorien")
        category_sales = df_filtered.groupby('category')['price'].sum().reset_index()
        fig_pie = px.pie(
            category_sales, values='price', names='category', 
            hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_predict:
        # Keep the original functionality for precise single day queries
        st.subheader("🎯 Gezielte Einzel-Prognose")
        st.markdown("Frag das KI-Modell für ein **konkretes Datum** in der Zukunft ab.")
        target_date = st.date_input("Datum wählen", value=date.today() + timedelta(days=1))
        if st.button("Umsatz vorhersagen", type="primary"):
            prediction = predict_revenue(target_date)
            st.success(f"Erwarteter Umsatz am **{target_date.strftime('%d.%m.%Y')}**:\n\n### {prediction:,.2f} €")
            
except FileNotFoundError:
    st.error("Daten nicht gefunden. Bitte führe die ETL-Pipeline aus.")