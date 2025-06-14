import streamlit as st
import plotly.express as px

def create_overview_tab(df):
    """Crée l'onglet Vue d'ensemble"""
    st.header("📊 Vue d'ensemble des données")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("🏫 Établissements", df['NOM_ETABL'].nunique()),
        ("👥 Élèves", df['id_eleve'].nunique()),
        ("🏛️ Classes", df['id_classe'].nunique()),
        ("🏛️ Types d'Établ.", df['libformatFr'].nunique())
    ]
    
    for i, (label, value) in enumerate(metrics):
        [col1, col2, col3, col4][i].metric(label, value)
    
    # Répartition urbain/rural
    st.subheader("🌆 Répartition Urbain/Rural")
    etab_par_milieu = df.groupby('LL_MIL')['NOM_ETABL'].nunique()
    
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(values=etab_par_milieu.values, names=etab_par_milieu.index,
                        title="Répartition des établissements par milieu")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        milieu_stats = df.groupby('LL_MIL').agg({
            'NOM_ETABL': 'nunique', 'id_eleve': 'nunique'
        }).rename(columns={'NOM_ETABL': 'Établissements', 'id_eleve': 'Élèves'})
        st.dataframe(milieu_stats)
    
    # Répartition par type et cycle
    for title, group_col, count_col, chart_title in [
        ("🏛️ Répartition par Type d'Établissement", 'libformatFr', 'NOM_ETABL', "Nombre d'établissements par type"),
        ("🎓 Répartition par Cycle", 'LL_CYCLE', 'id_eleve', "Nombre d'élèves par cycle")
    ]:
        st.subheader(title)
        stats = df.groupby(group_col).agg({'NOM_ETABL': 'nunique', 'id_eleve': 'nunique'}).rename(
            columns={'NOM_ETABL': 'Établissements', 'id_eleve': 'Élèves'})
        
        fig = px.bar(x=stats.index, y=stats[count_col.replace('NOM_ETABL', 'Établissements').replace('id_eleve', 'Élèves')],
                    title=chart_title)
        st.plotly_chart(fig, use_container_width=True)
        if group_col == 'LL_CYCLE':
            st.dataframe(stats)