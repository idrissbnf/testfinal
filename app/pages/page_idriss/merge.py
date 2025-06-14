import base64
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

def show_page():
    st.title("🔀 Fusion et Nettoyage de Données")
    
    if st.session_state["db_path"]:
        try:
            conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={st.session_state['db_path']}"
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Sélection des tables
            selected_tables = st.multiselect("Sélectionnez les tables à combiner", st.session_state["tables"])
            
            combined_df = pd.DataFrame()
            selected_columns = {}
            
            if selected_tables:
                for table in selected_tables:
                    df_temp = pd.read_sql(f"SELECT * FROM [{table}]", conn)
                    columns = st.multiselect(f"Sélectionnez les colonnes de {table}", df_temp.columns, key=table)
                    if columns:
                        selected_columns[table] = columns
                        if combined_df.empty:
                            combined_df = df_temp[columns]
                        else:
                            combined_df = pd.concat([combined_df, df_temp[columns]], axis=1)
                
                st.session_state["df_merged"] = combined_df
                st.write("### Données combinées :")
                st.dataframe(combined_df)
            
            conn.close()
        except Exception as e:
            st.error(f"Erreur de connexion à la base de données: {e}")
    else:
        st.warning("Veuillez d'abord charger une base de données dans l'onglet Accueil")
    
    # Nettoyage des données fusionnées
    if "df_merged" in st.session_state and not st.session_state["df_merged"].empty:
        df_cleaned = st.session_state["df_merged"].copy()
        
        # Sidebar buttons for toggling sections
        with st.sidebar:
            st.header("Options de traitement")
            if st.button("🧹 Nettoyage des Données"):
                st.session_state["show_cleaning_fusion"] = not st.session_state.get("show_cleaning_fusion", False)

            if st.button("🎛️ Filtrage des Données"):
                st.session_state["show_filtering_fusion"] = not st.session_state.get("show_filtering_fusion", False)
            
            if st.button("📈 Visualisation des Données"):
                st.session_state["show_visualization_fusion"] = not st.session_state.get("show_visualization_fusion", False)

        # Nettoyage des données fusionnées
        if st.session_state.get("show_cleaning_fusion", False):
            st.subheader("🧹 Nettoyage des Données")
            
            with st.expander("Options de nettoyage", expanded=True):
                if st.checkbox("Supprimer les valeurs manquantes"):
                    df_cleaned.dropna(inplace=True)
                    st.write("✔️ Valeurs manquantes supprimées.")
                    
                if st.checkbox("Supprimer les doublons"):
                    df_cleaned.drop_duplicates(inplace=True)
                    st.write("✔️ Doublons supprimés.")
                
                numeric_cols = df_cleaned.select_dtypes(include=['float64', 'int64']).columns
                if st.checkbox("Normaliser les données numériques") and len(numeric_cols) > 0:
                    df_cleaned[numeric_cols] = (df_cleaned[numeric_cols] - df_cleaned[numeric_cols].min()) / (df_cleaned[numeric_cols].max() - df_cleaned[numeric_cols].min())
                    st.write("✔️ Normalisation appliquée.")
        
        # Filtrage dynamique
        df_filtered = df_cleaned.copy()
        if st.session_state.get("show_filtering_fusion", False):
            st.subheader("🎛️ Filtrage des Données")
            
            with st.expander("Filtrer par catégories", expanded=True):
                cat_columns = df_filtered.select_dtypes(include=["object", "category"]).columns
                for col in cat_columns:
                    selected_values = st.multiselect(f"Filtrer {col}", df_filtered[col].dropna().unique())
                    if selected_values:
                        df_filtered = df_filtered[df_filtered[col].isin(selected_values)]
            
            with st.expander("Filtrer par valeurs numériques", expanded=True):
                num_columns = df_filtered.select_dtypes(include=["int64", "float64"]).columns
                for col in num_columns:
                    min_val, max_val = float(df_filtered[col].min()), float(df_filtered[col].max())
                    if min_val < max_val:
                        selected_range = st.slider(f"Filtrer {col}", min_val, max_val, (min_val, max_val))
                        df_filtered = df_filtered[(df_filtered[col] >= selected_range[0]) & (df_filtered[col] <= selected_range[1])]
        
        # Sauvegarde du dataframe filtré dans session_state
        st.session_state["df_filtered"] = df_filtered
        
        # Affichage des données filtrées
        st.write("### Données après Nettoyage et Filtrage :")
        st.dataframe(df_filtered)
        
        # Option d'export
        if not df_filtered.empty:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Exporter les données (CSV)"):
                    csv = df_filtered.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="donnees_fusionnees.csv">Télécharger le fichier CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
            with col2:
                if st.button("📊 Exporter le résumé statistique (CSV)"):
                    csv_stats = df_filtered.describe().to_csv()
                    b64_stats = base64.b64encode(csv_stats.encode()).decode()
                    href_stats = f'<a href="data:file/csv;base64,{b64_stats}" download="resume_statistique.csv">Télécharger le résumé statistique</a>'
                    st.markdown(href_stats, unsafe_allow_html=True)
        
        # Résumé statistique
        st.subheader("📊 Résumé Statistique des Données Fusionnées :")
        if not df_filtered.empty:
            st.write(df_filtered.describe())
        else:
            st.warning("Aucune donnée après nettoyage et filtrage.")
        
        # Visualisation des données fusionnées
        if st.session_state.get("show_visualization_fusion", False):
            st.subheader("📈 Visualisation des Données Fusionnées")
            if not df_filtered.empty:
                with st.expander("Options de visualisation", expanded=True):
                    graph_type = st.selectbox("Choisissez un type de graphique", ["Histogramme", "Nuage de points", "Graphique en barres", "Camembert"])
                    
                    if graph_type == "Histogramme":
                        num_cols = df_filtered.select_dtypes(include=['int64', 'float64']).columns
                        if len(num_cols) > 0:
                            column = st.selectbox("Sélectionnez une colonne numérique", num_cols)
                            nbins = st.slider("Nombre de groupes", 5, 100, 30)
                            fig = px.histogram(df_filtered, x=column, nbins=nbins, title=f"Histogramme de {column}")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Aucune colonne numérique disponible pour l'histogramme")
                    
                    elif graph_type == "Nuage de points":
                        x_col = st.selectbox("Sélectionnez l'axe X", df_filtered.columns)
                        y_col = st.selectbox("Sélectionnez l'axe Y", df_filtered.columns, index=min(1, len(df_filtered.columns)-1))
                        if x_col and y_col:
                            color_col = st.selectbox("Colonne pour la couleur (optionnel)", ["Aucune"] + list(df_filtered.columns))
                            color = None if color_col == "Aucune" else color_col
                            fig = px.scatter(df_filtered, x=x_col, y=y_col, color=color, title=f"Nuage de points : {x_col} vs {y_col}")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif graph_type == "Graphique en barres":
                        cat_cols = df_filtered.select_dtypes(include=['object', 'category']).columns
                        if len(cat_cols) > 0:
                            column = st.selectbox("Sélectionnez une colonne catégorielle", cat_cols)
                            limit = st.slider("Limite de catégories à afficher", 1, 50, 10)
                            count_data = df_filtered[column].value_counts().nlargest(limit).reset_index()
                            fig = px.bar(count_data, x='index', y=column, title=f"Top {limit} catégories de {column}")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Aucune colonne catégorielle disponible pour le graphique en barres")
                    
                    elif graph_type == "Camembert":
                        cat_cols = df_filtered.select_dtypes(include=['object', 'category']).columns
                        if len(cat_cols) > 0:
                            column = st.selectbox("Sélectionnez une colonne catégorielle", cat_cols)
                            limit = st.slider("Limite de catégories à afficher", 1, 20, 5)
                            count_data = df_filtered[column].value_counts().nlargest(limit)
                            fig = px.pie(values=count_data.values, names=count_data.index, title=f"Répartition des top {limit} catégories de {column}")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Aucune colonne catégorielle disponible pour le camembert")
            else:
                st.warning("Aucune donnée disponible pour la visualisation.")
    elif "df_merged" in st.session_state and st.session_state["df_merged"].empty:
        st.warning("Le jeu de données fusionné est vide. Veuillez sélectionner des tables et des colonnes.")