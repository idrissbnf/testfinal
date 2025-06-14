import streamlit as st
import plotly.express as px

def create_provincial_tab(df):
    """Crée l'onglet Analyse Provinciale"""
    st.header("📍 Analyse Provinciale")
    
    # Statistiques par province
    st.subheader("🏛️ Statistiques par province")
    stats_province = df.groupby('ll_com').agg({
        'NOM_ETABL': 'nunique', 'id_eleve': 'nunique'
    }).reset_index()
    stats_province.columns = ['Province', 'Établissements', 'Élèves']
    stats_province = stats_province.sort_values('Établissements', ascending=False)
    st.dataframe(stats_province, use_container_width=True)
    
    # Répartition urbain/rural par province
    st.subheader("🌆 Répartition urbain/rural par province")
    province_milieu = df.groupby(['ll_com', 'LL_MIL']).agg({
        'NOM_ETABL': 'nunique', 'id_eleve': 'nunique'
    }).reset_index()
    province_milieu.columns = ['Province', 'Milieu', 'Établissements', 'Élèves']
    
    fig_province = px.bar(province_milieu, x='Province', y='Établissements', color='Milieu',
                         title="Nombre d'établissements par province et milieu")
    fig_province.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_province, use_container_width=True)
    st.dataframe(province_milieu, use_container_width=True)