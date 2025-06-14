import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid

def show_page():
    """
    Belghiti page - Strategic Dashboard for Educational Performance Indicators
    """
    # Function to load data
    @st.cache_data
    def load_data(file):
        try:
            if file.name.endswith("csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {str(e)}")
            return None

    # Page Header
    st.title("📊 Suivi personnalisé des ICSE - G Belghiti")
    st.markdown("---")

    # Sidebar for file uploads
    st.sidebar.header("📂 Importation des Données")
    uploaded_file_ficher2 = st.sidebar.file_uploader("Importer Ficher2 (Excel)", type=["xlsx"], key="ficher2_file_belghiti")
    uploaded_file_perf = st.sidebar.file_uploader("Importer ficher1 (Excel/CSV)", type=["xlsx", "xls", "csv"], key="perf_file_belghiti")
    uploaded_file_cant = st.sidebar.file_uploader("Importer ficher3 (Excel/CSV)", type=["xlsx", "xls", "csv"], key="cantines_file_belghiti")

    # Initialize dataframes
    data_ficher2 = None
    data_perf = None
    data_cant = None

    # Static KPIs - Enseignants et Scolarisation
    st.subheader("📋 Indicateurs Clés - Enseignants et Scolarisation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👨‍🏫 Enseignants Primaire", "2,524")
        st.metric("👨‍🏫 Enseignants Collège", "942")
        st.metric("👨‍🏫 Enseignants Qualifiant", "735")
    
    with col2:
        st.metric("👥 Ratio élèves/enseignant Primaire", "31.51", delta="-3.49", delta_color="inverse")
        st.metric("👥 Ratio élèves/enseignant Collège", "28.68", delta="-1.32", delta_color="inverse")
        st.metric("👥 Ratio élèves/enseignant Qualifiant", "16.59", delta="0.59", delta_color="normal")
    
    with col3:
        st.metric("🎓 Taux scolarisation Primaire", "100%", delta="0%")
        st.metric("🎓 Taux scolarisation Collège", "56.71%", delta="6.71%")
        st.metric("🎓 Taux scolarisation Qualifiant", "20.41%", delta="-9.59%", delta_color="inverse")

    st.markdown("---")

    # Process Ficher2 data
    if uploaded_file_ficher2:
        df_ficher2 = load_data(uploaded_file_ficher2)
        if df_ficher2 is None:
            st.warning("⚠️ Erreur dans le chargement de ficher2.xlsx. Vérifiez le fichier.")
        else:
            # Rename columns for Ficher2
            cols_ficher2 = {
                'Commune': 'commune',
                'Etablissement': 'etab',
                'Niveau': 'niveau',
                'Total Nombre de classes': 'total_classes',
                'Nombre de classes  Multiniveaux': 'multiniveaux_classes',
                'classes Amazigh': 'amazigh_classes',
                'inférieur à 24 Nombre de classes': 'under_24',
                'entre 24 et 35 Nombre de classes': '24_35',
                'entre 36 et 40 Nombre de classes': '36_40',
                'entre 41 et 45 Nombre de classes': '41_45',
                'entre 46 et 50 Nombre de classes': '46_50',
                'supérieur à 51 Nombre de classes': 'over_51'
            }
            df_ficher2.rename(columns={k: cols_ficher2[k] for k in cols_ficher2 if k in df_ficher2.columns}, inplace=True)

            # Clean data: Replace NaN and ensure string type for filters
            filter_columns = ['commune', 'etab', 'niveau']
            for col in filter_columns:
                if col in df_ficher2.columns:
                    df_ficher2[col] = df_ficher2[col].fillna('Inconnu').astype(str)

            # Verify required columns
            required_columns_ficher2 = ['commune', 'etab', 'niveau', 'total_classes']
            missing_required = [col for col in required_columns_ficher2 if col not in df_ficher2.columns]
            if missing_required:
                st.error(f"❌ Colonnes manquantes dans ficher2.xlsx : {', '.join(missing_required)}")
                st.warning("Vérifiez le nom exact des colonnes dans ficher2.xlsx.")
            else:
                # Fallback: Calculate total_classes if missing
                if 'total_classes' not in df_ficher2.columns and all(col in df_ficher2.columns for col in ['under_24', '24_35', '36_40', '41_45', '46_50', 'over_51']):
                    st.warning("⚠️ La colonne 'total_classes' est manquante. Calcul à partir des colonnes de taille de classe.")
                    df_ficher2['total_classes'] = df_ficher2[['under_24', '24_35', '36_40', '41_45', '46_50', 'over_51']].sum(axis=1)

                # Filters for Ficher2
                st.sidebar.header("🔍 Filtres Performances des Classes")
                commune_ficher2 = st.sidebar.multiselect("Commune", options=sorted(df_ficher2['commune'].dropna().unique()), key="commune_ficher2_belghiti")
                etab_opts_ficher2 = df_ficher2[df_ficher2['commune'].isin(commune_ficher2)]['etab'].unique() if commune_ficher2 else df_ficher2['etab'].unique()
                etab_ficher2 = st.sidebar.multiselect("Établissement", options=sorted(etab_opts_ficher2), key="etab_ficher2_belghiti")
                niveau_ficher2 = st.sidebar.multiselect("Niveau", options=sorted(df_ficher2['niveau'].dropna().unique()), key="niveau_ficher2_belghiti")

                # Build filter dynamically
                filt_ficher2 = pd.Series(True, index=df_ficher2.index)
                if commune_ficher2:
                    filt_ficher2 &= df_ficher2['commune'].isin(commune_ficher2)
                if etab_ficher2:
                    filt_ficher2 &= df_ficher2['etab'].isin(etab_ficher2)
                if niveau_ficher2:
                    filt_ficher2 &= df_ficher2['niveau'].isin(niveau_ficher2)

                try:
                    data_ficher2 = df_ficher2[filt_ficher2]
                    if data_ficher2.empty:
                        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés pour ficher2.xlsx.")
                    else:
                        # Calculate indicators
                        total_classes = 4223  # Hard-coded as per request
                        overcrowded_classes = data_ficher2[['46_50', 'over_51']].sum().sum() if all(col in data_ficher2.columns for col in ['46_50', 'over_51']) else 0
                        overcrowding_rate = (overcrowded_classes / total_classes * 100) if total_classes > 0 else 0
                        multiniveaux_classes = data_ficher2['multiniveaux_classes'].sum() if 'multiniveaux_classes' in data_ficher2.columns else 0
                        multiniveaux_percentage = (multiniveaux_classes / total_classes * 100) if total_classes > 0 else 0
                        amazigh_etab = data_ficher2[data_ficher2['amazigh_classes'] > 0]['etab'].nunique() if 'amazigh_classes' in data_ficher2.columns else 0
                        total_etab = data_ficher2['etab'].nunique()
                        amazigh_percentage = (amazigh_etab / total_etab * 100) if total_etab > 0 else 0

                        # Ficher2 KPIs
                        st.subheader("📊 Indicateurs Clés - Performances des Classes")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("🏫 Total Classes", f"{int(total_classes):,}")
                        with col2:
                            st.metric("⚠️ Taux Encombrement (>45)", f"{overcrowding_rate:.2f}%", delta=f"{overcrowded_classes} classes")
                        with col3:
                            st.metric("📚 Classes Multi-Niveaux", f"{multiniveaux_percentage:.2f}%", delta=f"{multiniveaux_classes} classes")
                        with col4:
                            st.metric("🗣️ Établissements Amazigh", f"{amazigh_percentage:.2f}%", delta=f"{amazigh_etab} établissements")

                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement de ficher2.xlsx : {str(e)}")

    # Process Performance and Cantines/Internats data
    if uploaded_file_perf or uploaded_file_cant:
        # Initialize dataframes
        df_perf = None
        df_cant = None

        # Load and process performance data
        if uploaded_file_perf:
            df_perf = load_data(uploaded_file_perf)
            if df_perf is not None:
                # Standardize column names
                cols_perf = {
                    "CD_ETAB": "code_etab",
                    "CD_MIL": "milieu",
                    "id_resultat": "resultat",
                    "MoyenneGen": "moyenne",
                    "id_Genre": "genre",
                    "id_situation": "situation",
                    "id_StatutEleve": "statut_eleve",
                    "CD_CYCLE": "cycle",
                    "NOM_ETABL": "etab",
                    "ll_com": "commune",
                    "Fileire": "filiere",
                    "Cantine": "cantine",
                    "Internat": "internat"
                }
                df_perf.rename(columns={c: cols_perf[c] for c in cols_perf if c in df_perf.columns}, inplace=True)

                # Derive 'niveau' from 'filiere'
                if "filiere" in df_perf.columns:
                    df_perf["niveau"] = df_perf["filiere"].str.extract(r"(\d+° Année|Tronc Commun|1ère Année Bac|2ème Année Bac)")
                    df_perf["niveau"] = df_perf["niveau"].fillna("Inconnu")

                # Map values
                if "resultat" in df_perf.columns:
                    df_perf["resultat"] = df_perf["resultat"].map({1: "Admis", 2: "Non Admis"}).fillna("Inconnu")
                if "situation" in df_perf.columns:
                    df_perf["situation"] = df_perf["situation"].map({1: "1", 2: "2", 5: "5"}).fillna("Inconnu")
                if "genre" in df_perf.columns:
                    df_perf["genre"] = df_perf["genre"].map({1: "Masculin", 2: "Féminin"}).fillna("Inconnu")
                if "milieu" in df_perf.columns:
                    df_perf["milieu"] = df_perf["milieu"].map({1: "Urbain", 2: "Rural"}).fillna("Inconnu")
                if "cantine" in df_perf.columns:
                    df_perf["cantine"] = df_perf["cantine"].fillna(False)
                if "internat" in df_perf.columns:
                    df_perf["internat"] = df_perf["internat"].fillna(False)

                # Clean filter columns
                filter_columns = ["genre", "milieu", "commune", "etab", "cycle", "niveau"]
                for col in filter_columns:
                    if col in df_perf.columns:
                        df_perf[col] = df_perf[col].fillna("Inconnu").astype(str)

                # Verify required columns
                required_columns_perf = ["resultat", "niveau", "cycle", "situation"]
                missing_required = [col for col in required_columns_perf if col not in df_perf.columns]
                if missing_required:
                    st.error(f"❌ Colonnes manquantes dans les données de performance : {', '.join(missing_required)}")
                    df_perf = None

        # Load and process cantines/internats data
        if uploaded_file_cant:
            df_cant = load_data(uploaded_file_cant)
            if df_cant is not None:
                # Standardize column names
                cols_cant = {
                    "CD_COM": "code_commune",
                    "Cantine": "cantine",
                    "Internat": "internat",
                    "ll_com": "commune"
                }
                df_cant.rename(columns={c: cols_cant[c] for c in cols_cant if c in df_cant.columns}, inplace=True)

                # Clean commune column
                if "commune" in df_cant.columns:
                    df_cant["commune"] = df_cant["commune"].fillna("Inconnu").astype(str)

                # Verify required columns
                required_columns_cant = ["cantine", "internat", "commune"]
                missing_required = [col for col in required_columns_cant if col not in df_cant.columns]
                if missing_required:
                    st.error(f"❌ Colonnes manquantes dans les données de cantines/internats : {', '.join(missing_required)}")
                    df_cant = None

        # Filters for Performance/Cantines
        st.sidebar.header("🔍 Filtres Performance/Cantines")
        if df_perf is not None:
            genre_sel = st.sidebar.multiselect("Genre", options=sorted(df_perf["genre"].dropna().unique()), key="genre_perf_belghiti") if "genre" in df_perf.columns else []
            milieu_sel = st.sidebar.multiselect("Milieu", options=sorted(df_perf["milieu"].dropna().unique()), key="milieu_perf_belghiti") if "milieu" in df_perf.columns else []
            commune_perf_sel = st.sidebar.multiselect("Commune (Performance)", options=sorted(df_perf["commune"].dropna().unique()), key="commune_perf_belghiti") if "commune" in df_perf.columns else []
            etab_opts = df_perf[df_perf["commune"].isin(commune_perf_sel)]["etab"].unique() if commune_perf_sel and "commune" in df_perf.columns and "etab" in df_perf.columns else df_perf["etab"].unique() if "etab" in df_perf.columns else []
            etab_sel = st.sidebar.multiselect("Établissement (Performance)", options=sorted(list(etab_opts)), key="etab_perf_belghiti") if len(etab_opts) else []
            cycle_sel = st.sidebar.multiselect("Cycle", options=sorted(df_perf["cycle"].dropna().unique()), key="cycle_perf_belghiti") if "cycle" in df_perf.columns else []
            niveau_opts = df_perf[df_perf["cycle"].isin(cycle_sel)]["niveau"].unique() if cycle_sel and "cycle" in df_perf.columns and "niveau" in df_perf.columns else df_perf["niveau"].unique() if "niveau" in df_perf.columns else []
            niveau_sel = st.sidebar.multiselect("Niveau (Performance)", options=sorted(niveau_opts), key="niveau_perf_belghiti") if len(niveau_opts) else []

        if df_cant is not None:
            commune_cant_sel = st.sidebar.multiselect("Commune (Cantines/Internats)", options=sorted(df_cant["commune"].dropna().unique()), key="commune_cant_belghiti") if "commune" in df_cant.columns else []

        # Process performance data with filters
        if df_perf is not None:
            # Apply filters
            filt_perf = pd.Series(True, index=df_perf.index)
            if "genre" in df_perf.columns and genre_sel:
                filt_perf &= df_perf["genre"].isin(genre_sel)
            if "milieu" in df_perf.columns and milieu_sel:
                filt_perf &= df_perf["milieu"].isin(milieu_sel)
            if "commune" in df_perf.columns and commune_perf_sel:
                filt_perf &= df_perf["commune"].isin(commune_perf_sel)
            if "etab" in df_perf.columns and etab_sel:
                filt_perf &= df_perf["etab"].isin(etab_sel)
            if "cycle" in df_perf.columns and cycle_sel:
                filt_perf &= df_perf["cycle"].isin(cycle_sel)
            if "niveau" in df_perf.columns and niveau_sel:
                filt_perf &= df_perf["niveau"].isin(niveau_sel)

            try:
                data_perf = df_perf[filt_perf]
                if data_perf.empty:
                    st.warning("⚠️ Aucun élève ne correspond aux filtres sélectionnés pour les données de performance.")
                    data_perf = None
            except Exception as e:
                st.error(f"❌ Erreur lors de l'application du filtre de performance : {e}")
                df_perf = None

        # Process cantines/internats data with filters
        if df_cant is not None:
            # Apply filters
            filt_cant = pd.Series(True, index=df_cant.index)
            if "commune" in df_cant.columns and commune_cant_sel:
                filt_cant &= df_cant["commune"].isin(commune_cant_sel)

            try:
                data_cant = df_cant[filt_cant]
                if data_cant.empty:
                    st.warning("⚠️ Aucun enregistrement ne correspond aux filtres sélectionnés pour les données de cantines/internats.")
                    data_cant = None
            except Exception as e:
                st.error(f"❌ Erreur lors de l'application du filtre des cantines/internats : {e}")
                df_cant = None

        # KPIs - Performance
        if data_perf is not None:
            st.subheader("📈 Indicateurs Clés - Performance Globale des Élèves")
            total_etud = len(data_perf)
            total_etab = data_perf["etab"].nunique() if "etab" in data_perf.columns else 0
            total_commune_perf = data_perf["commune"].nunique() if "commune" in data_perf.columns else 0
            success_mask = data_perf["resultat"] == "Admis"
            failure_mask = data_perf["resultat"] == "Non Admis"
            dropout_mask = data_perf["situation"].isin(["2", "5"])
            social_support_mask = (data_perf["cantine"] == True) | (data_perf["internat"] == True)
            total_success = data_perf[success_mask].shape[0]
            total_failure = data_perf[failure_mask].shape[0]
            total_dropout = data_perf[dropout_mask].shape[0]
            total_social_support = data_perf[social_support_mask].shape[0]

            # Performance metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total Étudiants", f"{total_etud:,}")
                success_rate = (total_success / total_etud * 100) if total_etud else 0
                st.metric("✅ Taux de Réussite", f"{success_rate:.1f}%", delta=f"{total_success:,} étudiants")
            
            with col2:
                failure_rate = (total_failure / total_etud * 100) if total_etud else 0
                st.metric("❌ Taux d'Échec", f"{failure_rate:.1f}%", delta=f"{total_failure:,} étudiants", delta_color="inverse")
                dropout_rate = (total_dropout / total_etud * 100) if total_etud else 0
                st.metric("🚪 Taux d'Abandon", f"{dropout_rate:.1f}%", delta=f"{total_dropout:,} étudiants", delta_color="inverse")
            
            with col3:
                st.metric("🏫 Total Établissements", f"{total_etab:,}")
                st.metric("🏘️ Total Communes", f"{total_commune_perf:,}")

            # Social support metrics
            if data_cant is not None:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🍽️ Bénéficiaires Appui Social", f"{total_social_support:,}")
                with col2:
                    total_cantines = data_cant[data_cant["cantine"] == True].shape[0]
                    st.metric("🍽️ Total Cantines", f"{total_cantines:,}")
                with col3:
                    total_internats = data_cant[data_cant["internat"] == True].shape[0]
                    st.metric("🏠 Total Internats", f"{total_internats:,}")

    # Export functionality
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Exporter les Résultats")
    
    if data_ficher2 is not None:
        if st.sidebar.button("📊 Exporter Ficher2 CSV", key="ficher2_csv_belghiti"):
            data_ficher2.to_csv("belghiti_ficher2_resultats.csv", index=False, encoding="utf-8-sig")
            st.sidebar.success("✅ Fichier CSV exporté : belghiti_ficher2_resultats.csv")

    if data_perf is not None:
        if st.sidebar.button("📈 Exporter Performance CSV", key="perf_csv_belghiti"):
            data_perf.to_csv("belghiti_performance_resultats.csv", index=False, encoding="utf-8-sig")
            st.sidebar.success("✅ Fichier CSV exporté : belghiti_performance_resultats.csv")

    if data_cant is not None:
        if st.sidebar.button("🍽️ Exporter Cantines CSV", key="cant_csv_belghiti"):
            data_cant.to_csv("belghiti_cantines_resultats.csv", index=False, encoding="utf-8-sig")
            st.sidebar.success("✅ Fichier CSV exporté : belghiti_cantines_resultats.csv")

    # Data previews
    if data_perf is not None:
        with st.expander("👀 Aperçu des Données de Performance"):
            st.dataframe(data_perf.head(), use_container_width=True)
    
    if data_cant is not None:
        with st.expander("👀 Aperçu des Données de Cantines/Internats"):
            st.dataframe(data_cant.head(), use_container_width=True)

    if data_ficher2 is not None:
        with st.expander("👀 Aperçu des Données de Classes"):
            st.dataframe(data_ficher2.head(), use_container_width=True)

    # Visualizations section
    st.markdown("---")
    st.header("📊 Visualisations et Analyses")

    # Helper functions for charts
    def create_bar_chart_ficher2(data, x, y, color, title, barmode="group"):
        total = data[y].sum()
        data['Pourcentage'] = (data[y] / total * 100) if total > 0 else 0
        fig = px.bar(data, x=x, y=y, color=color, barmode=barmode, title=title,
                     text=data['Pourcentage'].apply(lambda x: f"{x:.2f}%"))
        fig.update_layout(yaxis_tickformat="d", xaxis_title=x, yaxis_title="Nombre", legend_title=color)
        fig.update_traces(textposition="auto")
        return fig

    def create_pie_chart(data, names, values, title):
        fig = px.pie(data, names=names, values=values, title=title)
        fig.update_traces(textinfo='percent+label')
        return fig

    def create_bar_chart(data, x, y, color, title, barmode="group"):
        if color:
            total = data.groupby(x)[y].sum()
            data["Pourcentage"] = data[y] / data[x].map(total) * 100
            fig = px.bar(data, x=x, y=y, color=color, barmode=barmode, title=title, text=data["Pourcentage"].apply(lambda x: f"{x:.1f}%"))
            fig.update_traces(textposition="auto")
        else:
            total = data[y].sum()
            data["Pourcentage"] = data[y] / total * 100 if total > 0 else 0
            fig = px.bar(data, x=x, y=y, barmode=barmode, title=title, text=data["Pourcentage"].apply(lambda x: f"{x:.1f}%"))
            fig.update_traces(textposition="auto")
        fig.update_layout(yaxis_tickformat="d", xaxis_title=x, yaxis_title="Nombre", legend_title=color if color else None)
        return fig

    # Ficher2 Visualizations
    if data_ficher2 is not None and not data_ficher2.empty:
        st.subheader("📊 Visualisations - Performances des Classes")
        
        # Total classes by commune
        if 'total_classes' in data_ficher2.columns and 'commune' in data_ficher2.columns:
            total_classes_data = data_ficher2.groupby('commune')['total_classes'].sum().reset_index()
            fig_total_classes = create_bar_chart_ficher2(total_classes_data, 'commune', 'total_classes', None, "Nombre Total de Classes par Commune")
            st.plotly_chart(fig_total_classes, use_container_width=True)

        # Overcrowding visualization
        if all(col in data_ficher2.columns for col in ['46_50', 'over_51']):
            overcrowding_data = data_ficher2.groupby('commune')[['46_50', 'over_51']].sum().sum(axis=1).reset_index(name='Overcrowded_Classes')
            fig_overcrowding = create_bar_chart_ficher2(overcrowding_data, 'commune', 'Overcrowded_Classes', None, "Nombre de Classes avec >45 Élèves par Commune")
            st.plotly_chart(fig_overcrowding, use_container_width=True)

        # Multi-level classes pie chart
        if 'multiniveaux_classes' in data_ficher2.columns and 'total_classes' in data_ficher2.columns:
            multiniveaux_classes_total = data_ficher2['multiniveaux_classes'].sum()
            total_classes_total = data_ficher2['total_classes'].sum()
            multi_data = pd.DataFrame({
                'Type': ['Multi-Niveaux', 'Autres'],
                'Nombre': [multiniveaux_classes_total, total_classes_total - multiniveaux_classes_total]
            })
            fig_multi = create_pie_chart(multi_data, 'Type', 'Nombre', "Répartition des Classes Multi-Niveaux")
            st.plotly_chart(fig_multi, use_container_width=True)

    # Performance Visualizations
    if data_perf is not None and not data_perf.empty:
        st.subheader("📈 Visualisations - Performance des Élèves")
        
        # Success by gender
        if "genre" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_genre = data_perf[success_mask].groupby("genre").size().reset_index(name="Réussites")
            fig_success_genre = create_bar_chart(success_genre, "genre", "Réussites", None, "Réussites par Genre")
            st.plotly_chart(fig_success_genre, use_container_width=True)

        # Performance by cycle
        # Performance by cycle
        if "cycle" in data_perf.columns and "niveau" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_cycle = data_perf[success_mask].groupby(["cycle", "niveau"]).size().reset_index(name="Réussites")
            fig_success_cycle = create_bar_chart(success_cycle, "niveau", "Réussites", "cycle", "Réussites par Cycle et Niveau")
            st.plotly_chart(fig_success_cycle, use_container_width=True)

        # Success by establishment
        if "etab" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_etab = data_perf[success_mask].groupby("etab").size().reset_index(name="Réussites")
            fig_success_etab = create_bar_chart(success_etab, "etab", "Réussites", None, "Réussites par Établissement")
            st.plotly_chart(fig_success_etab, use_container_width=True)

        # Success by commune
        if "commune" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_commune = data_perf[success_mask].groupby("commune").size().reset_index(name="Réussites")
            fig_success_commune = create_bar_chart(success_commune, "commune", "Réussites", None, "Réussites par Commune")
            st.plotly_chart(fig_success_commune, use_container_width=True)

        # Success by milieu
        if "milieu" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_milieu = data_perf[success_mask].groupby("milieu").size().reset_index(name="Réussites")
            fig_success_milieu = create_bar_chart(success_milieu, "milieu", "Réussites", None, "Réussites par Milieu")
            st.plotly_chart(fig_success_milieu, use_container_width=True)

        # Success pie charts
        if "genre" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_genre = data_perf[success_mask].groupby("genre").size().reset_index(name="Réussites")
            fig_pie_success_genre = px.pie(success_genre, names="genre", values="Réussites", title="Répartition des Réussites par Genre")
            st.plotly_chart(fig_pie_success_genre, use_container_width=True)

        if "cycle" in data_perf.columns:
            success_mask = data_perf["resultat"] == "Admis"
            success_cycle_dist = data_perf[success_mask].groupby("cycle").size().reset_index(name="Réussites")
            fig_pie_success_cycle = px.pie(success_cycle_dist, names="cycle", values="Réussites", title="Répartition des Réussites par Cycle")
            st.plotly_chart(fig_pie_success_cycle, use_container_width=True)

        # Redoublement (Repeat) Visualizations
        st.subheader("🔄 Redoublements")
        redoublement_mask = data_perf["situation"] != "1"

        if "genre" in data_perf.columns:
            redoublement_genre = data_perf[redoublement_mask].groupby("genre").size().reset_index(name="Redoublements")
            fig_redoublement_genre = create_bar_chart(redoublement_genre, "genre", "Redoublements", None, "Redoublements par Genre")
            st.plotly_chart(fig_redoublement_genre, use_container_width=True)
            fig_pie_redoublement_genre = px.pie(redoublement_genre, names="genre", values="Redoublements", title="Répartition des Redoublements par Genre")
            st.plotly_chart(fig_pie_redoublement_genre, use_container_width=True)

        if "etab" in data_perf.columns:
            redoublement_etab = data_perf[redoublement_mask].groupby("etab").size().reset_index(name="Redoublements")
            fig_redoublement_etab = create_bar_chart(redoublement_etab, "etab", "Redoublements", None, "Redoublements par Établissement")
            st.plotly_chart(fig_redoublement_etab, use_container_width=True)

        if "milieu" in data_perf.columns:
            redoublement_milieu = data_perf[redoublement_mask].groupby("milieu").size().reset_index(name="Redoublements")
            fig_redoublement_milieu = create_bar_chart(redoublement_milieu, "milieu", "Redoublements", None, "Redoublements par Milieu")
            st.plotly_chart(fig_redoublement_milieu, use_container_width=True)

        if "commune" in data_perf.columns:
            redoublement_commune = data_perf[redoublement_mask].groupby("commune").size().reset_index(name="Redoublements")
            fig_redoublement_commune = create_bar_chart(redoublement_commune, "commune", "Redoublements", None, "Redoublements par Commune")
            st.plotly_chart(fig_redoublement_commune, use_container_width=True)

        if "cycle" in data_perf.columns and "niveau" in data_perf.columns:
            redoublement_cycle = data_perf[redoublement_mask].groupby(["cycle", "niveau"]).size().reset_index(name="Redoublements")
            fig_redoublement_cycle = create_bar_chart(redoublement_cycle, "niveau", "Redoublements", "cycle", "Redoublements par Cycle et Niveau")
            st.plotly_chart(fig_redoublement_cycle, use_container_width=True)
            redoublement_cycle_dist = data_perf[redoublement_mask].groupby("cycle").size().reset_index(name="Redoublements")
            fig_pie_redoublement_cycle = px.pie(redoublement_cycle_dist, names="cycle", values="Redoublements", title="Répartition des Redoublements par Cycle")
            st.plotly_chart(fig_pie_redoublement_cycle, use_container_width=True)

        # Abandon (Dropout) Visualizations
        st.subheader("🚪 Abandons")
        dropout_mask = data_perf["situation"].isin(["2", "5"])

        if "genre" in data_perf.columns:
            dropout_genre = data_perf[dropout_mask].groupby("genre").size().reset_index(name="Abandons")
            fig_dropout_genre = create_bar_chart(dropout_genre, "genre", "Abandons", None, "Abandons par Genre")
            st.plotly_chart(fig_dropout_genre, use_container_width=True)
            fig_pie_dropout_genre = px.pie(dropout_genre, names="genre", values="Abandons", title="Répartition des Abandons par Genre")
            st.plotly_chart(fig_pie_dropout_genre, use_container_width=True)

        if "etab" in data_perf.columns:
            dropout_etab = data_perf[dropout_mask].groupby("etab").size().reset_index(name="Abandons")
            fig_dropout_etab = create_bar_chart(dropout_etab, "etab", "Abandons", None, "Abandons par Établissement")
            st.plotly_chart(fig_dropout_etab, use_container_width=True)

        if "milieu" in data_perf.columns:
            dropout_milieu = data_perf[dropout_mask].groupby("milieu").size().reset_index(name="Abandons")
            fig_dropout_milieu = create_bar_chart(dropout_milieu, "milieu", "Abandons", None, "Abandons par Milieu")
            st.plotly_chart(fig_dropout_milieu, use_container_width=True)

        if "commune" in data_perf.columns:
            dropout_commune = data_perf[dropout_mask].groupby("commune").size().reset_index(name="Abandons")
            fig_dropout_commune = create_bar_chart(dropout_commune, "commune", "Abandons", None, "Abandons par Commune")
            st.plotly_chart(fig_dropout_commune, use_container_width=True)

        if "cycle" in data_perf.columns and "niveau" in data_perf.columns:
            dropout_cycle = data_perf[dropout_mask].groupby(["cycle", "niveau"]).size().reset_index(name="Abandons")
            fig_dropout_cycle = create_bar_chart(dropout_cycle, "niveau", "Abandons", "cycle", "Abandons par Cycle et Niveau")
            st.plotly_chart(fig_dropout_cycle, use_container_width=True)
            dropout_cycle_dist = data_perf[dropout_mask].groupby("cycle").size().reset_index(name="Abandons")
            fig_pie_dropout_cycle = px.pie(dropout_cycle_dist, names="cycle", values="Abandons", title="Répartition des Abandons par Cycle")
            st.plotly_chart(fig_pie_dropout_cycle, use_container_width=True)

    # Cantines and Internats Visualizations
    if data_cant is not None and not data_cant.empty:
        st.subheader("🍽️ Visualisations - Cantines et Internats")
        
        # Combined cantines and internats by commune
        cantine_commune = data_cant[data_cant["cantine"] == True].groupby("commune").size().reset_index(name="Cantines")
        internat_commune = data_cant[data_cant["internat"] == True].groupby("commune").size().reset_index(name="Internats")
        combined_data = pd.merge(cantine_commune, internat_commune, on="commune", how="outer").fillna(0)
        
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Bar(
            x=combined_data["commune"], 
            y=combined_data["Cantines"], 
            name="Cantines", 
            text=combined_data["Cantines"].astype(int), 
            marker_color='#4CAF50'
        ))
        fig_combined.add_trace(go.Bar(
            x=combined_data["commune"], 
            y=combined_data["Internats"], 
            name="Internats", 
            text=combined_data["Internats"].astype(int), 
            marker_color='#2196F3'
        ))
        fig_combined.update_layout(
            title="Nombre de Cantines et Internats par Commune", 
            barmode="group", 
            yaxis_tickformat="d",
            xaxis_title="Commune",
            yaxis_title="Nombre",
            legend_title="Type"
        )
        fig_combined.update_traces(textposition="auto")
        st.plotly_chart(fig_combined, use_container_width=True)

        # Separate pie charts for cantines and internats
        col1, col2 = st.columns(2)
        
        with col1:
            total_cantines = data_cant[data_cant["cantine"] == True].shape[0]
            total_no_cantines = data_cant[data_cant["cantine"] == False].shape[0]
            cantine_pie_data = pd.DataFrame({
                'Status': ['Avec Cantine', 'Sans Cantine'],
                'Nombre': [total_cantines, total_no_cantines]
            })
            fig_cantine_pie = px.pie(cantine_pie_data, names="Status", values="Nombre", title="Répartition des Cantines")
            st.plotly_chart(fig_cantine_pie, use_container_width=True)

        with col2:
            total_internats = data_cant[data_cant["internat"] == True].shape[0]
            total_no_internats = data_cant[data_cant["internat"] == False].shape[0]
            internat_pie_data = pd.DataFrame({
                'Status': ['Avec Internat', 'Sans Internat'],
                'Nombre': [total_internats, total_no_internats]
            })
            fig_internat_pie = px.pie(internat_pie_data, names="Status", values="Nombre", title="Répartition des Internats")
            st.plotly_chart(fig_internat_pie, use_container_width=True)

    # Additional Ficher2 visualizations
    if data_ficher2 is not None and not data_ficher2.empty:
        
        # Amazigh establishments pie chart
        if 'amazigh_classes' in data_ficher2.columns:
            amazigh_etab_count = data_ficher2[data_ficher2['amazigh_classes'] > 0]['etab'].nunique()
            total_etab_count = data_ficher2['etab'].nunique()
            amazigh_data = pd.DataFrame({
                'Type': ['Enseignant l\'Amazigh', 'Non-Enseignant l\'Amazigh'],
                'Nombre': [amazigh_etab_count, total_etab_count - amazigh_etab_count]
            })
            fig_amazigh = create_pie_chart(amazigh_data, 'Type', 'Nombre', "Répartition des Établissements Enseignant l'Amazigh")
            st.plotly_chart(fig_amazigh, use_container_width=True)

        # Detailed class distribution by establishment and level
        if all(col in data_ficher2.columns for col in ['etab', 'niveau', 'total_classes']):
            class_data = data_ficher2.groupby(['etab', 'niveau'])['total_classes'].sum().reset_index()
            total_per_etab = class_data.groupby('etab')['total_classes'].sum()
            class_data['Pourcentage'] = class_data.apply(lambda row: (row['total_classes'] / total_per_etab[row['etab']] * 100), axis=1)
            
            fig_classes = px.bar(
                class_data,
                x='etab',
                y='total_classes',
                color='niveau',
                title="Nombre de Classes par Établissement et Niveau",
                text=class_data['Pourcentage'].apply(lambda x: f"{x:.1f}%"),
                height=800
            )
            fig_classes.update_layout(
                yaxis_title="Nombre de Classes",
                xaxis_title="Établissement",
                showlegend=True,
                xaxis={'tickangle': 45},
                margin=dict(b=150)
            )
            fig_classes.update_traces(textposition="auto")
            st.plotly_chart(fig_classes, use_container_width=True)

        # Class size distribution
        if all(col in data_ficher2.columns for col in ['under_24', '24_35', '36_40', '41_45', '46_50', 'over_51']):
            size_categories = ['< 24', '24-35', '36-40', '41-45', '46-50', '> 51']
            size_counts = [
                data_ficher2['under_24'].sum(),
                data_ficher2['24_35'].sum(),
                data_ficher2['36_40'].sum(),
                data_ficher2['41_45'].sum(),
                data_ficher2['46_50'].sum(),
                data_ficher2['over_51'].sum()
            ]
            
            size_distribution = pd.DataFrame({
                'Taille_Classe': size_categories,
                'Nombre_Classes': size_counts
            })
            
            fig_size_dist = px.bar(
                size_distribution, 
                x='Taille_Classe', 
                y='Nombre_Classes',
                title="Distribution des Classes par Taille",
                text='Nombre_Classes'
            )
            fig_size_dist.update_traces(textposition="auto")
            fig_size_dist.update_layout(
                xaxis_title="Taille de Classe (Nombre d'Élèves)",
                yaxis_title="Nombre de Classes"
            )
            st.plotly_chart(fig_size_dist, use_container_width=True)

    # Message if no data is available
    if data_ficher2 is None and data_perf is None and data_cant is None:
        st.info("🔍 Veuillez importer vos données pour commencer l'analyse et voir les visualisations.")
        st.markdown("""
        **Instructions d'utilisation :**
        1. Utilisez la barre latérale pour importer vos fichiers de données
        2. Appliquez les filtres souhaités pour affiner votre analyse
        3. Explorez les différentes visualisations générées automatiquement
        4. Exportez vos résultats filtrés au format CSV si nécessaire
        """)

    # Footer
    st.markdown("---")
    st.markdown("*Dashboard développé pour le suivi des indicateurs de performance éducative - Direction Provinciale Belghiti*")

if __name__ == "__main__":
    show_page()