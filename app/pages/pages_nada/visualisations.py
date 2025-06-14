import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .utils import get_service_name

def show_visualisations(filtered_data):
    """Affichage de la page des visualisations interactives"""
    
    st.subheader("📊 Visualisations Interactives")
    
    # Sélection du type de visualisation avec des boutons
    st.markdown("**Choisir le type d'analyse:**")
    col1, col2 = st.columns(2)
    
    with col1:
        services_button = st.button("📋 Analyse des Services", use_container_width=True)
    
    with col2:
        results_button = st.button("🎓 Analyse des Résultats", use_container_width=True)
    
    # Initialiser le state si nécessaire
    if 'viz_type' not in st.session_state:
        st.session_state.viz_type = "📋 Analyse des Services"
    
    # Mettre à jour le state selon le bouton cliqué
    if services_button:
        st.session_state.viz_type = "📋 Analyse des Services"
    elif results_button:
        st.session_state.viz_type = "🎓 Analyse des Résultats"
    
    viz_type = st.session_state.viz_type

    if viz_type == "📋 Analyse des Services":
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        # Sélection du type de visualisation des services
        viz_service_type = st.selectbox(
            "Type de Visualisation des Services",
            [
                "📊 Distribution des Services",
                "📈 Impact sur la Réussite",
                "🏫 Analyse par Type d'Établissement",
                "👥 Répartition Démographique",
                "🔄 Tendances Temporelles"
            ],
            key="viz_type_services"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
        # 1. DISTRIBUTION DES SERVICES
        if "Distribution des Services" in viz_service_type:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📊 Analyse de la Distribution des Services")
        
            # Extraire tous les services pour analyse
            all_services = []
            for services in filtered_data['Services'].dropna():
                for service in services:
                    all_services.append((service, get_service_name(service)))
        
            if all_services:
                col1, col2 = st.columns(2)
            
                with col1:
                    # Distribution des services par fréquence - Top 10
                    service_df = pd.DataFrame(all_services, columns=['Service ID', 'Nom Service'])
                    service_count = service_df.groupby(['Service ID', 'Nom Service']).size().reset_index(name='Fréquence')
                    service_count = service_count.sort_values('Fréquence', ascending=False).head(10)
                
                    fig = px.bar(
                        service_count,
                        x='Nom Service',
                        y='Fréquence',
                        title='Top 10 des Services les Plus Utilisés',
                        color='Fréquence',
                        color_continuous_scale='viridis',
                        labels={'Fréquence': 'Nombre d\'utilisations'}
                    )
                    fig.update_layout(
                        xaxis_title="Service",
                        yaxis_title="Nombre d'élèves",
                        xaxis_tickangle=-45,
                        margin=dict(l=20, r=20, t=40, b=80)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    # Distribution du nombre de services par élève
                    filtered_data['Nb_Services'] = filtered_data['Services'].apply(len)
                
                    fig = px.histogram(
                        filtered_data,
                        x='Nb_Services',
                        color='Type',
                        marginal="box",
                        nbins=10,
                        title='Distribution du Nombre de Services par Élève',
                        labels={'Nb_Services': 'Nombre de Services par Élève'},
                        opacity=0.7,
                        barmode='overlay',
                        color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                    )
                    fig.update_layout(
                        bargap=0.1,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                # Services combinés - Analyse des combinaisons fréquentes
                st.subheader("🔄 Combinaisons de Services Fréquentes")
            
                # Extraction des combinaisons de services
                def get_service_combinations(services_list, max_length=2):
                    if len(services_list) < max_length:
                        return []
                    result = []
                    for idx, a in enumerate(services_list):
                        for b in services_list[idx+1:]:
                            # Trier pour ne pas compter (a,b) et (b,a) comme différents
                            pair = tuple(sorted([a, b]))
                            result.append(pair)
                    return result
            
                all_combinations = []
                for services in filtered_data['Services'].dropna():
                    if len(services) >= 2:
                        all_combinations.extend(get_service_combinations(services))
            
                if all_combinations:
                    combo_counts = pd.Series(all_combinations).value_counts().reset_index()
                    combo_counts.columns = ['Combinaison', 'Fréquence']
                
                    # Ajouter les noms des services
                    combo_counts['Nom Combo'] = combo_counts['Combinaison'].apply(
                        lambda x: f"{get_service_name(x[0])} et {get_service_name(x[1])}"
                    )
                
                    fig = px.bar(
                        combo_counts.head(8),
                        x='Nom Combo',
                        y='Fréquence',
                        title='Combinaisons de Services les Plus Courantes',
                        color='Fréquence',
                        color_continuous_scale='sunset'
                    )
                    fig.update_layout(
                        xaxis_tickangle=-45,
                        margin=dict(l=20, r=20, t=40, b=100)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas assez de données pour analyser les combinaisons de services.")
            else:
                st.warning("Aucune donnée de service disponible pour cette analyse.")
            st.markdown('</div>', unsafe_allow_html=True)
    
        # 2. IMPACT SUR LA RÉUSSITE
        elif "Impact sur la Réussite" in viz_service_type:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📈 Analyse de l'Impact des Services sur la Réussite")
        
            # Extraire les services uniques
            all_services = []
            for services in filtered_data['Services'].dropna():
                all_services.extend(services)
            unique_services = sorted(set(all_services))
        
            if unique_services:
                col1, col2 = st.columns(2)
            
                with col1:
                    # Taux de réussite par nombre de services
                    filtered_data['Nb_Services'] = filtered_data['Services'].apply(len)
                    success_by_count = filtered_data.groupby('Nb_Services')['Taux_Reussite'].agg(['mean', 'count']).reset_index()
                    success_by_count.columns = ['Nombre de Services', 'Taux de Réussite', 'Nombre d\'Élèves']
                
                    # Créer un graphique avec taille des points proportionnelle au nombre d'élèves
                    fig = px.scatter(
                        success_by_count,
                        x='Nombre de Services',
                        y='Taux de Réussite',
                        size='Nombre d\'Élèves',
                        color='Taux de Réussite',
                        hover_data=['Nombre d\'Élèves'],
                        color_continuous_scale='rdylgn',
                        title='Relation entre Nombre de Services et Réussite',
                        size_max=40
                    )
                    fig.update_layout(
                        yaxis_tickformat='.0%',
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                
                    # Ajouter une ligne de tendance
                    fig.add_traces(
                        px.line(
                            success_by_count, 
                            x='Nombre de Services', 
                            y='Taux de Réussite'
                        ).data[0]
                    )
                
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    # Impact de chaque service sur le taux de réussite
                    service_impact = []
                
                    for service_id in unique_services:
                        # Élèves avec ce service
                        with_service = filtered_data[filtered_data['Services'].apply(
                            lambda x: service_id in x if isinstance(x, list) else False)]
                        # Élèves sans ce service
                        without_service = filtered_data[filtered_data['Services'].apply(
                            lambda x: service_id not in x if isinstance(x, list) else True)]
                    
                        # Calculer les taux de réussite
                        if not with_service.empty and not without_service.empty:
                            taux_with = with_service['Taux_Reussite'].mean()
                            taux_without = without_service['Taux_Reussite'].mean()
                            difference = taux_with - taux_without
                            count = len(with_service)
                        
                            service_impact.append({
                                'Service ID': service_id,
                                'Nom Service': get_service_name(service_id),
                                'Impact': difference,
                                'Nombre d\'Élèves': count,
                                'Taux Avec': taux_with
                            })
                
                    if service_impact:
                        impact_df = pd.DataFrame(service_impact)
                    
                        fig = px.bar(
                            impact_df.sort_values('Impact', ascending=False),
                            x='Nom Service',
                            y='Impact',
                            color='Impact',
                            color_continuous_scale='RdBu_r',
                            title='Impact des Services sur le Taux de Réussite',
                            hover_data=['Nombre d\'Élèves', 'Taux Avec']
                        )
                        fig.update_layout(
                            yaxis_tickformat='.0%',
                            xaxis_tickangle=-45,
                            margin=dict(l=20, r=20, t=40, b=80)
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
                # Tableau interactif d'impact des services
                if 'impact_df' in locals() and not impact_df.empty:
                    st.subheader("📋 Tableau Détaillé d'Impact des Services")
                
                    # Formater les données pour l'affichage
                    display_impact = impact_df.copy()
                    display_impact['Impact'] = display_impact['Impact'].apply(lambda x: f"{x*100:+.1f}%")
                    display_impact['Taux Avec'] = display_impact['Taux Avec'].apply(lambda x: f"{x*100:.1f}%")
                
                    # Trier par impact
                    display_impact = display_impact.sort_values('Nombre d\'Élèves', ascending=False)
                
                    # Afficher le tableau avec une option de recherche
                    search = st.text_input("Rechercher un service")
                
                    if search:
                        filtered_impact = display_impact[
                            display_impact['Nom Service'].str.contains(search, case=False)
                        ]
                    else:
                        filtered_impact = display_impact
                
                    st.dataframe(filtered_impact, use_container_width=True)
            else:
                st.warning("Données insuffisantes pour analyser l'impact des services sur la réussite.")
            st.markdown('</div>', unsafe_allow_html=True)
    
        # 3. ANALYSE PAR TYPE D'ÉTABLISSEMENT  
        elif "Analyse par Type d'Établissement" in viz_service_type:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🏫 Comparaison des Services par Type d'Établissement")
        
            # Extraire tous les services pour l'analyse
            all_services = []
            for services in filtered_data['Services'].dropna():
                all_services.extend(services)
            unique_services = sorted(set(all_services))
        
            if unique_services:
                # Créer des dataframes séparés par type d'établissement
                private_data = filtered_data[filtered_data['Type'] == 'Privé']
                public_data = filtered_data[filtered_data['Type'] == 'Public']
            
                # Distribution des services par type d'établissement
                col1, col2 = st.columns(2)
            
                with col1:
                    # Nombre moyen de services par élève
                    avg_services = filtered_data.groupby('Type')['Services'].apply(
                        lambda x: sum(len(s) for s in x if isinstance(s, list)) / len(x)
                    ).reset_index()
                    avg_services.columns = ['Type d\'Établissement', 'Moyenne Services/Élève']
                
                    fig = px.bar(
                        avg_services,
                        x='Type d\'Établissement',
                        y='Moyenne Services/Élève',
                        color='Type d\'Établissement',
                        text_auto='.2f',
                        title='Nombre Moyen de Services par Élève',
                        labels={'Moyenne Services/Élève': 'Services par Élève (moyenne)'},
                        color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                    )
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    # Taux de couverture des services (% d'élèves ayant au moins un service)
                    coverage = filtered_data.groupby('Type')['Id_TypeService'].apply(
                        lambda x: x.notna().sum() / len(x) * 100
                    ).reset_index()
                    coverage.columns = ['Type d\'Établissement', 'Taux de Couverture (%)']
                
                    fig = px.bar(
                        coverage,
                        x='Type d\'Établissement',
                        y='Taux de Couverture (%)',
                        color='Type d\'Établissement',
                        text_auto='.1f',
                        title='Pourcentage d\'Élèves Bénéficiant de Services',
                        labels={'Taux de Couverture (%)': '% Élèves avec Services'},
                        color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                    )
                    fig.update_layout(
                        yaxis_range=[0, 100],
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                # Comparaison des services spécifiques utilisés
                st.subheader("📊 Utilisation des Services Spécifiques")
            
                # Compter les occurrences de chaque service par type d'établissement
                service_counts_by_type = {'Privé': {}, 'Public': {}}
            
                for type_etab, df in [('Privé', private_data), ('Public', public_data)]:
                    services_list = []
                    for services in df['Services'].dropna():
                        services_list.extend(services)
                    for service in unique_services:
                        service_counts_by_type[type_etab][service] = services_list.count(service)
            
                # Préparer les données pour le graphique
                comparison_data = []
                for service in unique_services:
                    comparison_data.append({
                        'Service ID': service,
                        'Nom Service': get_service_name(service),
                        'Privé': service_counts_by_type['Privé'].get(service, 0),
                        'Public': service_counts_by_type['Public'].get(service, 0)
                    })
            
                comparison_df = pd.DataFrame(comparison_data)
            
                # Transformer pour Plotly
                melted_df = pd.melt(
                    comparison_df,
                    id_vars=['Service ID', 'Nom Service'],
                    value_vars=['Privé', 'Public'],
                    var_name='Type d\'Établissement',
                    value_name='Nombre d\'Élèves'
                )
            
                fig = px.bar(
                    melted_df,
                    x='Nom Service',
                    y='Nombre d\'Élèves',
                    color='Type d\'Établissement',
                    barmode='group',
                    title='Comparaison de l\'Utilisation des Services par Type d\'Établissement',
                    labels={'Nombre d\'Élèves': 'Élèves utilisant le service'},
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                )
                fig.update_layout(
                    xaxis_tickangle=-45,
                    margin=dict(l=20, r=20, t=40, b=80)
                )
                st.plotly_chart(fig, use_container_width=True)
            
                # Efficacité comparative des services
                st.subheader("🎯 Efficacité Comparative des Services")
            
                # Calculer l'efficacité des services par type d'établissement
                service_efficacy = []
            
                for service in unique_services:
                    for type_etab, df in [('Privé', private_data), ('Public', public_data)]:
                        # Élèves avec ce service
                        with_service = df[df['Services'].apply(
                            lambda x: service in x if isinstance(x, list) else False)]
                    
                        if len(with_service) > 0:
                            success_rate = with_service['Taux_Reussite'].mean()
                            service_efficacy.append({
                                'Service ID': service,
                                'Nom Service': get_service_name(service),
                                'Type': type_etab,
                                'Taux de Réussite': success_rate,
                                'Nombre d\'Élèves': len(with_service)
                            })
            
                if service_efficacy:
                    efficacy_df = pd.DataFrame(service_efficacy)
                    efficacy_df = efficacy_df[efficacy_df['Nombre d\'Élèves'] >= 5]  # Filtrer pour plus de fiabilité
                
                    if not efficacy_df.empty:
                        fig = px.scatter(
                            efficacy_df,
                            x='Nom Service',
                            y='Taux de Réussite',
                            color='Type',
                            size='Nombre d\'Élèves',
                            hover_data=['Nombre d\'Élèves'],
                            title='Efficacité des Services par Type d\'Établissement',
                            labels={'Taux de Réussite': 'Taux de Réussite'},
                            size_max=30,
                            color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                        )
                        fig.update_layout(
                            yaxis_tickformat='.0%',
                            xaxis_tickangle=-45,
                            margin=dict(l=20, r=20, t=40, b=80)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Pas assez de données pour comparer l'efficacité des services.")
                else:
                    st.info("Données insuffisantes pour l'analyse comparative d'efficacité.")
            else:
                st.warning("Aucune donnée de service disponible pour cette analyse.")
            st.markdown('</div>', unsafe_allow_html=True)
    
        # 4. RÉPARTITION DÉMOGRAPHIQUE
        elif "Répartition Démographique" in viz_service_type:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("👥 Analyse Démographique des Services")
        
            # Vérifier si les colonnes nécessaires existent
            required_cols = ['GenreFr', 'LL_MIL', 'Services', 'Taux_Reussite']
            if all(col in filtered_data.columns for col in required_cols):
                # Calculer le nombre moyen de services par genre
                filtered_data['Nb_Services'] = filtered_data['Services'].apply(len)
            
                col1, col2 = st.columns(2)
            
                with col1:
                    # Services par genre
                    gender_services = filtered_data.groupby('GenreFr')['Nb_Services'].mean().reset_index()
                    gender_services.columns = ['Genre', 'Nombre Moyen de Services']
                
                    fig = px.bar(
                        gender_services,
                        x='Genre',
                        y='Nombre Moyen de Services',
                        color='Genre',
                        color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#6495ED'},
                        text_auto='.2f',
                        title='Nombre Moyen de Services par Genre'
                    )
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    # Services par localisation
                    location_services = filtered_data.groupby('LL_MIL')['Nb_Services'].mean().reset_index()
                    location_services.columns = ['Localisation', 'Nombre Moyen de Services']
                
                    fig = px.bar(
                        location_services,
                        x='Localisation',
                        y='Nombre Moyen de Services',
                        color='Localisation',
                        text_auto='.2f',
                        title='Nombre Moyen de Services par Localisation'
                    )
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                # Distribution des services par démographie
                st.subheader("🗺️ Accès aux Services par Démographie")
            
                # Créer une matrice d'analyse multidimensionnelle
                service_access = filtered_data.pivot_table(
                    index=['GenreFr', 'LL_MIL'],
                    columns='Type',
                    values='Id_TypeService',
                    aggfunc=lambda x: x.notna().sum() / len(x) * 100 if len(x) > 0 else 0
                ).reset_index().fillna(0)
            
                service_access.columns.name = None
                service_access = service_access.melt(
                    id_vars=['GenreFr', 'LL_MIL'],
                    var_name='Type Établissement',
                    value_name='Taux d\'Accès (%)'
                )
            
                # Graphique à barres groupées
                fig = px.bar(
                    service_access,
                    x='GenreFr',
                    y='Taux d\'Accès (%)',
                    color='Type Établissement',
                    barmode='group',
                    facet_col='LL_MIL',
                    title='Taux d\'Accès aux Services par Démographie et Type d\'Établissement',
                    text_auto='.1f',
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            
                # Analyse de l'efficacité des services par démographie
                st.subheader("📊 Efficacité des Services par Groupe Démographique")
            
                all_services = []
                for services in filtered_data['Services'].dropna():
                    all_services.extend(services)
                unique_services = sorted(set(all_services))
            
                # Permettre à l'utilisateur de sélectionner un service spécifique pour l'analyse
                if unique_services:
                    # Créer un dictionnaire pour la sélection
                    service_options = {get_service_name(s): s for s in unique_services}
                
                    selected_service_name = st.selectbox(
                        "Sélectionnez un service pour voir son efficacité par groupe démographique",
                        options=list(service_options.keys()),
                        index=0
                    )
                
                    selected_id = service_options[selected_service_name]
                
                    # Filtrer les données pour ce service
                    with_service = filtered_data[filtered_data['Services'].apply(
                        lambda x: selected_id in x if isinstance(x, list) else False)]
                
                    if not with_service.empty:
                        # Calculer les taux de réussite par groupe démographique
                        demo_efficacy = with_service.pivot_table(
                            index='GenreFr',
                            columns='LL_MIL',
                            values='Taux_Reussite',
                            aggfunc='mean'
                        ).fillna(0)
                    
                        # Afficher sous forme de heatmap
                        fig = px.imshow(
                            demo_efficacy,
                            text_auto='.0%',
                            color_continuous_scale='RdYlGn',
                            title=f'Taux de Réussite pour {selected_service_name} par Groupe Démographique',
                            labels=dict(x="Localisation", y="Genre", color="Taux de Réussite")
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"Pas assez de données pour analyser l'efficacité de {selected_service_name}.")
                else:
                    st.info("Aucun service identifié dans les données filtrées.")
            else:
                st.warning("Données démographiques insuffisantes pour cette analyse.")
            st.markdown('</div>', unsafe_allow_html=True)
    
        # 5. TENDANCES ET CORRÉLATIONS
        elif "Tendances" in viz_service_type:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🔍 Analyse des Tendances")
        
            # Ajouter le nombre de services comme colonne
            filtered_data['Nb_Services'] = filtered_data['Services'].apply(len)
        
            col1, col2 = st.columns(2)
        
            with col1:
                # Distribution des résultats selon le nombre de services
                outcome_by_services = filtered_data.pivot_table(
                    index='resultatFr',
                    columns='Nb_Services',
                    aggfunc='size',
                    fill_value=0
                ).transpose()
            
                # Normaliser pour obtenir des pourcentages
                outcome_normalized = outcome_by_services.div(outcome_by_services.sum(axis=1), axis=0) * 100
            
                # Transformer pour plotly
                outcome_melted = outcome_normalized.reset_index().melt(
                    id_vars=['Nb_Services'],
                    var_name='Résultat',
                    value_name='Pourcentage'
                )
            
                fig = px.area(
                    outcome_melted,
                    x='Nb_Services',
                    y='Pourcentage',
                    color='Résultat',
                    title='Distribution des Résultats par Nombre de Services',
                    labels={'Pourcentage': '% d\'Élèves'},
                    line_shape='spline'
                )
                fig.update_layout(
                    yaxis_tickformat='.0f',
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        
            with col2:
                # Situations des élèves selon les services
                situation_by_services = filtered_data.pivot_table(
                    index='SituationFr',
                    columns='Nb_Services',
                    aggfunc='size',
                    fill_value=0
                ).transpose()
            
                # Normaliser
                if not situation_by_services.empty:
                    situation_normalized = situation_by_services.div(situation_by_services.sum(axis=1), axis=0) * 100
                
                    # Transformer pour plotly
                    situation_melted = situation_normalized.reset_index().melt(
                        id_vars=['Nb_Services'],
                        var_name='Situation',
                        value_name='Pourcentage'
                    )
                
                    fig = px.line(
                        situation_melted,
                        x='Nb_Services',
                        y='Pourcentage',
                        color='Situation',
                        title='Évolution des Situations selon le Nombre de Services',
                        labels={'Pourcentage': '% d\'Élèves'},
                        markers=True,
                        line_shape='spline'
                    )
                    fig.update_layout(
                        yaxis_tickformat='.0f',
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Données insuffisantes pour cette analyse.")
        
            # Analyse de corrélation avancée
            st.subheader("🔗 Analyse de Corrélations")
            
            # Matrice de corrélation entre variables quantitatives
            correlation_cols = ['Nb_Services', 'Taux_Reussite']
            if len(correlation_cols) >= 2:
                corr_data = filtered_data[correlation_cols].corr()
                
                fig = px.imshow(
                    corr_data,
                    text_auto='.3f',
                    color_continuous_scale='RdBu_r',
                    title='Matrice de Corrélation',
                    labels=dict(color="Corrélation")
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
                    
    elif viz_type == "🎓 Analyse des Résultats":
        # Nouvelle section pour l'analyse des taux de réussite
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    
        viz_result_type = st.selectbox(
            "Visualisation sur Taux de Réussite",
            [
                "📈 Taux Global",
                "👥 Comparaison par Genre et établissement",
                "🌍 Répartition Géographique",
                "📊 Analyse Détaillée des Résultats"
            ],
            key="viz_type_results"
        )
    
        # 1. TAUX GLOBAL
        if viz_result_type == "📈 Taux Global":
            st.subheader("📈 Analyse Globale du Taux de Réussite")
        
            col1, col2 = st.columns(2)
        
            with col1:
                # Distribution globale
                fig = px.histogram(
                    filtered_data,
                    x='Taux_Reussite',
                    nbins=20,
                    title='Distribution des Taux de Réussite',
                    labels={'Taux_Reussite': 'Taux de Réussite'},
                    color_discrete_sequence=['#4E79A7']
                )
                fig.update_layout(
                    yaxis_title="Nombre d'élèves",
                    bargap=0.1,
                    xaxis_tickformat='.0%'
                )
                st.plotly_chart(fig, use_container_width=True)
        
            with col2:
                # Boxplot par type d'établissement
                fig = px.box(
                    filtered_data,
                    x='Type',
                    y='Taux_Reussite',
                    color='Type',
                    title='Répartition par Type d\'Établissement',
                    labels={'Taux_Reussite': 'Taux de Réussite'},
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                )
                fig.update_layout(
                    yaxis_tickformat='.0%',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
            # KPI globaux
            st.subheader("📊 Indicateurs Clés")
        
            avg_success = filtered_data['Taux_Reussite'].mean()
            median_success = filtered_data['Taux_Reussite'].median()
            std_success = filtered_data['Taux_Reussite'].std()
        
            kpi1, kpi2, kpi3 = st.columns(3)
        
            with kpi1:
                st.metric(
                    label="Moyenne de Réussite",
                    value=f"{avg_success:.1%}",
                    help="Taux de réussite moyen de tous les élèves"
                )
        
            with kpi2:
                st.metric(
                    label="Médiane de Réussite",
                    value=f"{median_success:.1%}",
                    help="Valeur médiane du taux de réussite"
                )
        
            with kpi3:
                st.metric(
                    label="Écart-Type",
                    value=f"{std_success:.3f}",
                    help="Mesure de dispersion des résultats"
                )
    
    
        # 2. COMPARAISON PAR GENRE
        elif viz_result_type == "👥 Comparaison par Genre et établissement":
            st.subheader("👥 Analyse des Résultats par Genre et établissement")
        
            if 'GenreFr' in filtered_data.columns:
                col1, col2 = st.columns(2)
            
                with col1:
                    # Répartition par genre
                    gender_dist = filtered_data['GenreFr'].value_counts(normalize=True).reset_index()
                    gender_dist.columns = ['Genre', 'Proportion']
                
                    fig = px.pie(
                        gender_dist,
                        names='Genre',
                        values='Proportion',
                        title='Répartition des Élèves par Genre',
                        color='Genre',
                        color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#6495ED'}
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    # Taux de réussite par genre
                    gender_success = filtered_data.groupby('GenreFr')['Taux_Reussite'] \
                        .agg(['mean', 'std', 'count']) \
                        .reset_index()
                    gender_success.columns = ['Genre', 'Moyenne', 'Écart-Type', 'Effectif']
                
                    fig = px.bar(
                        gender_success,
                        x='Genre',
                        y='Moyenne',
                        error_y='Écart-Type',
                        color='Genre',
                        title='Taux de Réussite Moyen par Genre',
                        labels={'Moyenne': 'Taux de Réussite'},
                        color_discrete_map={'Fille': '#FF69B4', 'Garçon': '#6495ED'},
                        text_auto='.1%'
                    )
                    fig.update_layout(
                        yaxis_tickformat='.0%',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                # Analyse combinée genre + type d'établissement
                st.subheader("🏫 Combinaison Genre et Type d'Établissement")
            
                combined_analysis = filtered_data.groupby(['GenreFr', 'Type'])['Taux_Reussite'] \
                    .mean().unstack().reset_index()
            
                fig = px.bar(
                    combined_analysis,
                    x='GenreFr',
                    y=['Public', 'Privé'],
                    barmode='group',
                    title='Taux de Réussite par Genre et Type d\'Établissement',
                    labels={'value': 'Taux de Réussite', 'GenreFr': 'Genre'},
                    color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                )
                fig.update_layout(
                    yaxis_tickformat='.0%',
                    legend_title='Type d\'Établissement'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.warning("Données de genre non disponibles dans le dataset filtré.")
            
        # 3. RÉPARTITION GÉOGRAPHIQUE
        elif viz_result_type == "🌍 Répartition Géographique":
            st.subheader("🌍 Analyse Géographique des Résultats")
        
            if 'LL_MIL' in filtered_data.columns:
                # Taux moyen par localisation
                geo_success = filtered_data.groupby('LL_MIL')['Taux_Reussite'] \
                    .agg(['mean', 'count']) \
                    .reset_index() \
                    .rename(columns={'mean': 'Taux_Reussite', 'count': 'Nombre_Élèves'})
            
                col1, col2 = st.columns(2)
            
                with col1:
                    fig = px.bar(
                        geo_success,
                        x='LL_MIL',
                        y='Taux_Reussite',
                        color='Taux_Reussite',
                        title='Taux de Réussite par Localisation',
                        labels={'Taux_Reussite': 'Taux de Réussite Moyen', 'LL_MIL': 'Localisation'},
                        color_continuous_scale='tealrose',
                        text_auto='.1%'
                    )
                    fig.update_layout(
                        yaxis_tickformat='.0%',
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    fig = px.scatter(
                        geo_success,
                        x='Nombre_Élèves',
                        y='Taux_Reussite',
                        size='Nombre_Élèves',
                        color='LL_MIL',
                        title='Corrélation Taille/Réussite par Localisation',
                        labels={'Taux_Reussite': 'Taux de Réussite Moyen', 'LL_MIL': 'Localisation'},
                        hover_name='LL_MIL'
                    )
                    fig.update_layout(
                        yaxis_tickformat='.0%'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Analyse détaillée par région
                st.subheader("📍 Analyse Détaillée par Région")
                
                # Permettre la sélection d'une région spécifique
                selected_region = st.selectbox(
                    "Sélectionnez une région pour analyse détaillée:",
                    options=['Toutes'] + sorted(filtered_data['LL_MIL'].unique().tolist())
                )
                
                if selected_region != 'Toutes':
                    region_data = filtered_data[filtered_data['LL_MIL'] == selected_region]
                    
                    # Statistiques pour la région sélectionnée
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_region = region_data['Taux_Reussite'].mean()
                        st.metric(
                            label=f"Taux Moyen - {selected_region}",
                            value=f"{avg_region:.1%}"
                        )
                    
                    with col2:
                        count_region = len(region_data)
                        st.metric(
                            label="Nombre d'Élèves",
                            value=f"{count_region:,}"
                        )
                    
                    with col3:
                        std_region = region_data['Taux_Reussite'].std()
                        st.metric(
                            label="Écart-Type",
                            value=f"{std_region:.3f}"
                        )
                    
                    # Distribution dans la région sélectionnée
                    fig = px.histogram(
                        region_data,
                        x='Taux_Reussite',
                        color='Type',
                        title=f'Distribution des Taux de Réussite - {selected_region}',
                        labels={'Taux_Reussite': 'Taux de Réussite'},
                        nbins=15,
                        barmode='overlay',
                        opacity=0.7,
                        color_discrete_map={'Public': '#1e88e5', 'Privé': '#ff5252'}
                    )
                    fig.update_layout(
                        xaxis_tickformat='.0%',
                        bargap=0.1
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
            else:
                st.warning("Données de localisation non disponibles dans le dataset filtré.")
        
        # 4. ANALYSE DÉTAILLÉE DES RÉSULTATS
        elif viz_result_type == "📊 Analyse Détaillée des Résultats":
            st.subheader("📊 Analyse Détaillée des Résultats Scolaires")
            
            # Vérifier la présence des colonnes nécessaires
            if 'resultatFr' in filtered_data.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Distribution des résultats
                    result_dist = filtered_data['resultatFr'].value_counts().reset_index()
                    result_dist.columns = ['Résultat', 'Nombre']
                    
                    fig = px.pie(
                        result_dist,
                        names='Résultat',
                        values='Nombre',
                        title='Distribution des Résultats Scolaires',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Résultats par type d'établissement
                    result_by_type = filtered_data.groupby(['Type', 'resultatFr']).size().unstack(fill_value=0)
                    result_by_type_pct = result_by_type.div(result_by_type.sum(axis=1), axis=0) * 100
                    
                    fig = px.bar(
                        result_by_type_pct.reset_index(),
                        x='Type',
                        y=result_by_type_pct.columns.tolist(),
                        title='Répartition des Résultats par Type d\'Établissement (%)',
                        labels={'value': 'Pourcentage', 'variable': 'Résultat'},
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig.update_layout(
                        yaxis_tickformat='.0f',
                        legend_title='Résultat'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Analyse des situations d'élèves
                if 'SituationFr' in filtered_data.columns:
                    st.subheader("👨‍🎓 Analyse des Situations d'Élèves")
                    
                    # Situation par résultat
                    situation_result = pd.crosstab(
                        filtered_data['SituationFr'], 
                        filtered_data['resultatFr'], 
                        normalize='columns'
                    ) * 100
                    
                    fig = px.imshow(
                        situation_result,
                        text_auto='.1f',
                        color_continuous_scale='Blues',
                        title='Relation entre Situation et Résultat (%)',
                        labels=dict(x="Résultat", y="Situation", color="Pourcentage")
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                # Tableau de synthèse
                st.subheader("📋 Tableau de Synthèse")
                
                # Créer un tableau de synthèse
                synthesis_data = []
                for result in filtered_data['resultatFr'].unique():
                    result_data = filtered_data[filtered_data['resultatFr'] == result]
                    synthesis_data.append({
                        'Résultat': result,
                        'Nombre d\'Élèves': len(result_data),
                        'Taux de Réussite Moyen': f"{result_data['Taux_Reussite'].mean():.1%}",
                        'Écart-Type': f"{result_data['Taux_Reussite'].std():.3f}",
                        '% du Total': f"{len(result_data)/len(filtered_data)*100:.1f}%"
                    })
                
                synthesis_df = pd.DataFrame(synthesis_data)
                synthesis_df = synthesis_df.sort_values('Nombre d\'Élèves', ascending=False)
                
                st.dataframe(synthesis_df, use_container_width=True)
                
            else:
                st.warning("Données de résultats détaillées non disponibles dans le dataset filtré.")
                    
        st.markdown('</div>', unsafe_allow_html=True)
    
    # FOOTER
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p><strong>Système d'Analyse Intelligente des Données Scolaires</strong></p>
        <p><small>Tableau de bord interactif pour l'analyse des performances et services éducatifs</small></p>
    </div>
    """, unsafe_allow_html=True)
                        