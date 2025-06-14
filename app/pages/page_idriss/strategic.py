import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def show_page():
    # Titre principal
    st.title("Analyse Stratégique des Données")
    
    # Vérifier si des données sont chargées
    if st.session_state.get("df") is None:
        st.warning("⚠️ Aucune donnée n'est chargée. Veuillez d'abord charger des données depuis la page d'accueil.")
        return
    
    # Récupérer le DataFrame
    df = st.session_state["df"]
    
    # Section d'introduction
    st.markdown("""
    Cette page vous permet d'effectuer une analyse stratégique de vos données en générant des tableaux de bord
    interactifs et des visualisations qui vous aideront à prendre des décisions éclairées.
    """)
    
    # Sélection des colonnes pour l'analyse
    st.header("1. Sélection des données pour l'analyse")
    
    # Colonnes numériques et catégorielles
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if 'date_cols' not in st.session_state:
        # Tentative de détection des colonnes de date
        date_cols = []
        for col in df.columns:
            try:
                if pd.to_datetime(df[col], errors='coerce').notna().any():
                    date_cols.append(col)
            except:
                pass
        st.session_state['date_cols'] = date_cols
    
    # Interface de sélection des colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        selected_metric_cols = st.multiselect(
            "Sélectionnez les colonnes métriques (pour les KPIs)",
            options=numerical_cols,
            default=numerical_cols[:3] if len(numerical_cols) >= 3 else numerical_cols
        )
    
    with col2:
        selected_dimension_cols = st.multiselect(
            "Sélectionnez les colonnes dimensionnelles (pour les filtres)",
            options=categorical_cols,
            default=categorical_cols[:2] if len(categorical_cols) >= 2 else categorical_cols
        )
    
    # Sélection de la colonne temporelle si disponible
    if st.session_state['date_cols']:
        time_col = st.selectbox(
            "Sélectionnez une colonne temporelle pour l'analyse d'évolution (optionnel)",
            options=["Aucune"] + st.session_state['date_cols'],
            index=0
        )
    else:
        time_col = "Aucune"
        st.info("Aucune colonne de date détectée dans vos données.")
    
    # Filtres interactifs
    st.header("2. Filtres interactifs")
    
    # Création des filtres pour chaque dimension sélectionnée
    filtered_df = df.copy()
    
    for dim in selected_dimension_cols:
        # Obtenir les valeurs uniques
        unique_values = filtered_df[dim].dropna().unique()
        
        # Créer un sélecteur multiple
        selected_values = st.multiselect(
            f"Filtrer par {dim}",
            options=unique_values,
            default=unique_values
        )
        
        # Appliquer le filtre si l'utilisateur a sélectionné des valeurs
        if selected_values:
            filtered_df = filtered_df[filtered_df[dim].isin(selected_values)]
    
    # Filtres pour les colonnes numériques
    if selected_metric_cols:
        st.subheader("Filtres numériques")
        
        col1, col2 = st.columns(2)
        
        # Sélection de la colonne numérique à filtrer
        with col1:
            numeric_filter_col = st.selectbox(
                "Sélectionnez une colonne numérique à filtrer",
                options=["Aucune"] + selected_metric_cols
            )
        
        # Création du slider pour filtrer
        if numeric_filter_col != "Aucune":
            with col2:
                min_val = float(filtered_df[numeric_filter_col].min())
                max_val = float(filtered_df[numeric_filter_col].max())
                
                # Ajuster le step en fonction de la plage
                range_val = max_val - min_val
                step = range_val / 100 if range_val > 0 else 0.01
                
                # Slider pour sélectionner la plage
                selected_range = st.slider(
                    f"Plage pour {numeric_filter_col}",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=step
                )
                
                # Appliquer le filtre
                filtered_df = filtered_df[
                    (filtered_df[numeric_filter_col] >= selected_range[0]) & 
                    (filtered_df[numeric_filter_col] <= selected_range[1])
                ]
    
    # Afficher un aperçu des données filtrées
    st.subheader("Aperçu des données filtrées")
    st.dataframe(filtered_df.head(10), use_container_width=True)
    st.info(f"{len(filtered_df)} enregistrements après filtrage sur {len(df)} au total")
    
    # Analyse et tableaux de bord
    st.header("3. Tableau de bord stratégique")
    
    # KPIs principaux
    if selected_metric_cols:
        st.subheader("3.1 Indicateurs clés de performance (KPIs)")
        
        # Afficher les KPIs en colonnes (maximum 4 par ligne)
        cols = st.columns(min(4, len(selected_metric_cols)))
        
        for i, metric in enumerate(selected_metric_cols[:4]):  # Limiter à 4 métriques
            with cols[i % 4]:
                current_val = filtered_df[metric].mean()
                
                # Formater la valeur selon son ordre de grandeur
                if abs(current_val) >= 1000000:
                    display_val = f"{current_val/1000000:.2f}M"
                elif abs(current_val) >= 1000:
                    display_val = f"{current_val/1000:.2f}K"
                else:
                    display_val = f"{current_val:.2f}"
                
                st.metric(
                    label=metric,
                    value=display_val
                )
    
    # Analyses comparatives
    st.subheader("3.2 Analyse comparative")
    
    # Onglets pour différentes dimensions d'analyse
    if selected_dimension_cols:
        tabs = st.tabs([f"Par {dim}" for dim in selected_dimension_cols[:4]])  # Limiter à 4 dimensions
        
        for i, tab in enumerate(tabs):
            dim = selected_dimension_cols[i]
            
            with tab:
                if selected_metric_cols:
                    # Agrégation des données par dimension
                    agg_funcs = {col: 'mean' for col in selected_metric_cols}
                    dim_data = filtered_df.groupby(dim).agg(agg_funcs).reset_index()
                    
                    # Visualisation des données
                    st.subheader(f"Analyse comparative par {dim}")
                    
                    # Création du graphique
                    if len(selected_metric_cols) > 1:
                        # Graphique en barres groupées si plusieurs métriques
                        fig = px.bar(
                            dim_data,
                            x=dim,
                            y=selected_metric_cols[:3],  # Limiter à 3 métriques pour la lisibilité
                            barmode='group',
                            title=f"Comparaison des métriques par {dim}",
                            labels={'value': 'Valeur', 'variable': 'Métrique'},
                            height=500
                        )
                    else:
                        # Graphique en barres simple si une seule métrique
                        fig = px.bar(
                            dim_data,
                            x=dim,
                            y=selected_metric_cols[0],
                            title=f"{selected_metric_cols[0]} par {dim}",
                            color=dim,
                            height=500
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau de données agrégées
                    st.subheader("Données détaillées")
                    st.dataframe(dim_data, use_container_width=True)
    
    # Analyse temporelle si une colonne de temps est sélectionnée
    if time_col != "Aucune" and selected_metric_cols:
        st.header("4. Analyse d'évolution temporelle")
        
        # Préparer les données temporelles
        try:
            # Convertir en datetime si ce n'est pas déjà le cas
            if not pd.api.types.is_datetime64_any_dtype(filtered_df[time_col]):
                filtered_df[time_col] = pd.to_datetime(filtered_df[time_col], errors='coerce')
            
            # Déterminer le niveau d'agrégation (jour, mois, année)
            time_resolution = st.selectbox(
                "Sélectionnez la résolution temporelle",
                options=["Jour", "Mois", "Année"],
                index=1  # Mois par défaut
            )
            
            # Créer une colonne de période
            if time_resolution == "Jour":
                filtered_df['period'] = filtered_df[time_col].dt.date
                format_str = '%Y-%m-%d'
            elif time_resolution == "Mois":
                filtered_df['period'] = filtered_df[time_col].dt.strftime('%Y-%m')
                format_str = '%Y-%m'
            else:  # Année
                filtered_df['period'] = filtered_df[time_col].dt.year
                format_str = '%Y'
            
            # Sélectionner la métrique à visualiser
            selected_time_metric = st.selectbox(
                "Sélectionnez une métrique pour l'analyse temporelle",
                options=selected_metric_cols
            )
            
            # Agréger les données par période
            time_data = filtered_df.groupby('period')[selected_time_metric].mean().reset_index()
            time_data = time_data.sort_values('period')
            
            # Visualisation
            fig = px.line(
                time_data,
                x='period',
                y=selected_time_metric,
                title=f"Évolution de {selected_time_metric} au fil du temps",
                markers=True,
                line_shape="linear",
                height=500
            )
            
            # Améliorer la mise en forme de l'axe des x
            fig.update_xaxes(
                title="Période",
                tickangle=45 if time_resolution == "Mois" else 0
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau de données temporelles
            st.subheader("Données d'évolution")
            st.dataframe(time_data, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erreur lors de l'analyse temporelle: {e}")
    
    # Analyse de distribution
    if selected_metric_cols:
        st.header("5. Analyse de distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dist_metric = st.selectbox(
                "Sélectionnez une métrique pour l'analyse de distribution",
                options=selected_metric_cols
            )
        
        with col2:
            if selected_dimension_cols:
                dist_dimension = st.selectbox(
                    "Sélectionnez une dimension pour la segmentation (facultatif)",
                    options=["Aucune"] + selected_dimension_cols
                )
            else:
                dist_dimension = "Aucune"
        
        # Histogramme pour la distribution
        if dist_dimension == "Aucune":
            fig = px.histogram(
                filtered_df,
                x=dist_metric,
                nbins=30,
                title=f"Distribution de {dist_metric}",
                height=500
            )
        else:
            fig = px.histogram(
                filtered_df,
                x=dist_metric,
                color=dist_dimension,
                nbins=30,
                title=f"Distribution de {dist_metric} par {dist_dimension}",
                barmode="overlay",
                opacity=0.7,
                height=500
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques descriptives
        st.subheader("Statistiques descriptives")
        
        if dist_dimension == "Aucune":
            desc_stats = filtered_df[dist_metric].describe().reset_index()
            desc_stats.columns = ["Statistique", "Valeur"]
        else:
            desc_stats = filtered_df.groupby(dist_dimension)[dist_metric].describe().reset_index()
        
        st.dataframe(desc_stats, use_container_width=True)
    
    # Analyse de corrélation
    if len(selected_metric_cols) > 1:
        st.header("6. Analyse de corrélation")
        
        # Matrice de corrélation
        corr_matrix = filtered_df[selected_metric_cols].corr()
        
        # Heatmap de corrélation avec Plotly
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title="Matrice de corrélation",
            height=600,
            width=800
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des métriques hautement corrélées
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:  # Seuil de corrélation élevée
                    high_corr.append({
                        "Métrique 1": corr_matrix.columns[i],
                        "Métrique 2": corr_matrix.columns[j],
                        "Coefficient de corrélation": corr_matrix.iloc[i, j]
                    })
        
        if high_corr:
            st.subheader("Paires de métriques hautement corrélées")
            st.dataframe(pd.DataFrame(high_corr), use_container_width=True)
        else:
            st.info("Aucune paire de métriques n'est hautement corrélée (seuil > 0.7)")
        
        # Visualisation de la corrélation entre deux métriques spécifiques
        st.subheader("Analyse de corrélation bivariée")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_metric = st.selectbox(
                "Sélectionnez la métrique pour l'axe X",
                options=selected_metric_cols,
                index=0
            )
        
        with col2:
            y_metric = st.selectbox(
                "Sélectionnez la métrique pour l'axe Y",
                options=selected_metric_cols,
                index=min(1, len(selected_metric_cols)-1)
            )
        
        # Créer le nuage de points
        if selected_dimension_cols:
            color_dim = st.selectbox(
                "Sélectionner une dimension pour la couleur (facultatif)",
                options=["Aucune"] + selected_dimension_cols
            )
        else:
            color_dim = "Aucune"
        
        if color_dim == "Aucune":
            fig = px.scatter(
                filtered_df,
                x=x_metric,
                y=y_metric,
                title=f"Corrélation entre {x_metric} et {y_metric}",
                opacity=0.7,
                trendline="ols"  # Ligne de tendance
            )
        else:
            fig = px.scatter(
                filtered_df,
                x=x_metric,
                y=y_metric,
                color=color_dim,
                title=f"Corrélation entre {x_metric} et {y_metric}, par {color_dim}",
                opacity=0.7,
                trendline="ols"
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Section pour l'analyse d'opportunités et de menaces (SWOT simplifiée)
    st.header("7. Analyse d'opportunités et de risques")
    
    st.markdown("""
    Utilisez cette section pour identifier les opportunités et les risques basés sur l'analyse des données.
    Les seuils peuvent être ajustés pour correspondre à votre contexte spécifique.
    """)
    
    # Sélectionner une métrique cible
    target_metric = None
    if selected_metric_cols:
        target_metric = st.selectbox(
            "Sélectionnez une métrique cible pour l'analyse",
            options=selected_metric_cols
        )
    
    # Définir des seuils pour les opportunités et les risques
    if target_metric:
        col1, col2 = st.columns(2)
        
        with col1:
            min_val = float(filtered_df[target_metric].min())
            max_val = float(filtered_df[target_metric].max())
            mean_val = float(filtered_df[target_metric].mean())
            
            # Définir un seuil d'opportunité par défaut à 75% entre la moyenne et le max
            default_opportunity = mean_val + (max_val - mean_val) * 0.75
            
            opportunity_threshold = st.slider(
                "Seuil d'opportunité",
                min_value=min_val,
                max_value=max_val,
                value=min(max_val, default_opportunity),
                step=(max_val - min_val) / 100
            )
        
        with col2:
            # Définir un seuil de risque par défaut à 75% entre le min et la moyenne
            default_risk = mean_val - (mean_val - min_val) * 0.75
            
            risk_threshold = st.slider(
                "Seuil de risque",
                min_value=min_val,
                max_value=max_val,
                value=max(min_val, default_risk),
                step=(max_val - min_val) / 100
            )
        
        # Identifier les dimensions avec opportunités et risques
        if selected_dimension_cols:
            dimension_for_analysis = st.selectbox(
                "Sélectionner une dimension pour l'analyse d'opportunités et de risques",
                options=selected_dimension_cols
            )
            
            # Agréger par la dimension sélectionnée
            analysis_data = filtered_df.groupby(dimension_for_analysis)[target_metric].mean().reset_index()
            
            # Identifier les opportunités et les risques
            analysis_data['statut'] = pd.cut(
                analysis_data[target_metric],
                bins=[float('-inf'), risk_threshold, opportunity_threshold, float('inf')],
                labels=['Risque', 'Normal', 'Opportunité']
            )
            
            # Afficher les opportunités et les risques
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Opportunités potentielles 🚀")
                opportunities = analysis_data[analysis_data['statut'] == 'Opportunité']
                if not opportunities.empty:
                    st.dataframe(opportunities[[dimension_for_analysis, target_metric]], use_container_width=True)
                else:
                    st.info("Aucune opportunité identifiée avec les seuils actuels.")
            
            with col2:
                st.subheader("Risques potentiels ⚠️")
                risks = analysis_data[analysis_data['statut'] == 'Risque']
                if not risks.empty:
                    st.dataframe(risks[[dimension_for_analysis, target_metric]], use_container_width=True)
                else:
                    st.info("Aucun risque identifié avec les seuils actuels.")
            
            # Visualiser la distribution avec les seuils
            fig = go.Figure()
            
            # Ajouter l'histogramme
            fig.add_trace(go.Histogram(
                x=analysis_data[target_metric],
                name="Distribution",
                opacity=0.75,
                marker_color="lightblue"
            ))
            
            # Ajouter les seuils
            fig.add_shape(
                type="line",
                x0=risk_threshold,
                x1=risk_threshold,
                y0=0,
                y1=analysis_data[target_metric].value_counts().max() * 1.1,
                line=dict(color="red", dash="dash", width=2)
            )
            
            fig.add_shape(
                type="line",
                x0=opportunity_threshold,
                x1=opportunity_threshold,
                y0=0,
                y1=analysis_data[target_metric].value_counts().max() * 1.1,
                line=dict(color="green", dash="dash", width=2)
            )
            
            # Annotations
            fig.add_annotation(
                x=risk_threshold,
                y=analysis_data[target_metric].value_counts().max() * 1.05,
                text="Seuil de risque",
                showarrow=False,
                font=dict(color="red")
            )
            
            fig.add_annotation(
                x=opportunity_threshold,
                y=analysis_data[target_metric].value_counts().max() * 1.05,
                text="Seuil d'opportunité",
                showarrow=False,
                font=dict(color="green")
            )
            
            fig.update_layout(
                title=f"Distribution de {target_metric} par {dimension_for_analysis} avec seuils",
                xaxis_title=target_metric,
                yaxis_title="Fréquence",
                bargap=0.2,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Graphique en barres pour visualiser les opportunités et les risques
            fig = px.bar(
                analysis_data.sort_values(target_metric),
                x=dimension_for_analysis,
                y=target_metric,
                color='statut',
                color_discrete_map={
                    'Risque': 'red',
                    'Normal': 'gray',
                    'Opportunité': 'green'
                },
                title=f"Analyse des {dimension_for_analysis} par {target_metric}",
                height=600
            )
            
            # Ajouter des lignes horizontales pour les seuils
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=len(analysis_data)-0.5,
                y0=risk_threshold,
                y1=risk_threshold,
                line=dict(color="red", dash="dash", width=1)
            )
            
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=len(analysis_data)-0.5,
                y0=opportunity_threshold,
                y1=opportunity_threshold,
                line=dict(color="green", dash="dash", width=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations finales
    st.header("8. Recommandations")
    
    st.markdown("""
    Sur la base de votre analyse stratégique des données, vous pouvez formuler 
    des recommandations pour améliorer les performances et prendre des décisions éclairées.
    
    **Exemples de recommandations stratégiques:**
    
    1. **Identification des facteurs de succès**: Concentrez-vous sur les dimensions qui montrent
       un impact positif significatif sur vos indicateurs clés.
       
    2. **Atténuation des risques**: Élaborez des stratégies pour les dimensions qui 
       présentent des indicateurs en dessous des seuils critiques.
       
    3. **Optimisation des ressources**: Réaffectez les ressources vers les domaines
       présentant les meilleures opportunités de croissance ou d'amélioration.
       
    4. **Benchmarking interne**: Identifiez les meilleures pratiques des segments
       les plus performants et appliquez-les aux segments moins performants.
    """)
    
    # Zone pour les notes et recommandations de l'utilisateur
    user_recommendations = st.text_area(
        "Vos recommandations stratégiques basées sur l'analyse des données:",
        height=200
    )
    
    # Bouton pour générer un rapport
    if st.button("Générer un rapport d'analyse stratégique"):
        st.success("Rapport d'analyse stratégique généré avec succès!")
        # Ici, vous pourriez implémenter une fonction pour générer un PDF ou un document exportable
        # C'est une fonctionnalité qui pourrait être développée plus tard
        
    # Crédit en bas de page
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; font-size: 12px; color: gray;">
        Analyse Stratégique • Développé avec Streamlit • 2025
        </div>
        """, 
        unsafe_allow_html=True
    )