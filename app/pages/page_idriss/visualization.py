import io
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
import numpy as np
from datetime import datetime

def show_page():
    st.title("📊 Tableau de Bord Analytique")
    
    if st.session_state["df"] is not None or st.session_state.get("df_merged") is not None or st.session_state.get("db_path"):
        # On vérifie d'abord le type de fichier chargé en session
        file_type = None
        df = None
        
        if "db_path" in st.session_state and st.session_state["db_path"]:
            file_type = "access"
        elif "df" in st.session_state and st.session_state["df"] is not None:
            file_type = "excel_csv"
            df = st.session_state["df"].copy()
        elif "df_merged" in st.session_state and st.session_state["df_merged"] is not None:
            file_type = "merged"
            df = st.session_state["df_merged"].copy()
            st.info("Visualisation basée sur les données fusionnées. Utilisez l'onglet 'Fusion' pour modifier les sources.")
        
        # Si fichier Access
        if file_type == "access":
            selected_table = st.sidebar.selectbox("Sélectionnez une table", st.session_state["tables"])
            
            if selected_table:
                try:
                    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={st.session_state['db_path']}"
                    conn = pyodbc.connect(conn_str)
                    df = pd.read_sql(f"SELECT * FROM [{selected_table}]", conn)
                    conn.close()
                except Exception as e:
                    st.error(f"Erreur lors de la connexion à la base de données: {e}")
                    return
        
        # Si fichier Excel ou CSV et pas encore de df
        elif file_type == "excel_csv" and df is None:
            df = st.session_state["df"].copy()
            st.sidebar.info("Données chargées à partir d'un fichier Excel ou CSV")
        
        if df is not None and not df.empty:
            # Préparation des données pour s'adapter à tous types de données
            # Conversion automatique des colonnes qui peuvent être converties en nombres
            for col in df.columns:
                try:
                    # Essayer de convertir en numérique, ignorer si échec
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            
            # Liste des colonnes disponibles pour les graphiques
            all_columns = df.columns.tolist()
            
            # Identifier les colonnes numériques et catégorielles
            num_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            cat_columns = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            
            # Si pas de colonnes numériques, créer des colonnes calculées
            if not num_columns:
                st.info("Aucune colonne numérique détectée. Des métriques basiques seront créées pour l'analyse.")
                
                # Créer une colonne de comptage pour permettre au moins les graphiques de base
                df['_count'] = 1
                num_columns = ['_count']
                
                # Si des colonnes catégorielles existent, créer une colonne de fréquence
                if cat_columns:
                    for cat_col in cat_columns[:1]:  # Limiter à la première colonne catégorielle
                        # Créer une colonne avec la fréquence de chaque valeur
                        value_counts = df[cat_col].value_counts()
                        df['_freq'] = df[cat_col].map(value_counts)
                        num_columns.append('_freq')
                
                # Ajouter un index numérique si besoin
                df['_index'] = range(len(df))
                num_columns.append('_index')
            
            # Si pas de colonnes catégorielles, utiliser l'index comme catégorie
            if not cat_columns:
                st.info("Aucune colonne catégorielle détectée. L'index sera utilisé comme catégorie.")
                df['_category'] = [f"Item {i+1}" for i in range(len(df))]
                cat_columns = ['_category']
            
            # Initialiser les variables avec des valeurs par défaut
            color_primary = "#1E3A8A"
            color_secondary = "#2CFF1C"
            
            # Variables pour les graphiques avec des valeurs par défaut
            bar_x = cat_columns[0] if len(cat_columns) > 0 else "_category"
            bar_y = num_columns[0] if len(num_columns) > 0 else "_count"
            bar_type = "bar"
            show_second_year = True
            second_y = num_columns[1] if len(num_columns) > 1 else None
            
            pie_col = cat_columns[0] if len(cat_columns) > 0 else "_category"
            pie_type = "pie"
            center_value = 45
            
            line_x = cat_columns[0] if len(cat_columns) > 0 else "_category"
            line_y = num_columns[:1] if len(num_columns) > 0 else ["_count"]
            line_type = "line"
            
            bubble_x = num_columns[0] if len(num_columns) > 0 else "_count"
            bubble_y = num_columns[1] if len(num_columns) > 1 else "_index"
            bubble_size = num_columns[0] if len(num_columns) > 0 else "_count"
            bubble_color = cat_columns[0] if len(cat_columns) > 0 else "_category"
            bubble_type = "scatter"
            
            boxplot_col = num_columns[0] if len(num_columns) > 0 else "_count"
            group_by = "Aucun"
            box_type = "box"
            
            # Initialiser la liste des tableaux sauvegardés si elle n'existe pas
            if "saved_dashboards" not in st.session_state:
                st.session_state["saved_dashboards"] = []
            
            # ----- SECTION SAUVEGARDE DU TABLEAU DE BORD -----
            st.sidebar.markdown("## 💾 Tableaux sauvegardés")
            
            # Style CSS personnalisé pour améliorer l'apparence des tableaux sauvegardés
            st.sidebar.markdown("""
            <style>
                .dashboard-item {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: all 0.3s ease;
                }
                .dashboard-item:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                    transform: translateY(-2px);
                }
                .dashboard-name {
                    font-weight: bold;
                    font-size: 1.1em;
                    margin-bottom: 5px;
                }
                .dashboard-date {
                    font-size: 0.85em;
                    color: rgba(255, 255, 255, 0.7);
                    margin-bottom: 10px;
                }
                .dashboard-actions {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 8px;
                }
                .action-button {
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-size: 0.9em;
                    cursor: pointer;
                    text-align: center;
                }
                .load-button {
                    background-color: #1E3A8A;
                    color: white;
                    flex: 2;
                    margin-right: 5px;
                }
                .delete-button {
                    background-color: rgba(220, 53, 69, 0.7);
                    color: white;
                    flex: 1;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Nom du tableau de bord
            dashboard_name = st.sidebar.text_input("Nom du tableau de bord", "Mon Tableau de Bord")
            
            # Afficher les tableaux de bord sauvegardés
            if st.session_state["saved_dashboards"]:
                for i, dashboard in enumerate(st.session_state["saved_dashboards"]):
                    # Utiliser un conteneur HTML personnalisé pour chaque élément
                    dashboard_html = f"""
                    <div class="dashboard-item" id="dashboard-{i}">
                        <div class="dashboard-name">{dashboard['name']}</div>
                        <div class="dashboard-date">{dashboard['timestamp']}</div>
                        <div class="dashboard-actions">
                    """
                    st.sidebar.markdown(dashboard_html, unsafe_allow_html=True)
                    
                    # Créer des boutons "invisibles" qui détectent les clics sur les éléments HTML
                    col1, col2 = st.sidebar.columns([2, 1])
                    with col1:
                        if st.button("Charger", key=f"load_{i}", help="Charger ce tableau de bord"):
                            # Mettre en place les flags dans session_state
                            st.session_state["dashboard_to_load"] = True
                            
                            # Stocker les paramètres des graphiques
                            st.session_state["selected_bar_x"] = dashboard["charts"]["bar"]["x"]
                            st.session_state["selected_bar_y"] = dashboard["charts"]["bar"]["y"]
                            st.session_state["selected_bar_type"] = dashboard["charts"]["bar"]["type"]
                            st.session_state["selected_show_second"] = dashboard["charts"]["bar"]["show_second"]
                            st.session_state["selected_second_y"] = dashboard["charts"]["bar"]["second_y"]
                            
                            st.session_state["selected_pie_col"] = dashboard["charts"]["pie"]["col"]
                            st.session_state["selected_pie_type"] = dashboard["charts"]["pie"]["type"]
                            st.session_state["selected_center_value"] = dashboard["charts"]["pie"]["center_value"]
                            
                            st.session_state["selected_line_x"] = dashboard["charts"]["line"]["x"]
                            st.session_state["selected_line_y"] = dashboard["charts"]["line"]["y"]
                            st.session_state["selected_line_type"] = dashboard["charts"]["line"]["type"]
                            
                            st.session_state["selected_bubble_x"] = dashboard["charts"]["bubble"]["x"]
                            st.session_state["selected_bubble_y"] = dashboard["charts"]["bubble"]["y"]
                            st.session_state["selected_bubble_size"] = dashboard["charts"]["bubble"]["size"]
                            st.session_state["selected_bubble_color"] = dashboard["charts"]["bubble"]["color"]
                            st.session_state["selected_bubble_type"] = dashboard["charts"]["bubble"]["type"]
                            
                            st.session_state["selected_boxplot_col"] = dashboard["charts"]["box"]["col"]
                            st.session_state["selected_group_by"] = dashboard["charts"]["box"]["group_by"]
                            st.session_state["selected_box_type"] = dashboard["charts"]["box"]["type"]
                            
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_{i}", help="Supprimer ce tableau de bord"):
                            # Supprimer le tableau de bord
                            del st.session_state["saved_dashboards"][i]
                            st.rerun()

            
            # Récupérer les valeurs des tableaux chargés si disponibles
            if "dashboard_to_load" in st.session_state and st.session_state["dashboard_to_load"]:
                # Récupérer les valeurs stockées
                bar_x = st.session_state["selected_bar_x"]
                bar_y = st.session_state["selected_bar_y"]
                bar_type = st.session_state["selected_bar_type"]
                show_second_year = st.session_state["selected_show_second"]
                second_y = st.session_state["selected_second_y"]
                
                pie_col = st.session_state["selected_pie_col"]
                pie_type = st.session_state["selected_pie_type"]
                center_value = st.session_state["selected_center_value"]
                
                line_x = st.session_state["selected_line_x"]
                line_y = st.session_state["selected_line_y"]
                line_type = st.session_state["selected_line_type"]
                
                bubble_x = st.session_state["selected_bubble_x"]
                bubble_y = st.session_state["selected_bubble_y"]
                bubble_size = st.session_state["selected_bubble_size"]
                bubble_color = st.session_state["selected_bubble_color"]
                bubble_type = st.session_state["selected_bubble_type"]
                
                boxplot_col = st.session_state["selected_boxplot_col"]
                group_by = st.session_state["selected_group_by"]
                box_type = st.session_state["selected_box_type"]
                
                # Réinitialiser le flag après utilisation
                st.session_state["dashboard_to_load"] = False
            
            # ----- SECTION PARAMÈTRES DES GRAPHIQUES -----
            st.sidebar.markdown("## 📈 Paramètres des graphiques")
            
            # Ajout d'un expander pour chaque graphique
            with st.sidebar.expander("⚙️ Configuration du graphique 1 (Tendances)"):
                graph_types_1 = ["bar", "line", "area", "scatter"]
                bar_type = st.selectbox("Type de graphique", graph_types_1, 
                                        index=graph_types_1.index(bar_type) if bar_type in graph_types_1 else 0, 
                                        key="bar_type")
                
                # Sélecteurs d'axes l'un sous l'autre
                bar_x = st.selectbox("Axe X", all_columns, 
                                    index=all_columns.index(bar_x) if bar_x in all_columns else 0, 
                                    key="bar_x")
                bar_y = st.selectbox("Axe Y", num_columns, 
                                    index=num_columns.index(bar_y) if bar_y in num_columns else 0, 
                                    key="bar_y")
            
            with st.sidebar.expander("⚙️ Configuration du graphique 2 (Répartition)"):
                graph_types_2 = ["pie", "bar", "funnel", "treemap"]
                pie_type = st.selectbox("Type de graphique", graph_types_2, 
                                       index=graph_types_2.index(pie_type) if pie_type in graph_types_2 else 0, 
                                       key="pie_type")
                
                pie_col = st.selectbox("Colonne de catégories", cat_columns, 
                                      index=cat_columns.index(pie_col) if pie_col in cat_columns else 0, 
                                      key="pie_col")
                center_value = st.slider("Valeur centrale (%)", 0, 100, center_value, key="center_value")
            
            with st.sidebar.expander("⚙️ Configuration du graphique 3 (Évolution)"):
                graph_types_3 = ["line", "bar", "area", "scatter"]
                line_type = st.selectbox("Type de graphique", graph_types_3, 
                                        index=graph_types_3.index(line_type) if line_type in graph_types_3 else 0, 
                                        key="line_type")
                
                # Sélecteurs d'axes l'un sous l'autre
                line_x = st.selectbox("Axe X", all_columns, 
                                     index=all_columns.index(line_x) if line_x in all_columns else 0, 
                                     key="line_x")
                line_y = st.multiselect("Métriques", num_columns, 
                                       default=line_y if isinstance(line_y, list) and all(y in num_columns for y in line_y) else [num_columns[0]], 
                                       key="line_y")
            
            with st.sidebar.expander("⚙️ Configuration du graphique 4 (Comparaison)"):
                graph_types_4 = ["scatter", "line", "bar", "area"]
                bubble_type = st.selectbox("Type de graphique", graph_types_4, 
                                          index=graph_types_4.index(bubble_type) if bubble_type in graph_types_4 else 0, 
                                          key="bubble_type")
                
                # Sélecteurs d'axes l'un sous l'autre
                bubble_x = st.selectbox("Axe X", num_columns, 
                                       index=num_columns.index(bubble_x) if bubble_x in num_columns else 0, 
                                       key="bubble_x")
                bubble_y = st.selectbox("Axe Y", num_columns, 
                                       index=num_columns.index(bubble_y) if bubble_y in num_columns else (1 if len(num_columns) > 1 else 0), 
                                       key="bubble_y")
                
                if bubble_type == "scatter":
                    # Sélecteurs de taille et couleur l'un sous l'autre
                    bubble_size = st.selectbox("Taille", num_columns, 
                                              index=num_columns.index(bubble_size) if bubble_size in num_columns else 0, 
                                              key="bubble_size")
                    bubble_color = st.selectbox("Couleur", cat_columns, 
                                               index=cat_columns.index(bubble_color) if bubble_color in cat_columns else 0, 
                                               key="bubble_color")
            
            with st.sidebar.expander("⚙️ Configuration du graphique 5 (Distribution)"):
                graph_types_5 = ["box", "violin", "histogram", "bar"]
                box_type = st.selectbox("Type de graphique", graph_types_5, 
                                       index=graph_types_5.index(box_type) if box_type in graph_types_5 else 0, 
                                       key="box_type")
                
                boxplot_col = st.selectbox("Axe X", num_columns, 
                                          index=num_columns.index(boxplot_col) if boxplot_col in num_columns else 0, 
                                          key="boxplot_col")
                
                group_options = ["Aucun"] + cat_columns
                group_by = st.selectbox("Axe Y", group_options, 
                                      index=group_options.index(group_by) if group_by in group_options else 0, 
                                      key="group_by")
            
            # Bouton pour sauvegarder le tableau de bord actuel
            if st.sidebar.button("💾 Sauvegarder ce tableau", 
                                help="Sauvegarder la configuration actuelle du tableau de bord"):
                # Collecter tous les paramètres actuels
                dashboard_config = {
                    "name": dashboard_name,
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "colors": {
                        "primary": color_primary,
                        "secondary": color_secondary
                    },
                    "charts": {
                        "bar": {
                            "x": bar_x,
                            "y": bar_y,
                            "type": bar_type,
                            "show_second": show_second_year,
                            "second_y": second_y
                        },
                        "pie": {
                            "col": pie_col,
                            "type": pie_type,
                            "center_value": center_value
                        },
                        "line": {
                            "x": line_x,
                            "y": line_y,
                            "type": line_type
                        },
                        "bubble": {
                            "x": bubble_x,
                            "y": bubble_y,
                            "size": bubble_size,
                            "color": bubble_color,
                            "type": bubble_type
                        },
                        "box": {
                            "col": boxplot_col,
                            "group_by": group_by,
                            "type": box_type
                        }
                    },
                    
                }
                
                # Vérifier si un tableau de bord avec ce nom existe déjà
                existing_idx = next((i for i, d in enumerate(st.session_state["saved_dashboards"]) 
                                  if d["name"] == dashboard_name), None)
                
                if existing_idx is not None:
                    # Mettre à jour le tableau existant
                    st.session_state["saved_dashboards"][existing_idx] = dashboard_config
                    st.sidebar.success(f"✅ Tableau '{dashboard_name}' mis à jour!")
                else:
                    # Ajouter un nouveau tableau
                    st.session_state["saved_dashboards"].append(dashboard_config)
                    st.sidebar.success(f"✅ Tableau '{dashboard_name}' sauvegardé!")
            
            # Paramètres globaux pour tous les graphiques
            smaller_height = 240  # Hauteur réduite pour les graphiques
            
            # Aperçu des données masqué par défaut mais accessible
            with st.expander("Aperçu des données"):
                st.dataframe(df)
                
                # Afficher les colonnes générées automatiquement si présentes
                generated_cols = [col for col in df.columns if col.startswith('_')]
                if generated_cols:
                    st.info(f"Colonnes générées automatiquement pour l'analyse: {', '.join(generated_cols)}")
            
            # Cartes récapitulatives en haut (en une seule ligne)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div style="background-color:{}; padding:5px; border-radius:10px; text-align:center;">
                    <h4 style="color:white; margin:0; font-size:0.9em;">Total Données</h4>
                    <h2 style="color:white; font-size:1.8em; margin:0;">{}</h2>
                </div>
                """.format(color_primary, len(df)), unsafe_allow_html=True)
                
            with col2:
                st.markdown("""
                <div style="background-color:white; padding:5px; border-radius:10px; border:1px solid #ddd; text-align:center;">
                    <h4 style="color:#333; margin:0; font-size:0.9em;">Colonnes</h4>
                    <h2 style="color:#333; font-size:1.8em; margin:0;">{}</h2>
                </div>
                """.format(len(df.columns) - len([c for c in df.columns if c.startswith('_')])), unsafe_allow_html=True)
                
            with col3:
                unique_count = 0
                if len(cat_columns) > 0 and cat_columns[0] in df.columns:
                    unique_count = df[cat_columns[0]].nunique()
                
                st.markdown("""
                <div style="background-color:white; padding:5px; border-radius:10px; border:1px solid #ddd; text-align:center;">
                    <h4 style="color:#333; margin:0; font-size:0.9em;">Valeurs Uniques</h4>
                    <h2 style="color:#333; font-size:1.8em; margin:0;">{}</h2>
                </div>
                """.format(unique_count), unsafe_allow_html=True)
                
            with col4:
                avg_value = 0
                if len(num_columns) > 0 and num_columns[0] in df.columns and num_columns[0] != '_count':
                    avg_value = round(df[num_columns[0]].mean(), 1)
                
                st.markdown("""
                <div style="background-color:white; padding:5px; border-radius:10px; border:1px solid #ddd; text-align:center;">
                    <h4 style="color:#333; margin:0; font-size:0.9em;">Moyenne</h4>
                    <h2 style="color:#333; font-size:1.8em; margin:0;">{}</h2>
                </div>
                """.format(avg_value), unsafe_allow_html=True)
            
            # SECTION POUR LES 5 GRAPHIQUES PRINCIPAUX VISIBLES SANS DÉFILEMENT
            st.markdown("### Principaux Indicateurs")
            
            # Première ligne - 3 graphiques en row
            col1, col2, col3 = st.columns([1, 1, 1])
            
            # Variables pour stocker les figures pour l'exportation PDF
            bar_fig = None
            pie_fig = None
            line_fig = None
            bubble_fig = None
            box_fig = None
            
            # Fonction de sécurité pour vérifier si les colonnes existent
            def safe_get_column(df, col_name, default_col=None):
                if col_name in df.columns:
                    return col_name
                elif default_col and default_col in df.columns:
                    return default_col
                elif '_count' in df.columns:
                    return '_count'
                elif len(df.columns) > 0:
                    return df.columns[0]
                return None
            
            # Graphique 1 - Barres/Lignes/Area selon le type choisi
            with col1:
                st.markdown("<div style='background-color:white; padding:10px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#333; margin-top:0;'>Tendances</h5>", unsafe_allow_html=True)
                
                try:
                    # Vérifier si les colonnes sélectionnées existent
                    x_col = safe_get_column(df, bar_x, cat_columns[0] if cat_columns else None)
                    y_col = safe_get_column(df, bar_y, num_columns[0] if num_columns else None)
                    
                    if x_col and y_col:
                        # Créer le graphique selon le type sélectionné
                        if bar_type == "bar":
                            fig = px.bar(df, x=x_col, y=y_col, 
                                        color_discrete_sequence=[color_primary],
                                        template="plotly_white")
                            
                            if show_second_year and second_y and second_y in df.columns:
                                fig.add_bar(x=df[x_col], y=df[second_y], 
                                           name=second_y, marker_color=color_secondary)
                                fig.update_layout(barmode='group')
                        elif bar_type == "line":
                            fig = px.line(df, x=x_col, y=y_col, 
                                         color_discrete_sequence=[color_primary],
                                         template="plotly_white")
                            
                            if show_second_year and second_y and second_y in df.columns:
                                fig.add_scatter(x=df[x_col], y=df[second_y], 
                                               mode='lines+markers',
                                               name=second_y, marker_color=color_secondary)
                        elif bar_type == "area":
                            fig = px.area(df, x=x_col, y=y_col, 
                                         color_discrete_sequence=[color_primary],
                                         template="plotly_white")
                            
                            if show_second_year and second_y and second_y in df.columns:
                                temp_df = df.copy()
                                fig = px.area(temp_df, x=x_col, y=[y_col, second_y], 
                                             color_discrete_sequence=[color_primary, color_secondary],
                                             template="plotly_white")
                        else:  # scatter
                            fig = px.scatter(df, x=x_col, y=y_col, 
                                            color_discrete_sequence=[color_primary],
                                            template="plotly_white")
                            
                            if show_second_year and second_y and second_y in df.columns:
                                fig.add_scatter(x=df[x_col], y=df[second_y], 
                                               mode='markers',
                                               name=second_y, marker_color=color_secondary)
                        
                        fig.update_layout(
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=smaller_height
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        bar_fig = fig
                    else:
                        st.info("Données insuffisantes pour ce graphique")
                except Exception as e:
                    st.info(f"Erreur lors de la création du graphique 1: {str(e)}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            
       
            
            # Graphique 2 - Circulaire/Autres selon le type choisi
            with col2:
                st.markdown("<div style='background-color:white; padding:10px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#333; margin-top:0;'>Répartition</h5>", unsafe_allow_html=True)
                
                if len(cat_columns) > 0 and cat_columns[0] != "Aucune colonne" and pie_col in df.columns:
                    # Limiter le nombre de catégories pour éviter les graphiques surchargés
                    value_counts = df[pie_col].value_counts()
                    
                    if pie_type == "pie":
                        if len(value_counts) > 10:
                            top_categories = value_counts.nlargest(9)
                            others = pd.Series({'Autres': value_counts[9:].sum()})
                            values = pd.concat([top_categories, others])
                            fig = px.pie(values=values.values, names=values.index, hole=0.6,
                                        color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        else:
                            fig = px.pie(df, names=pie_col, hole=0.6,
                                        color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        
                        fig.update_layout(
                            annotations=[dict(text=f"{center_value}%", x=0.5, y=0.5, font_size=20, showarrow=False)],
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=smaller_height,
                            showlegend=False  # Masquer la légende pour gagner de l'espace
                        )
                    elif pie_type == "bar":
                        if len(value_counts) > 10:
                            top_categories = value_counts.nlargest(10)
                            fig = px.bar(x=top_categories.index, y=top_categories.values,
                                        color_discrete_sequence=[color_primary])
                        else:
                            fig = px.bar(x=value_counts.index, y=value_counts.values,
                                        color_discrete_sequence=[color_primary])
                        fig.update_layout(
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=smaller_height,
                            xaxis_title="",
                            yaxis_title="Nombre"
                        )
                    elif pie_type == "funnel":
                        if len(value_counts) > 10:
                            top_categories = value_counts.nlargest(10)
                            fig = px.funnel(x=top_categories.values, y=top_categories.index,
                                            color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        else:
                            fig = px.funnel(x=value_counts.values, y=value_counts.index,color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        fig.update_layout(
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=smaller_height
                        )
                    elif pie_type == "treemap":
                        if len(value_counts) > 15:
                            top_categories = value_counts.nlargest(15)
                            temp_df = pd.DataFrame({"catégorie": top_categories.index, "valeur": top_categories.values})
                        else:
                            temp_df = pd.DataFrame({"catégorie": value_counts.index, "valeur": value_counts.values})
                        fig = px.treemap(temp_df, path=["catégorie"], values="valeur",
                                        color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        fig.update_layout(
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=smaller_height
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    pie_fig = fig
                else:
                    st.info("Données insuffisantes ou colonne invalide")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Graphique 3 - Ligne/autres selon le type choisi
            with col3:
                st.markdown("<div style='background-color:white; padding:10px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#333; margin-top:0;'>Évolution</h5>", unsafe_allow_html=True)
                
                if len(line_y) > 0 and line_x in df.columns and all(col in df.columns for col in line_y):
                    # Pour les graphiques en ligne, on peut agréger les données pour éviter les surcharges
                    try:
                        line_df = df.groupby(line_x)[line_y].mean().reset_index()
                        
                        if line_type == "line":
                            fig = px.line(line_df, x=line_x, y=line_y, 
                                        color_discrete_sequence=[color_primary, color_secondary])
                            
                            for trace in fig.data:
                                trace.mode = "lines+markers"
                        elif line_type == "bar":
                            fig = px.bar(line_df, x=line_x, y=line_y,
                                        color_discrete_sequence=[color_primary, color_secondary])
                        elif line_type == "area":
                            fig = px.area(line_df, x=line_x, y=line_y,
                                        color_discrete_sequence=[color_primary, color_secondary])
                        else:  # scatter
                            fig = px.scatter(line_df, x=line_x, y=line_y,
                                           color_discrete_sequence=[color_primary, color_secondary])
                        
                        fig.update_layout(
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=smaller_height
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        line_fig = fig
                    except Exception as e:
                        st.info(f"Erreur lors de la création du graphique en ligne: {e}")
                else:
                    st.info("Sélectionnez des métriques valides")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Deuxième ligne - 2 graphiques supplémentaires
            col1, col2 = st.columns(2)
            
            # Graphique 4 - Bulles/autres selon le type choisi
            with col1:
                st.markdown("<div style='background-color:white; padding:10px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#333; margin-top:0;'>Comparaison Multidimensionnelle</h5>", unsafe_allow_html=True)
                
                valid_bubble_columns = (bubble_x in df.columns and bubble_y in df.columns)
                
                if valid_bubble_columns:
                    if bubble_type == "scatter" and bubble_size in df.columns and bubble_color in df.columns:
                        fig = px.scatter(df, x=bubble_x, y=bubble_y, 
                                         size=bubble_size, 
                                         color=bubble_color,
                                         hover_name=cat_columns[0] if cat_columns else None,
                                         color_discrete_sequence=px.colors.sequential.Viridis)
                    elif bubble_type == "line":
                        fig = px.line(df, x=bubble_x, y=bubble_y,
                                     color_discrete_sequence=[color_primary])
                    elif bubble_type == "bar":
                        fig = px.bar(df, x=bubble_x, y=bubble_y,
                                    color_discrete_sequence=[color_primary])
                    else:  # area
                        fig = px.area(df, x=bubble_x, y=bubble_y,
                                     color_discrete_sequence=[color_primary])
                    
                    fig.update_layout(
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=smaller_height
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    bubble_fig = fig
                else:
                    st.info("Données insuffisantes ou colonnes invalides")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Graphique 5 - Boîte à moustaches/autres selon le type choisi
            with col2:
                st.markdown("<div style='background-color:white; padding:10px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color:#333; margin-top:0;'>Distribution des Valeurs</h5>", unsafe_allow_html=True)
                
                if len(num_columns) > 0 and boxplot_col in df.columns:
                    if box_type == "box":
                        if group_by != "Aucun" and group_by in df.columns:
                            fig = px.box(df, x=group_by, y=boxplot_col, 
                                        color=group_by,
                                        color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        else:
                            fig = px.box(df, y=boxplot_col, 
                                        color_discrete_sequence=[color_primary])
                    elif box_type == "violin":
                        if group_by != "Aucun" and group_by in df.columns:
                            fig = px.violin(df, x=group_by, y=boxplot_col, 
                                           color=group_by,
                                           color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        else:
                            fig = px.violin(df, y=boxplot_col, 
                                           color_discrete_sequence=[color_primary])
                    elif box_type == "histogram":
                        fig = px.histogram(df, x=boxplot_col, 
                                          color_discrete_sequence=[color_primary])
                        if group_by != "Aucun" and group_by in df.columns:
                            fig = px.histogram(df, x=boxplot_col, color=group_by,
                                              color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                    else:  # bar
                        if group_by != "Aucun" and group_by in df.columns:
                            # Agrégation pour graphique à barres
                            agg_df = df.groupby(group_by)[boxplot_col].mean().reset_index()
                            fig = px.bar(agg_df, x=group_by, y=boxplot_col,
                                        color=group_by,
                                        color_discrete_sequence=[color_primary, color_secondary, "#2D7DD2", "#97CC04"])
                        else:
                            bins = min(10, df[boxplot_col].nunique())
                            hist_vals, hist_bins = np.histogram(df[boxplot_col], bins=bins)
                            bin_centers = (hist_bins[:-1] + hist_bins[1:]) / 2
                            fig = px.bar(x=bin_centers, y=hist_vals,
                                        color_discrete_sequence=[color_primary])
                    
                    fig.update_layout(
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=smaller_height,
                        showlegend=False  # Masquer la légende pour gagner de l'espace
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    box_fig = fig
                else:
                    st.info("Données insuffisantes ou colonne invalide")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Les données importées ne contiennent pas de valeurs valides.")
    else:
        st.warning("Veuillez d'abord importer un fichier dans l'onglet 'Importation'.")
                                            