import streamlit as st
import pandas as pd
import pyodbc
import tempfile
import os
from utils import display_enhanced_filter_options

def show_page():
    # Titre avec animation et style amélioré
    st.markdown(
        """
    <div style="background-color:rgba(30, 58, 138, 0.9); padding:10px; border-radius:10px; margin-bottom:20px;">
        <h1 style="color:white; text-align:center;">📊 Analyse, Nettoyage et Préparation des Données</h1>
        <p style="color:white; text-align:center;">Votre assistant intelligent pour l'analyse de données</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Disposition en colonnes pour une meilleure organisation
    col1, col2 = st.columns([2, 1])

    with col1:
        # Téléchargement du fichier avec interface améliorée
        st.markdown(
            """
        <div style="background-color:rgba(248, 249, 250, 0.9); padding:15px; border-radius:10px; border:1px solid #ddd;">
            <h3 style="color:#1E3A8A;">📂 Importer vos données</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Téléchargez un fichier CSV, Excel ou Access", type=["csv", "xlsx", "accdb"]
        )

        if uploaded_file:
            with st.spinner("Chargement des données en cours..."):
                file_extension = uploaded_file.name.split(".")[-1]

                if "df" not in st.session_state or st.session_state["df"] is None:
                    if file_extension == "csv":
                        df = pd.read_csv(uploaded_file)
                    elif file_extension == "xlsx":
                        df = pd.read_excel(uploaded_file)
                    elif file_extension == "accdb":
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".accdb") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            st.session_state["db_path"] = tmp_file.name

                        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={st.session_state['db_path']}"
                        conn = pyodbc.connect(conn_str)
                        cursor = conn.cursor()

                        st.session_state["tables"] = [
                            table.table_name for table in cursor.tables(tableType="TABLE")
                        ]
                        selected_table = st.selectbox(
                            "📑 Sélectionnez une table", st.session_state["tables"]
                        )

                        if selected_table:
                            df = pd.read_sql(f"SELECT * FROM [{selected_table}]", conn)

                        conn.close()

                    st.session_state["df"] = df
                    st.session_state["df_filtered"] = df.copy()
                    st.success(f"✅ Fichier {uploaded_file.name} chargé avec succès!")

    with col2:
        # Statistiques du jeu de données
        if st.session_state["df"] is not None:
            nb_lignes = len(st.session_state["df"])
            nb_colonnes = len(st.session_state["df"].columns)
            nb_valeurs_manquantes = st.session_state["df"].isna().sum().sum()

    # Organisation des boutons d'actions dans la sidebar - UNIQUEMENT SI UN FICHIER EST CHARGÉ
    if st.session_state["df"] is not None:
        # Affichage des actions disponibles seulement si un fichier est chargé
        st.sidebar.markdown(
            """
        <div class="sidebar-section-heading">
            ACTIONS
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Boutons avec callbacks directs mais style préservé
        sidebar_col1, sidebar_col2 = st.sidebar.columns(2)

        with sidebar_col1:
            clean_clicked = st.button("🧹clean", key="clean_btn")

        with sidebar_col2:
            filter_clicked = st.button("🎛️ Filtrer", key="filter_btn")

        # Logique des boutons
        if clean_clicked:
            st.session_state["show_cleaning"] = not st.session_state["show_cleaning"]
            st.session_state["show_filtering"] = False
            st.rerun()

        if filter_clicked:
            st.session_state["show_filtering"] = not st.session_state["show_filtering"]
            st.session_state["show_cleaning"] = False
            st.rerun()

        # Affichage des options de filtrage améliorées
        if st.session_state["show_filtering"]:
            # Utiliser la nouvelle fonction pour afficher les options de filtrage améliorées
            display_enhanced_filter_options()

        # Options de nettoyage des données
        if st.session_state["show_cleaning"]:
            st.sidebar.markdown(
                """
            <div class="section-header">
                <h4 style="color:#1E3A8A; margin:0 0 8px 0;">🧹 Options de nettoyage</h4>
            </div>
            """,
                unsafe_allow_html=True,
            )

            cleaning_options = {}
            cleaning_options["dropna"] = st.sidebar.checkbox(
                "🗑️ Supprimer les lignes avec valeurs manquantes"
            )
            cleaning_options["fillna"] = st.sidebar.checkbox(
                "🔄 Remplacer valeurs manquantes par la moyenne"
            )
            cleaning_options["dropduplicates"] = st.sidebar.checkbox("📌 Supprimer les doublons")
            cleaning_options["normalize"] = st.sidebar.checkbox(
                "📊 Normaliser les données numériques"
            )

            apply_cleaning_clicked = st.sidebar.button(
                "✅ Appliquer le nettoyage", key="apply_cleaning"
            )

            if apply_cleaning_clicked:
                with st.spinner("Nettoyage en cours..."):
                    df_filtered = st.session_state["df"].copy()

                    if cleaning_options["dropna"]:
                        df_filtered.dropna(inplace=True)

                    if cleaning_options["fillna"]:
                        numeric_cols = df_filtered.select_dtypes(
                            include=["float64", "int64"]
                        ).columns
                        for col in numeric_cols:
                            df_filtered[col] = df_filtered[col].fillna(df_filtered[col].mean())

                    if cleaning_options["dropduplicates"]:
                        df_filtered.drop_duplicates(inplace=True)

                    if cleaning_options["normalize"]:
                        numeric_cols = df_filtered.select_dtypes(
                            include=["float64", "int64"]
                        ).columns
                        for col in numeric_cols:
                            min_val = df_filtered[col].min()
                            max_val = df_filtered[col].max()
                            if max_val > min_val:  # Éviter la division par zéro
                                df_filtered[col] = (df_filtered[col] - min_val) / (max_val - min_val)

                    st.session_state["df_filtered"] = df_filtered
                    st.success("✅ Nettoyage appliqué avec succès!")

        # Filtrage par catégories
        if "show_filter_category" in st.session_state and st.session_state["show_filter_category"]:
            st.sidebar.markdown(
                """
            <div class="section-header">
                <h4 style="color:#1E3A8A; margin:0 0 8px 0;">📌 Filtrage par catégories</h4>
            </div>
            """,
                unsafe_allow_html=True,
            )

            df_filtered = st.session_state["df"].copy()
            cat_columns = df_filtered.select_dtypes(include=["object", "category"]).columns
            filter_changes = False
            category_filters = {}

            for col in cat_columns:
                category_filters[col] = st.sidebar.multiselect(
                    f"📌 {col}", df_filtered[col].dropna().unique()
                )
                if category_filters[col]:
                    filter_changes = True

            if filter_changes:
                apply_cat_filters_clicked = st.sidebar.button(
                    "✅ Appliquer les filtres", key="apply_cat_filters"
                )

                if apply_cat_filters_clicked:
                    # Appliquer les filtres
                    for col, values in category_filters.items():
                        if values:
                            df_filtered = df_filtered[df_filtered[col].isin(values)]

                    st.session_state["df_filtered"] = df_filtered
                    st.success("✅ Filtres catégoriels appliqués!")

        # Filtrage par valeurs numériques
        if "show_filter_numeric" in st.session_state and st.session_state["show_filter_numeric"]:
            st.sidebar.markdown(
                """
            <div class="section-header">
                <h4 style="color:#1E3A8A; margin:0 0 8px 0;">📏 Filtrage par valeurs numériques</h4>
            </div>
            """,
                unsafe_allow_html=True,
            )

            df_filtered = st.session_state["df"].copy()
            num_columns = df_filtered.select_dtypes(include=["int64", "float64"]).columns
            filter_changes = False
            numeric_filters = {}

            for col in num_columns:
                min_val, max_val = float(df_filtered[col].min()), float(df_filtered[col].max())
                if min_val < max_val:
                    numeric_filters[col] = st.sidebar.slider(
                        f"📏 {col}", min_val, max_val, (min_val, max_val)
                    )
                    filter_changes = True

            if filter_changes:
                apply_num_filters_clicked = st.sidebar.button(
                    "✅ Appliquer les filtres", key="apply_num_filters"
                )

                if apply_num_filters_clicked:
                    # Appliquer les filtres
                    for col, range_vals in numeric_filters.items():
                        df_filtered = df_filtered[
                            (df_filtered[col] >= range_vals[0]) & (df_filtered[col] <= range_vals[1])
                        ]

                    st.session_state["df_filtered"] = df_filtered
                    st.success("✅ Filtres numériques appliqués!")

    # Affichage des données avec un titre adaptatif et des métriques
    if "df" in st.session_state and st.session_state["df"] is not None:
        container = st.container()

        if st.session_state.get("show_cleaning", False):
            container.markdown(
                """
            <div style="background-color:rgba(232, 244, 248, 0.9); padding:10px; border-radius:10px; margin-bottom:10px;">
                <h3 style="color:#000000; margin:0;">✅ Données nettoyées</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )
        elif st.session_state.get("show_filtering", False):
            container.markdown(
                """
            <div style="background-color:rgba(232, 244, 248, 0.9); padding:10px; border-radius:10px; margin-bottom:10px;">
                <h3 style="color:#000000; margin:0;">✅ Données filtrées</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            container.markdown(
                """
            <div style="background-color:rgba(232, 244, 248, 0.9); padding:10px; border-radius:10px; margin-bottom:10px;">
                <h3 style="color:#000000; margin:0;">🔍 Aperçu des données</h3>
            </div>
            """, 
                unsafe_allow_html=True,
            )
            
        # Métriques des données filtrées vs données originales
        if "df" in st.session_state and "df_filtered" in st.session_state:
            orig_rows = len(st.session_state["df"])
            filtered_rows = len(st.session_state["df_filtered"])
            percentage = (
                round((filtered_rows / orig_rows) * 100, 1) if orig_rows > 0 else 0
            )

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Lignes d'origine", orig_rows)
            with metric_col2:
                st.metric("Lignes filtrées", filtered_rows)
            with metric_col3:
                st.metric("Données conservées", f"{percentage}%")

        # Tableau de données avec options d'affichage
        tab1, tab2 = st.tabs(["📋 Tableau de données", "📊 Résumé statistique"])

        with tab1:
            # Option pour voir toutes les données ou limiter l'affichage
            show_all = st.checkbox("Afficher toutes les lignes", value=False)

            if show_all:
                st.dataframe(st.session_state["df_filtered"], use_container_width=True)
            else:
                st.dataframe(st.session_state["df_filtered"].head(50), use_container_width=True)
                st.info(
                    f"Affichage limité aux 50 premières lignes. {len(st.session_state['df_filtered'])} lignes au total."
                )

        with tab2:
            if "df_filtered" in st.session_state and not st.session_state["df_filtered"].empty:
                st.write(st.session_state["df_filtered"].describe())

                # Informations sur les types de données
                st.markdown("#### Types de données:")
                dtypes = st.session_state["df_filtered"].dtypes.reset_index()
                dtypes.columns = ["Colonne", "Type"]
                st.dataframe(dtypes, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible après filtrage.")