"""
================================================================================
Streamlit-Seite 6: Marktanalyse & Benchmark
================================================================================
Diese Seite analysiert deutsche Fahrrad-Marktdaten (Kaggle-Datensatz, gefiltert
und auf 2026 zeitverschoben) mit interaktiven Echtzeitfiltern.

Datenquelle: data_benchmark/bike_sales_germany_2026.csv
Transformation: eda_pipeline/bike-store-sales-in-europe.ipynb
================================================================================
"""

# ===== IMPORTS =====
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import datetime, timedelta

# ===== PAGE CONFIG (MUSS ERSTER BEFEHL SEIN!) =====
st.set_page_config(
    page_title="Marktanalyse & Benchmark",
    page_icon="🌍",
    layout="wide"
)

# ===== BASE DIRECTORY SETUP =====
# Diese Datei liegt in: streamlit_app/pages/6_Marktanalyse_Benchmark.py
# Wir müssen 3x os.path.dirname() gehen, um zum Projekt-Stammverzeichnis zu kommen:
# pages/ -> streamlit_app/ -> Projekt_aws/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# ===== DATEN LADEN =====
CSV_PATH = os.path.join(BASE_DIR, 'data_benchmark', 'bike_sales_germany_2026.csv')

try:
    # Lade die CSV-Datei
    df = pd.read_csv(CSV_PATH)
    
    # Konvertiere Date-Spalte zu datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # ===== HEADER & TITLE =====
    st.title("🌍 Marktanalyse & Benchmark")
    st.markdown(
        """
        **Deutsche Fahrradmarkt 2026 — Echtzeit-Datenanalyse**
        
        Dieses Dashboard zeigt den realen deutschen Fahrradmarkt basierend auf echten Kaggle-Daten
        (gefiltert auf Deutschland, zeitverschoben auf 2026). Nutze die Filter links, um die Analyse
        auf spezifische Bundesländer und Zeiträume zu konzentrieren.
        
        💡 **Hinweis:** Die Daten werden in Echtzeit auf deine Filter-Auswahl aktualisiert.
        """
    )
    st.divider()
    
    # ===== SIDEBAR-FILTER =====
    st.sidebar.header("⚙️ Filter & Einstellungen")
    
    # Filter 1: Bundesländer (State) - MultiSelect
    alle_bundeslaender = sorted(df['State'].unique())
    ausgewaehlte_bundeslaender = st.sidebar.multiselect(
        "📍 Bundesländer wählen:",
        options=alle_bundeslaender,
        default=alle_bundeslaender,  # Standard: alle Bundesländer ausgewählt
        help="Wähle ein oder mehrere Bundesländer zur Filterung."
    )
    
    # Filter 2: Zeitraum - Slider
    min_datum = df['Date'].min().date()
    max_datum = df['Date'].max().date()
    
    datum_bereich = st.sidebar.slider(
        "📅 Zeitraum wählen:",
        min_value=min_datum,
        max_value=max_datum,
        value=(min_datum, max_datum),  # Standard: gesamter Bereich
        step=timedelta(days=1),
        help="Wähle Start- und Enddatum für die Analyse."
    )
    
    start_date, end_date = datum_bereich
    
    # ===== DATEN FILTERN =====
    # Wende beide Filter auf den ursprünglichen Datensatz an
    df_filtered = df[
        (df['State'].isin(ausgewaehlte_bundeslaender)) &
        (df['Date'].dt.date >= start_date) &
        (df['Date'].dt.date <= end_date)
    ].copy()
    
    # ===== SICHERHEIT: WARNUNG BEI LEEREN DATEN =====
    if df_filtered.empty:
        st.warning(
            "⚠️ Keine Daten für diese Filterauswahl verfügbar. "
            "Bitte wähle andere Bundesländer oder einen anderen Zeitraum."
        )
        st.stop()  # Beende hier, um keine leeren Diagramme anzuzeigen
    
    # ===== KPI-METRIKEN =====
    st.subheader("📊 Key Performance Indicators")
    
    # Berechne KPI-Werte aus gefilterten Daten
    gesamtumsatz = df_filtered['Revenue'].sum()
    durchschnittsalter = df_filtered['Customer_Age'].mean()
    
    # Bestseller: Kategorie mit den meisten Verkäufen (Volumen, nicht Umsatz)
    bestseller = df_filtered['Product_Category'].value_counts().index[0]
    bestseller_count = df_filtered['Product_Category'].value_counts().values[0]
    
    # Render KPIs in 3 Spalten
    kpi1, kpi2, kpi3 = st.columns(3)
    
    kpi1.metric(
        label="💰 Gesamtumsatz (Markt)",
        value=f"{gesamtumsatz:,.0f} €",
        delta=f"{len(df_filtered)} Transaktionen"
    )
    
    kpi2.metric(
        label="👥 Ø Kundenalter",
        value=f"{durchschnittsalter:.1f} Jahre",
        delta=f"Bereich: {df_filtered['Customer_Age'].min():.0f}–{df_filtered['Customer_Age'].max():.0f} Jahren"
    )
    
    kpi3.metric(
        label="🏆 Bestseller Kategorie",
        value=f"{bestseller}",
        delta=f"{bestseller_count} Verkäufe"
    )
    
    st.divider()
    
    # ===== VISUALISIERUNG 1: HISTOGRAMM =====
    # Umsatz nach Altersgruppe & Geschlecht
    st.subheader("📊 Umsatz nach Altersgruppe & Geschlecht")
    
    # ⭐ WICHTIG: histfunc='sum' ist KRITISCH!
    # Ohne diesen Parameter würde Plotly nur die Anzahl der Zeilen pro Altersgruppe zählen.
    # Mit histfunc='sum' werden die Revenue-Werte korrekt addiert (Euros, nicht Zeilenanzahl).
    fig_histogram = px.histogram(
        df_filtered,
        x='Age_Group',
        y='Revenue',
        color='Customer_Gender',
        barmode='group',
        histfunc='sum',  # ⭐ Summe von Revenue, nicht Zeilenanzahl!
        title='Gesamtumsatz nach Altersgruppe und Geschlecht',
        labels={
            'Revenue': 'Umsatz (€)',
            'Age_Group': 'Altersgruppe',
            'Customer_Gender': 'Geschlecht'
        },
        template='plotly_white',
        color_discrete_map={
            'M': '#1f77b4',  # Blau für Männlich
            'F': '#ff7f0e'   # Orange für Weiblich
        }
    )
    
    fig_histogram.update_layout(
        hovermode='x unified',
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis_title='Altersgruppe',
        yaxis_title='Gesamtumsatz (€)',
        showlegend=True,
        legend=dict(title='Geschlecht', x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig_histogram, use_container_width=True)
    
    st.divider()
    
    # ===== VISUALISIERUNG 2: BOXPLOT =====
    # Gewinnverteilung nach Produktkategorie
    st.subheader("📈 Gewinnverteilung nach Produktkategorie")
    
    fig_boxplot = px.box(
        df_filtered,
        x='Product_Category',
        y='Profit',
        title='Gewinnverteilung nach Produktkategorie',
        labels={
            'Profit': 'Gewinn (€)',
            'Product_Category': 'Produktkategorie'
        },
        template='plotly_white',
        color='Product_Category'
    )
    
    fig_boxplot.update_layout(
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis_title='Produktkategorie',
        yaxis_title='Gewinn (€)',
        showlegend=False
    )
    
    st.plotly_chart(fig_boxplot, use_container_width=True)
    
    st.divider()
    
    # ===== ZUSÄTZLICHE INFORMATIONEN =====
    st.subheader("ℹ️ Datensatz-Informationen")
    
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    info_col1.metric(
        label="Datensätze (gefiltert)",
        value=f"{len(df_filtered):,}"
    )
    
    info_col2.metric(
        label="Zeitraum",
        value=f"{start_date.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')}"
    )
    
    info_col3.metric(
        label="Bundesländer",
        value=f"{len(ausgewaehlte_bundeslaender)}"
    )
    
    info_col4.metric(
        label="Ø Gewinn pro Verkauf",
        value=f"{df_filtered['Profit'].mean():,.2f} €"
    )
    
    # ===== OPTIONAL: DETAILLIERTE DATENÜBERSICHT =====
    with st.expander("🔍 Detaillierte Datenübersicht (Top 20 Transaktionen)"):
        # Zeige die Top-20-Transaktionen nach Umsatz
        display_cols = ['Date', 'State', 'Customer_Age', 'Age_Group', 'Customer_Gender', 
                       'Product_Category', 'Revenue', 'Profit']
        df_display = df_filtered[display_cols].sort_values('Revenue', ascending=False).head(20)
        
        # Formatiere die Datumsspalte für bessere Lesbarkeit
        df_display['Date'] = df_display['Date'].dt.strftime('%d.%m.%Y')
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

# ===== FEHLERBEHANDLUNG =====
except FileNotFoundError:
    st.error(
        f"""
        ❌ **Fehler:** Die Datei `data_benchmark/bike_sales_germany_2026.csv` wurde nicht gefunden.
        
        **Mögliche Lösungen:**
        1. Führe das Notebook `eda_pipeline/bike-store-sales-in-europe.ipynb` aus, um die Daten zu generieren.
        2. Stelle sicher, dass das Verzeichnis `data_benchmark/` im Projekt-Stammverzeichnis existiert.
        3. Überprüfe den Datei-Pfad: `{CSV_PATH}`
        """
    )

except pd.errors.ParserError as e:
    st.error(
        f"""
        ❌ **Fehler beim Lesen der CSV-Datei:** 
        
        {str(e)}
        
        Bitte überprüfe, dass die CSV-Datei in einem gültigen Format vorliegt.
        """
    )

except Exception as e:
    st.error(
        f"""
        ❌ **Ein unerwarteter Fehler ist aufgetreten:**
        
        {str(e)}
        
        Bitte wende dich an den Admin oder überprüfe die Logs.
        """
    )
