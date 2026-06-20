import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import numpy as np

# Projekt-Root zum Python-Pfad hinzufügen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sales.parquet')

st.set_page_config(page_title="Lager", page_icon="📦", layout="wide")
st.title("📦 Intelligentes Lager & Bestellwesen")

# Farb-Konstanten
COLOR_A = "#00CC96"  # Grün
COLOR_B = "#FFA15A"  # Orange
COLOR_C = "#EF553B"  # Rot

try:
    df_sales = pd.read_parquet(DATA_PATH)
    
    # Historischen Zeitraum für Reichweitenberechnung ermitteln
    min_date = pd.to_datetime(df_sales['date']).min()
    max_date = pd.to_datetime(df_sales['date']).max()
    days_in_history = (max_date - min_date).days
    days_in_history = days_in_history if days_in_history > 0 else 1
    
    # 1. Basis-Statistiken pro Artikel berechnen
    inventory_df = df_sales.groupby(['item_name', 'category']).agg(
        verkauft_gesamt=('transaction_id', 'count'),
        umsatz_gesamt=('price', 'sum')
    ).reset_index()
    
    # 2. ABC-Analyse berechnen (nach kumuliertem Umsatz)
    inventory_df = inventory_df.sort_values(by='umsatz_gesamt', ascending=False)
    inventory_df['umsatz_prozent'] = inventory_df['umsatz_gesamt'] / inventory_df['umsatz_gesamt'].sum() * 100
    inventory_df['umsatz_kumuliert'] = inventory_df['umsatz_prozent'].cumsum()
    
    def get_abc_class(kumuliert):
        if kumuliert <= 80:
            return "A"
        elif kumuliert <= 95:
            return "B"
        else:
            return "C"
            
    inventory_df['ABC_Klasse'] = inventory_df['umsatz_kumuliert'].apply(get_abc_class)
    
    # 3. Dynamischer Bestand und Reichweite (Days of Supply)
    # Reproduzierbarer Seed für die Demo, damit die Zahlen beim Filtern nicht wild herumspringen
    np.random.seed(42)
    inventory_df['aktueller_bestand'] = np.random.randint(0, 25, size=len(inventory_df))
    
    # Ø Verkäufe pro Tag
    inventory_df['sales_per_day'] = inventory_df['verkauft_gesamt'] / days_in_history
    
    # Reichweite in Tagen berechnen (bei 0 Verkäufen = Unendlich/999)
    inventory_df['reichweite_tage'] = np.where(
        inventory_df['sales_per_day'] > 0,
        inventory_df['aktueller_bestand'] / inventory_df['sales_per_day'],
        999
    ).round(0)
    
    # 4. KI-Bestellempfehlung (erweitert um Reichweite)
    def empfehlung(row):
        if row['aktueller_bestand'] == 0 and row['ABC_Klasse'] in ['A', 'B']:
            return "🚨 Kritisch: Sofort nachbestellen!"
        elif row['reichweite_tage'] < 7 and row['ABC_Klasse'] == 'A':
            return "⚠️ Warnung: A-Artikel fast leer"
        elif row['aktueller_bestand'] == 0:
            return "🚨 Leerstand (C-Artikel)"
        elif row['reichweite_tage'] == 999:
            return "📉 Ladenhüter"
        else:
            return "✅ Bestand OK"
            
    inventory_df['KI_Empfehlung'] = inventory_df.apply(empfehlung, axis=1)
    
    # --- SIDEBAR: FILTER ---
    st.sidebar.header("⚙️ Lager-Filter")
    
    all_categories = sorted(inventory_df['category'].unique().tolist())
    selected_categories = st.sidebar.multiselect("Kategorie:", options=all_categories, default=all_categories)
    
    all_statuses = sorted(inventory_df['KI_Empfehlung'].unique().tolist())
    selected_statuses = st.sidebar.multiselect("Status-Filter:", options=all_statuses, default=all_statuses)
    
    selected_abc = st.sidebar.multiselect("ABC-Klassen:", options=["A", "B", "C"], default=["A", "B", "C"])
    
    # Filter anwenden
    df_filtered = inventory_df[
        (inventory_df['category'].isin(selected_categories)) & 
        (inventory_df['KI_Empfehlung'].isin(selected_statuses)) &
        (inventory_df['ABC_Klasse'].isin(selected_abc))
    ].copy()

    # --- TOP KPIs ---
    st.subheader("📊 Aktueller Lagerstatus")
    
    kritisch = len(inventory_df[inventory_df['KI_Empfehlung'].str.contains("🚨")])
    warnung = len(inventory_df[inventory_df['KI_Empfehlung'].str.contains("⚠️")])
    a_out_of_stock = len(inventory_df[(inventory_df['ABC_Klasse'] == 'A') & (inventory_df['aktueller_bestand'] == 0)])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Überwachte Artikel", len(inventory_df))
    col2.metric("A-Artikel (Top Seller)", len(inventory_df[inventory_df['ABC_Klasse'] == 'A']))
    col3.metric("Kritische Engpässe", kritisch)
    col4.metric("A-Artikel Out-of-Stock", a_out_of_stock, "Höchste Prio!", delta_color="inverse" if a_out_of_stock > 0 else "normal")
    
    st.divider()

    # --- DATENTABELLE MIT PANDAS STYLER ---
    st.subheader("📋 Inventar & Reichweiten-Analyse")
    
    if not df_filtered.empty:
        # Spalten für Anzeige sortieren und umbenennen
        display_df = df_filtered[[
            'item_name', 'category', 'ABC_Klasse', 'aktueller_bestand', 
            'reichweite_tage', 'verkauft_gesamt', 'umsatz_gesamt', 'KI_Empfehlung'
        ]].copy()
        
        display_df.columns = [
            'Artikel', 'Kategorie', 'ABC', 'Bestand', 
            'Reichweite (Tage)', 'Verkäufe (Hist.)', 'Umsatz (€)', 'Empfehlung'
        ]
        
        # Pandas Styler für farbliche Markierungen
        def highlight_rows(row):
            # Rot für komplett leere A/B Artikel
            if "🚨" in row['Empfehlung']:
                return ['background-color: rgba(255, 75, 75, 0.2)'] * len(row)
            # Gelb/Orange für fast leere A-Artikel (Reichweite < 7)
            elif "⚠️" in row['Empfehlung']:
                return ['background-color: rgba(255, 165, 0, 0.2)'] * len(row)
            # A-Artikel leicht grün hervorheben
            elif row['ABC'] == 'A':
                return ['background-color: rgba(0, 204, 150, 0.1)'] * len(row)
            return [''] * len(row)

        styled_df = display_df.style.apply(highlight_rows, axis=1).format({
            "Umsatz (€)": "{:,.2f} €",
            "Reichweite (Tage)": "{:.0f}"
        })
        
        st.dataframe(styled_df, use_container_width=True, height=400, hide_index=True)
        
        # ACTION BUTTONS
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("🛒 Lieferanten-Bestellung auslösen (n8n)", type="primary"):
                items_to_order = len(display_df[display_df['Empfehlung'].str.contains("🚨|⚠️")])
                if items_to_order > 0:
                    st.success(f"✅ Webhook an n8n gesendet! Automatische Bestellung für {items_to_order} kritische Artikel wurde ausgelöst.")
                else:
                    st.info("In der aktuellen Ansicht gibt es keine kritischen Artikel, die bestellt werden müssen.")
    else:
        st.info("Keine Artikel gefunden, die den gewählten Filtern entsprechen.")
    
    st.divider()

    # --- PARETO CHART ---
    st.subheader("📈 Pareto-Analyse (80/20 Regel)")
    st.markdown("Das Diagramm zeigt, wie wenige Artikel (A-Klasse) für den Großteil des Umsatzes verantwortlich sind.")
    
    # Pareto nutzt die unfilterten Daten, um das Gesamtbild nicht zu verfälschen
    pareto_data = inventory_df.head(50).copy() # Top 50 der Übersichtlichkeit halber
    
    fig_pareto = go.Figure()
    
    # Layer 1: Umsatz Balken
    fig_pareto.add_trace(go.Bar(
        x=pareto_data['item_name'], 
        y=pareto_data['umsatz_gesamt'],
        name="Umsatz (€)",
        marker_color='#1E90FF',
        yaxis='y1'
    ))
    
    # Layer 2: Kumulierte Prozent-Linie
    fig_pareto.add_trace(go.Scatter(
        x=pareto_data['item_name'], 
        y=pareto_data['umsatz_kumuliert'],
        name="Kumulierter Umsatz (%)",
        mode='lines+markers',
        line=dict(color='#FF4500', width=3),
        yaxis='y2'
    ))
    
    # 80% Markierungslinie
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", yref="y2", annotation_text="80% Umsatz-Grenze")
    
    # Layout mit zweiter Y-Achse
    fig_pareto.update_layout(
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(title="Artikel (Top 50)", tickangle=-45, showticklabels=False), # Labels verstecken bei vielen Produkten
        yaxis=dict(title="Umsatz (€)", side='left', showgrid=False),
        yaxis2=dict(title="Kumulierter Anteil (%)", side='right', overlaying='y', range=[0, 105], showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        margin=dict(b=0)
    )
    
    st.plotly_chart(fig_pareto, use_container_width=True)

except FileNotFoundError:
    st.error("Daten nicht gefunden. Bitte führe die ETL-Pipeline aus.")