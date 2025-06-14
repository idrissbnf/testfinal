import streamlit as st
import plotly.express as px

def create_students_tab(df):
    """Crée l'onglet Analyse Élèves"""
    st.header("👥 Analyse des Élèves")
    
    # Élèves par niveau
    st.subheader("📚 Répartition des élèves par niveau")
    niveau_stats = df.groupby(['LL_CYCLE', 'libformatFr'])['id_eleve'].nunique().reset_index()
    niveau_stats.columns = ['Cycle', 'Niveau', 'Nombre_Eleves']
    
    fig_niveau = px.bar(niveau_stats, x='Niveau', y='Nombre_Eleves', color='Cycle',
                       title="Nombre d'élèves par niveau et cycle")
    fig_niveau.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_niveau, use_container_width=True)
    st.dataframe(niveau_stats, use_container_width=True)
    
    # Élèves par type d'établissement
    st.subheader("🏛️ Répartition des élèves par type d'établissement")
    eleves_par_type = df.groupby(['typeEtab', 'LL_CYCLE'])['id_eleve'].nunique().reset_index()
    eleves_par_type.columns = ['Type_Etablissement', 'Cycle', 'Nombre_Eleves']
    eleves_par_type['Type_Etablissement'] = eleves_par_type['Type_Etablissement'].replace({
        'public': 'Public', 'privé': 'Privé'
    })
    
    fig_eleves_type = px.bar(eleves_par_type, x='Type_Etablissement', y='Nombre_Eleves', color='Cycle',
                            title="Nombre d'élèves par type d'établissement et cycle")
    st.plotly_chart(fig_eleves_type, use_container_width=True)
    st.dataframe(eleves_par_type, use_container_width=True)