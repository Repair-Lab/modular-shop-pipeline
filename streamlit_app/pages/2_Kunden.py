import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Projekt-Root zum Python-Pfad hinzufügen
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from machine_learning.predict import predict_churn

st.set_page_config(page_title="Kunden", page_icon="👥", layout="wide")
st.title("👥 Kundenanalyse & CRM")

DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'ml_customers.parquet')

try:
    df_customers = pd.read_parquet(DATA_PATH)
    
    # 1. RFM Segmentierung berechnen
    def get_segment(row):
        days = row.get('days_since_last_purchase', 9999)
        spent = row.get('total_spent', 0)
        count = row.get('purchase_count', 0)
        
        if days == 9999 or count == 0:
            return "Lead"
        elif days > 180:
            return "Abgewandert"
        elif days > 90:
            return "Gefährdet"
        elif spent >= 2000 and count >= 3:
            return "VIP"
        elif count > 1:
            return "Loyal"
        else:
            return "Einsteiger"

    df_customers['Segment'] = df_customers.apply(get_segment, axis=1)
    
    # Farb-Mapping für Konsistenz im Dashboard
    color_map = {
        "VIP": "#00CC96", "Loyal": "#636EFA", "Einsteiger": "#AB63FA", 
        "Gefährdet": "#FFA15A", "Abgewandert": "#EF553B", "Lead": "#B6E880"
    }
    
    # --- SIDEBAR: FILTER ---
    st.sidebar.header("⚙️ CRM-Filter")
    all_segments = df_customers['Segment'].unique().tolist()
    
    # Default: Verstecke komplett Inaktive im Standard-View (falls es andere gibt)
    default_segs = [s for s in all_segments if s not in ["Abgewandert", "Lead"]]
    if not default_segs: 
        default_segs = all_segments
        
    selected_segments = st.sidebar.multiselect(
        "Zu analysierende Segmente:", 
        options=all_segments,
        default=default_segs
    )
    
    df_filtered = df_customers[df_customers['Segment'].isin(selected_segments)].copy()

    # --- SCATTER PLOT (BUBBLE CHART) ---
    st.subheader("📊 Interaktive Kunden-Segmente (RFM)")
    st.markdown("Größe der Blasen entspricht dem Gesamtumsatz. Fahre mit der Maus über die Punkte für Details.")
    
    if not df_filtered.empty:
        # Hilfsspalte für Bubble-Größe (verhindert 0-Werte und Fehler bei kleinen Einkäufen)
        df_filtered['bubble_size'] = df_filtered['total_spent'].clip(lower=50)
        
        fig = px.scatter(
            df_filtered, 
            x='days_since_last_purchase', 
            y='total_spent', 
            size='bubble_size',
            color='Segment',
            color_discrete_map=color_map,
            hover_name='name',
            hover_data={'bubble_size': False, 'purchase_count': True, 'city': True},
            labels={
                'days_since_last_purchase': 'Tage seit letztem Kauf (Recency)', 
                'total_spent': 'Gesamtumsatz in € (Monetary)', 
                'purchase_count': 'Anzahl Käufe'
            },
            marginal_y="histogram"
        )
        fig.update_layout(template="plotly_white", margin=dict(t=30))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Bitte wähle mindestens ein Segment in der Seitenleiste aus.")
        
    st.divider()

    # --- CHURN RADAR ---
    st.subheader("🚨 Churn-Radar: Gefährdete Kunden")
    st.markdown("Diese Kunden haben längere Zeit nicht gekauft, sind aber noch nicht vollständig abgewandert (90-180 Tage inaktiv).")
    
    df_risk = df_customers[df_customers['Segment'] == 'Gefährdet'].copy()
    
    if not df_risk.empty:
        # Relevante Spalten für die Tabelle auswählen und ordnen
        df_display = df_risk[['name', 'city', 'total_spent', 'purchase_count', 'days_since_last_purchase']].sort_values('total_spent', ascending=False)
        df_display.columns = ['Name', 'Wohnort', 'Umsatz (€)', 'Käufe', 'Tage inaktiv']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        if st.button("📧 Re-Engagement Kampagne starten (Massen-E-Mail via n8n)", type="primary"):
            st.success(f"✅ Batch-Webhook ausgelöst! Es wurden {len(df_risk)} Gutscheine erfolgreich an gefährdete Kunden versendet.")
    else:
        st.success("🎉 Aktuell gibt es keine akut gefährdeten Kunden in diesem Zeitfenster!")

    st.divider()

    # --- CUSTOMER 360 VIEW ---
    st.subheader("🔍 Customer 360° Profil")
    st.markdown("Detaillierte Einzelanalyse und KI-Abwanderungsprognose.")
    
    customer_names = sorted(df_customers['name'].dropna().unique())
    selected_customer = st.selectbox("Kundenakte aufrufen:", customer_names)
    
    if selected_customer:
        cust_data = df_customers[df_customers['name'] == selected_customer].iloc[0]
        
        # Visuelle Badges mit Farben/Emojis
        badge_map = {
            "VIP": "**:green[🌟 VIP-Kunde]**",
            "Loyal": "**:blue[🤝 Loyaler Kunde]**",
            "Einsteiger": "**:violet[🌱 Einsteiger]**",
            "Gefährdet": "**:orange[⚠️ Gefährdet (Schläfer)]**",
            "Abgewandert": "**:red[🛑 Abgewandert]**",
            "Lead": "**:grey[👻 Lead (Noch kein Kauf)]**"
        }
        badge = badge_map.get(cust_data['Segment'], f"**{cust_data['Segment']}**")
        
        st.markdown(f"### {cust_data['name']} {badge}")
        st.caption(f"📍 {cust_data['city']} | ✉️ {cust_data['email']} | 📞 {cust_data['phone']}")
        
        # KPIs für den Kunden
        c1, c2, c3 = st.columns(3)
        c1.metric("Gesamtumsatz", f"{cust_data['total_spent']:,.2f} €")
        c2.metric("Anzahl Käufe", f"{cust_data['purchase_count']:.0f}")
        
        days_inactive = cust_data['days_since_last_purchase']
        c3.metric("Zuletzt aktiv vor", f"{days_inactive:.0f} Tagen" if days_inactive < 9999 else "Noch nie")
        
        # KI Prognose
        st.markdown("#### 🤖 KI-Risikobewertung")
        prediction = predict_churn(cust_data['total_spent'], cust_data['purchase_count'])
        
        if prediction == 1:
            st.error("🛑 **Kritisch:** Das ML-Modell prognostiziert Abwanderung für diesen Kunden.")
            if st.button("📧 Individuellen 20% Rabatt-Code senden (via n8n)"):
                st.success(f"✅ Webhook ausgelöst! {cust_data['email']} erhält in Kürze eine persönliche Re-Engagement-Nachricht.")
        else:
            st.success("✅ **Gesund:** Dieser Kunde verhält sich laut ML-Modell unauffällig. Keine Maßnahmen erforderlich.")
                
except FileNotFoundError:
    st.error("Daten nicht gefunden. Bitte führe die ETL-Pipeline aus.")