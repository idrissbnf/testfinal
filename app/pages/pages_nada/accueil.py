import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from .utils import get_service_name

def show_accueil(filtered_data):
    st.subheader("📈 Tableau de Bord Interactif des Performances Scolaires")
    
    # Métriques pour les services dans des cartes élégantes
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        st.metric("Total des Élèves (Public + Privé)", len(filtered_data))
    with col1:
        st.metric("Total Élèves avec Services", filtered_data['Id_TypeService'].notna().sum())
    with col2:
        admis = filtered_data['resultatFr'].fillna('').str.contains('Admis').sum()
        total = filtered_data['resultatFr'].notna().sum()
        st.metric("Taux d'Admission", f"{admis/total*100:.1f}%" if total > 0 else "N/A")
    with col3:
        abandon = filtered_data['SituationFr'].fillna('').str.contains('Abandon').sum()
        st.metric("Taux d'Abandon", f"{abandon/len(filtered_data)*100:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Nouvelle section: Répartitions générales
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("📊 Répartitions Générales")

    # 1. Répartition par Genre
    genre_counts = filtered_data['GenreFr'].value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Nombre']
    fig_genre = px.pie(
        genre_counts,
        names='Genre',
        values='Nombre',
        title="Répartition par Genre",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # 2. Répartition par Type d'Établissement
    type_counts = filtered_data['Type'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Nombre']
    fig_type = px.pie(
        type_counts,
        names='Type',
        values='Nombre',
        title="Répartition Public vs Privé",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Affichage côte à côte
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_genre, use_container_width=True)
    with col2:
        st.plotly_chart(fig_type, use_container_width=True)

    # 3. Répartition hiérarchique (Localisation -> Genre)
    hierarchy = filtered_data.groupby(['LL_MIL', 'GenreFr']).size().reset_index(name='Nombre')
    fig_hier = px.sunburst(
        hierarchy,
        path=['LL_MIL', 'GenreFr'],
        values='Nombre',
        title="Répartition Hiérarchique (Localisation → Genre)"
    )
    st.plotly_chart(fig_hier, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualisations pour les services
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.subheader("🔍 Analyse des Services")
    cols = st.columns(3)
    
    with cols[0]:
        # Distribution des services les plus fréquents
        service_counts = []
        
        # Compter les occurrences de chaque service
        for services in filtered_data['Services'].dropna():
            for service in services:
                service_counts.append((service, get_service_name(service)))
        
        if service_counts:
            service_df = pd.DataFrame(service_counts, columns=['Service ID', 'Nom Service'])
            service_count = service_df.groupby(['Service ID', 'Nom Service']).size().reset_index(name='Count')
            service_count = service_count.sort_values('Count', ascending=False).head(5)
            
            fig = px.bar(
                service_count, 
                x='Nom Service', 
                y='Count',
                title='<b>Services les Plus Fréquents</b>',
                color='Count',
                color_continuous_scale='viridis',
                labels={'Count': 'Nombre d\'élèves', 'Nom Service': 'Service'}
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=40, b=40),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de service disponible avec les filtres actuels.")
    
    with cols[1]:
        # Réussite par nombre de services
        if 'Services' in filtered_data.columns:
            service_success = filtered_data.groupby('Nb_Services')['Taux_Reussite'].mean().reset_index()
            
            if not service_success.empty and not service_success['Taux_Reussite'].isna().all():
                fig = px.line(
                    service_success,
                    x='Nb_Services',
                    y='Taux_Reussite',
                    title='<b>Taux de Réussite par Nombre de Services</b>',
                    markers=True,
                    line_shape='spline',
                )
                fig.update_layout(
                    yaxis_tickformat='.0%',
                    xaxis_title="Nombre de Services",
                    yaxis_title="Taux de Réussite",
                    margin=dict(l=20, r=20, t=40, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Données insuffisantes pour cette analyse.")
        else:
            st.info("Aucune donnée de service disponible.")
    
    with cols[2]:
        # Distribution des situations des élèves
        situation_counts = filtered_data['SituationFr'].value_counts().reset_index()
        situation_counts.columns = ['Situation', 'Count']
        
        fig = px.pie(
            situation_counts,
            names='Situation',
            values='Count',
            title='<b>Situations des Élèves</b>',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textinfo='percent+label', pull=[0.05]*len(situation_counts))
        fig.update_layout(
            legend_title="Situation",
            margin=dict(l=20, r=20, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Carte d'information supplémentaire
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    
    st.subheader("📊 Comparaison Public vs Privé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Taux de réussite par type d'établissement
        success_by_type = filtered_data.groupby('Type')['Taux_Reussite'].mean().reset_index()
        
        if not success_by_type.empty:
            fig = px.bar(
                success_by_type,
                x='Type',
                y='Taux_Reussite',
                color='Type',
                text_auto='.0%',
                title='<b>Taux de Réussite par Type d\'Établissement</b>',
                color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
            )
            fig.update_layout(
                yaxis_tickformat='.0%',
                xaxis_title="Type d'Établissement",
                yaxis_title="Taux de Réussite",
                margin=dict(l=20, r=20, t=40, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Nombre moyen de services par type d'établissement
        avg_services = filtered_data.groupby('Type')['Nb_Services'].mean().reset_index()
        
        if not avg_services.empty:
            fig = px.bar(
                avg_services,
                x='Type',
                y='Nb_Services',
                color='Type',
                text_auto='.2f',
                title='<b>Nombre Moyen de Services par Type d\'Établissement</b>',
                color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
            )
            fig.update_layout(
                xaxis_title="Type d'Établissement",
                yaxis_title="Nombre Moyen de Services",
                margin=dict(l=20, r=20, t=40, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)