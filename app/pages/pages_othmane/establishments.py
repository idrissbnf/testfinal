import streamlit as st
import plotly.express as px

def create_establishments_tab(df):
    """Crée l'onglet Analyse Établissements"""
    st.header("🏫 Analyse des Établissements")
    
    # Classes par établissement
    st.subheader("📚 Nombre de classes par établissement")
    classes_par_etab = df.groupby(['NOM_ETABL', 'LL_MIL'])['id_classe'].nunique().reset_index()
    classes_par_etab.columns = ['Nom_Etablissement', 'Milieu', 'Nombre_Classes']
    
    fig_classes = px.bar(classes_par_etab, x='Nom_Etablissement', y='Nombre_Classes', color='Milieu',
                        title="Nombre de classes par établissement et milieu")
    fig_classes.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_classes, use_container_width=True)
    
    # Statistiques détaillées
    st.subheader("📊 Statistiques détaillées par établissement")
    stats_etablissement = df.groupby(['NOM_ETABL', 'LL_MIL', 'll_com']).agg({
        'id_classe': 'nunique', 'id_eleve': 'nunique'
    }).reset_index()
    stats_etablissement.columns = ['Nom Établissement', 'Milieu', 'Commune', 'Classes', 'Élèves']
    st.dataframe(stats_etablissement, use_container_width=True)
    
    # Analyse par type
    st.subheader("🏛️ Analyse par type d'établissement")
    type_analysis = df.groupby(['libformatFr', 'LL_MIL']).agg({
        'NOM_ETABL': 'nunique', 'id_eleve': 'nunique', 'id_classe': 'nunique'
    }).reset_index()
    type_analysis.columns = ['Type', 'Milieu', 'Établissements', 'Élèves', 'Classes']
    
    fig_type_milieu = px.bar(type_analysis, x='Type', y='Établissements', color='Milieu',
                            title="Nombre d'établissements par type et milieu")
    fig_type_milieu.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_type_milieu, use_container_width=True)
    st.dataframe(type_analysis, use_container_width=True)