import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .utils import get_service_name

def show_statistiques(filtered_data):
    """
    Affiche la page des statistiques comparatives entre établissements publics et privés
    """
    st.subheader("📈 Analyses Statistiques Comparatives")
    
    # Séparation des données de service
    service_public = filtered_data[filtered_data["Type"] == "Public"]
    service_prive = filtered_data[filtered_data["Type"] == "Privé"]
    
    # Création des boutons pour la navigation
    st.markdown("### Sélectionnez une analyse :")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Statistiques Services", use_container_width=True):
            st.session_state.selected_tab = "tab1"
    
    with col2:
        if st.button("📈 Comparaisons Détaillées", use_container_width=True):
            st.session_state.selected_tab = "tab2"
    
    with col3:
        if st.button("🎯 Analyses Avancées", use_container_width=True):
            st.session_state.selected_tab = "tab3"
    
    # Initialiser la session state si elle n'existe pas
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "tab1"
    
    st.markdown("---")
    
    # Affichage conditionnel basé sur le bouton sélectionné
    if st.session_state.selected_tab == "tab1":
        st.subheader("Statistiques des Services")
        
        # Métriques services
        cols = st.columns(2)
        
        with cols[0]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            with st.expander("🔵 PUBLIC - Statistiques Services", expanded=True):
                if not service_public.empty:
                    # Calculer les métriques de service pour les établissements publics
                    st.metric("Nombre d'élèves", len(service_public))
                    
                    # Calculer le taux de service (pourcentage d'élèves ayant au moins un service)
                    has_service = service_public['Id_TypeService'].notna().sum()
                    service_rate = has_service/len(service_public)*100 if len(service_public) > 0 else 0
                    st.metric("Élèves avec services", f"{has_service} ({service_rate:.1f}%)")
                    
                    # Nombre moyen de services par élève
                    if 'Services' in service_public.columns and 'Nb_Services' in service_public.columns:
                        avg_services = service_public['Nb_Services'].mean()
                        st.metric("Moyenne services/élève", f"{avg_services:.2f}")
                    
                    # Taux de réussite pour les élèves avec services
                    if 'Taux_Reussite' in service_public.columns:
                        with_service = service_public[service_public['Id_TypeService'].notna()]
                        if not with_service.empty and not with_service['Taux_Reussite'].isna().all():
                            reussite_avec_service = with_service['Taux_Reussite'].mean() * 100
                            st.metric("Taux réussite avec services", f"{reussite_avec_service:.1f}%")
                        else:
                            st.metric("Taux réussite avec services", "N/A")
                else:
                    st.info("Aucune donnée de service public disponible")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            with st.expander("🔴 PRIVÉ - Statistiques Services", expanded=True):
                if not service_prive.empty:
                    # Calculer les métriques de service pour les établissements privés
                    st.metric("Nombre d'élèves", len(service_prive))
                    
                    # Calculer le taux de service (pourcentage d'élèves ayant au moins un service)
                    has_service = service_prive['Id_TypeService'].notna().sum()
                    service_rate = has_service/len(service_prive)*100 if len(service_prive) > 0 else 0
                    st.metric("Élèves avec services", f"{has_service} ({service_rate:.1f}%)")
                    
                    # Nombre moyen de services par élève
                    if 'Services' in service_prive.columns and 'Nb_Services' in service_prive.columns:
                        avg_services = service_prive['Nb_Services'].mean()
                        st.metric("Moyenne services/élève", f"{avg_services:.2f}")
                    
                    # Taux de réussite pour les élèves avec services
                    if 'Taux_Reussite' in service_prive.columns:
                        with_service = service_prive[service_prive['Id_TypeService'].notna()]
                        if not with_service.empty and not with_service['Taux_Reussite'].isna().all():
                            reussite_avec_service = with_service['Taux_Reussite'].mean() * 100
                            st.metric("Taux réussite avec services", f"{reussite_avec_service:.1f}%")
                        else:
                            st.metric("Taux réussite avec services", "N/A")
                else:
                    st.info("Aucune donnée de service privé disponible")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparaison des services entre public et privé
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Comparaison des Services Public vs Privé")
        
        # Extraction des identifiants de service uniques
        all_services = []
        for services in filtered_data['Services'].dropna():
            if isinstance(services, list):
                all_services.extend(services)
        unique_services = sorted(set(all_services))
        
        if unique_services:
            # Préparation des données pour le graphique
            service_comparison = []
            
            for service_id in unique_services:
                # Compter pour le public
                count_public = sum(1 for services in service_public['Services'].dropna() 
                                 if isinstance(services, list) and service_id in services)
                
                # Compter pour le privé
                count_prive = sum(1 for services in service_prive['Services'].dropna() 
                                if isinstance(services, list) and service_id in services)
                
                service_comparison.append({
                    'Service ID': service_id,
                    'Nom Service': get_service_name(service_id),
                    'Public': count_public,
                    'Privé': count_prive
                })
            
            service_df = pd.DataFrame(service_comparison)
            
            # Melt pour préparer les données pour le graphique
            service_df_melted = pd.melt(
                service_df, 
                id_vars=['Service ID', 'Nom Service'],
                value_vars=['Public', 'Privé'],
                var_name='Type',
                value_name='Count'
            )
            
            # Créer le graphique
            fig = px.bar(
                service_df_melted,
                x='Nom Service',
                y='Count',
                color='Type',
                barmode='group',
                title='Distribution des Services par Type d\'Établissement',
                color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'},
                labels={'Count': 'Nombre d\'élèves', 'Nom Service': 'Service'}
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de service disponible pour cette comparaison")
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.selected_tab == "tab2":
        st.subheader("📈 Comparaisons Détaillées")
        
        # Graphiques de comparaison détaillés
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("Taux de Réussite par Genre")
            
            # Analyse par genre et type d'établissement
            genre_success = filtered_data.groupby(['Type', 'GenreFr'])['Taux_Reussite'].mean().reset_index()
            
            if not genre_success.empty and not genre_success['Taux_Reussite'].isna().all():
                fig = px.bar(
                    genre_success,
                    x='GenreFr',
                    y='Taux_Reussite',
                    color='Type',
                    barmode='group',
                    title='Taux de Réussite par Genre et Type d\'Établissement',
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'},
                    labels={'Taux_Reussite': 'Taux de Réussite', 'GenreFr': 'Genre'}
                )
                fig.update_layout(yaxis_tickformat='.0%')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Données insuffisantes pour cette analyse")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("Répartition par Localisation")
            
            # Analyse par localisation
            lieu_repartition = filtered_data.groupby(['Type', 'LL_MIL']).size().reset_index(name='Count')
            
            if not lieu_repartition.empty:
                fig = px.bar(
                    lieu_repartition,
                    x='LL_MIL',
                    y='Count',
                    color='Type',
                    barmode='group',
                    title='Répartition des Élèves par Localisation',
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'},
                    labels={'Count': 'Nombre d\'élèves', 'LL_MIL': 'Localisation'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Données insuffisantes pour cette analyse")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphique de corrélation services-réussite
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Corrélation Services et Réussite")
        
        if 'Nb_Services' in filtered_data.columns and 'Taux_Reussite' in filtered_data.columns:
            correlation_data = filtered_data[['Nb_Services', 'Taux_Reussite', 'Type']].dropna()
            
            if not correlation_data.empty:
                fig = px.scatter(
                    correlation_data,
                    x='Nb_Services',
                    y='Taux_Reussite',
                    color='Type',
                    title='Corrélation entre Nombre de Services et Taux de Réussite',
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'},
                    labels={
                        'Nb_Services': 'Nombre de Services',
                        'Taux_Reussite': 'Taux de Réussite'
                    },
                    trendline="ols"
                )
                fig.update_layout(yaxis_tickformat='.0%')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Données insuffisantes pour l'analyse de corrélation")
        else:
            st.info("Colonnes nécessaires non disponibles pour l'analyse de corrélation")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.selected_tab == "tab3":
        st.subheader("🎯 Analyses Avancées")
        
        # Tableau récapitulatif
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Tableau Récapitulatif Comparatif")
        
        # Créer un tableau de comparaison
        summary_data = []
        
        for type_etablissement in ['Public', 'Privé']:
            data_type = filtered_data[filtered_data['Type'] == type_etablissement]
            
            if not data_type.empty:
                # Calculs des métriques
                total_eleves = len(data_type)
                eleves_avec_services = data_type['Id_TypeService'].notna().sum()
                taux_service = (eleves_avec_services / total_eleves * 100) if total_eleves > 0 else 0
                
                # Taux de réussite moyen
                taux_reussite = data_type['Taux_Reussite'].mean() * 100 if 'Taux_Reussite' in data_type.columns else 0
                
                # Nombre moyen de services
                nb_services_moyen = data_type['Nb_Services'].mean() if 'Nb_Services' in data_type.columns else 0
                
                # Taux d'abandon
                taux_abandon = (data_type['SituationFr'].fillna('').str.contains('Abandon').sum() / total_eleves * 100) if total_eleves > 0 else 0
                
                summary_data.append({
                    'Type': type_etablissement,
                    'Total Élèves': total_eleves,
                    'Élèves avec Services': eleves_avec_services,
                    'Taux de Service (%)': f"{taux_service:.1f}%",
                    'Taux de Réussite (%)': f"{taux_reussite:.1f}%",
                    'Nb Services Moyen': f"{nb_services_moyen:.2f}",
                    'Taux d\'Abandon (%)': f"{taux_abandon:.1f}%"
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour le tableau récapitulatif")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Analyse des situations critiques
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Situations Critiques")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Élèves sans services
            sans_service = filtered_data[filtered_data['Id_TypeService'].isna() | (filtered_data['Id_TypeService'] == '')]
            
            if not sans_service.empty:
                sans_service_by_type = sans_service['Type'].value_counts()
                
                fig = px.pie(
                    values=sans_service_by_type.values,
                    names=sans_service_by_type.index,
                    title='Élèves Sans Services par Type',
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tous les élèves ont au moins un service")
        
        with col2:
            # Élèves en situation d'abandon
            abandon = filtered_data[filtered_data['SituationFr'].fillna('').str.contains('Abandon')]
            
            if not abandon.empty:
                abandon_by_type = abandon['Type'].value_counts()
                
                fig = px.pie(
                    values=abandon_by_type.values,
                    names=abandon_by_type.index,
                    title='Élèves en Abandon par Type',
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun élève en situation d'abandon")
        
        st.markdown('</div>', unsafe_allow_html=True)