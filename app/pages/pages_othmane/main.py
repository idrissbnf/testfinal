import streamlit as st
import pandas as pd
from io import BytesIO
from .overview import create_overview_tab
from .establishments import create_establishments_tab
from .students import create_students_tab
from .provincial import create_provincial_tab
from .custom import create_custom_viz_tab

def show_page():
    st.markdown("---")
    st.title("🏫 Analyse des Établissements Scolaires - Marrakech-Asafi")
    st.markdown("---")

    # Initialize navigation state if not exists
    if 'analysis_page' not in st.session_state:
        st.session_state['analysis_page'] = "Vue d'ensemble"

    @st.cache_data
    def load_and_process_data(uploaded_file):
        """Charge et traite les données Excel avec optimisations de performance"""
        
        # Optimized Excel reading with specific parameters
        try:
            # Read only required columns to speed up loading
            required_columns = ['NOM_ETABL', 'cd_com', 'CD_MIL', 'LL_MIL', 'll_com', 
                               'nefstat', 'id_eleve', 'id_classe', 'typeEtab', 'libformatFr', 'LL_CYCLE']
            
            # Try to read with openpyxl engine for better performance
            df = pd.read_excel(
                uploaded_file,
                engine='openpyxl',  # Usually faster for .xlsx files
                usecols=required_columns,  # Only read required columns
                dtype={
                    'NOM_ETABL': 'string',
                    'cd_com': 'string', 
                    'CD_MIL': 'string',
                    'LL_MIL': 'string',
                    'll_com': 'string',
                    'nefstat': 'string',
                    'id_eleve': 'string',
                    'id_classe': 'string',
                    'typeEtab': 'string',
                    'libformatFr': 'string',
                    'LL_CYCLE': 'string'
                }
            )
        except:
            # Fallback to default reading if optimized version fails
            df = pd.read_excel(uploaded_file)
            
            # Vérification des colonnes requises
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.error(f"Colonnes manquantes: {missing_columns}")
                st.stop()
        
        # Optimized filtering - vectorized operations
        marrakech_asafi_keywords = ['marrakech', 'asafi', 'safi', 'marrakesh']
        
        # Convert to lowercase once and use vectorized operations
        ll_com_lower = df['ll_com'].str.lower()
        marrakech_asafi_mask = ll_com_lower.str.contains('|'.join(marrakech_asafi_keywords), na=False, regex=True)
        
        if marrakech_asafi_mask.any():
            df_filtered = df[marrakech_asafi_mask].copy()
        else:
            df_filtered = df.copy()
        
        # Optimized data cleaning - vectorized fillna
        fill_columns = ['LL_MIL', 'LL_CYCLE', 'libformatFr', 'NOM_ETABL', 'typeEtab', 'nefstat']
        df_filtered[fill_columns] = df_filtered[fill_columns].fillna('Non spécifié')
        
        return df_filtered

    def create_sidebar_config(df):
        """Crée la configuration complète de la sidebar avec navigation en haut et filtres en bas"""
        
        
        # SECTION 1: NAVIGATION (EN HAUT)
        st.sidebar.markdown("---")
        st.sidebar.markdown("<h3 style='color: #1e3a8a;'>🚀 Navigation</h3>", unsafe_allow_html=True)
        
        # Navigation buttons
        if st.sidebar.button("📊 Vue d'ensemble", use_container_width=True):
            st.session_state['analysis_page'] = "Vue d'ensemble"
            st.rerun()
            
        if st.sidebar.button("🏫 Analyse Établissements", use_container_width=True):
            st.session_state['analysis_page'] = "Analyse Établissements"
            st.rerun()
            
        if st.sidebar.button("👥 Analyse Élèves", use_container_width=True):
            st.session_state['analysis_page'] = "Analyse Élèves"
            st.rerun()
            
        if st.sidebar.button("📍 Analyse Provinciale", use_container_width=True):
            st.session_state['analysis_page'] = "Analyse Provinciale"
            st.rerun()
            
        if st.sidebar.button("📈 Visualisations Personnalisées", use_container_width=True):
            st.session_state['analysis_page'] = "Visualisations Personnalisées"
            st.rerun()
        
        # Display current page
        st.sidebar.markdown(f"**Page actuelle:** {st.session_state['analysis_page']}")
        
        # SECTION 2: FILTRES (EN BAS)
        st.sidebar.markdown("---")
        st.sidebar.markdown("<h3 style='color: #1e3a8a;'>🔍 Filtres Hiérarchiques</h3>", unsafe_allow_html=True)
        
        # Filtres hiérarchiques
        filters = {}
        
        # Milieu
        milieux = ['Tous'] + sorted(df['LL_MIL'].unique().tolist())
        filters['milieu'] = st.sidebar.selectbox("🌆 Milieu", milieux)
        if filters['milieu'] != 'Tous':
            df = df[df['LL_MIL'] == filters['milieu']]
        
        # Commune
        communes = ['Toutes'] + sorted(df['ll_com'].unique().tolist())
        filters['commune'] = st.sidebar.selectbox("🏘️ Commune", communes)
        if filters['commune'] != 'Toutes':
            df = df[df['ll_com'] == filters['commune']]
        
        # Établissement
        etablissements = ['Tous'] + sorted(df['NOM_ETABL'].unique().tolist())
        filters['etablissement'] = st.sidebar.selectbox("🏫 Établissement", etablissements)
        if filters['etablissement'] != 'Tous':
            df = df[df['NOM_ETABL'] == filters['etablissement']]
        
        # Type d'établissement
        types_etab = ['Tous'] + sorted(df['typeEtab'].unique().tolist())
        filters['type_etab'] = st.sidebar.selectbox("🏛️ Type d'établissement", types_etab)
        if filters['type_etab'] != 'Tous':
            df = df[df['typeEtab'] == filters['type_etab']]
        
        # Cycle
        cycles = ['Tous'] + sorted(df['LL_CYCLE'].unique().tolist())
        filters['cycle'] = st.sidebar.selectbox("🎓 Cycle", cycles)
        if filters['cycle'] != 'Tous':
            df = df[df['LL_CYCLE'] == filters['cycle']]
        
        # Niveau
        niveaux = ['Tous'] + sorted(df['libformatFr'].unique().tolist())
        filters['niveau'] = st.sidebar.selectbox("📚 Niveau", niveaux)
        if filters['niveau'] != 'Tous':
            df = df[df['libformatFr'] == filters['niveau']]
        
        return df

    # Main Application - File Upload in Main Content Area
    st.subheader("📁 Importation des Données")
    st.markdown("Téléchargez votre fichier Excel contenant les données des établissements scolaires.")
    st.markdown("")  # Add some spacing
    
    # Full width file uploader - no columns to make it large
    uploaded_file = st.file_uploader(
        "Choisir le fichier Excel", 
        type=['xlsx', 'xls'],
        help="Téléchargez votre fichier de données Excel contenant les informations des établissements scolaires de Marrakech-Asafi"
    )

    if uploaded_file is not None:
        try:
            # Show file info before processing
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB
            st.info(f"📁 Fichier: {uploaded_file.name} ({file_size:.1f} MB)")
            
            # Progress bar for better UX
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Chargement et traitement des données
            status_text.text("📖 Lecture du fichier Excel...")
            progress_bar.progress(25)
            
            df = load_and_process_data(uploaded_file)
            
            progress_bar.progress(75)
            status_text.text("✅ Traitement des données terminé")
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Affichage des infos de base
            st.success("✅ Fichier chargé avec succès!")
            
            # Display basic statistics in main area
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Lignes de données", f"{len(df):,}")
            with col2:
                st.metric("🏫 Établissements", f"{df['NOM_ETABL'].nunique():,}")
            with col3:
                st.metric("👥 Élèves", f"{df['id_eleve'].nunique():,}")
            
            st.markdown("---")
            
            # Application des filtres et création de la sidebar complète
            df_filtered = create_sidebar_config(df)
            
            # Navigation vers les différentes pages basée sur l'état de session
            if st.session_state['analysis_page'] == "Vue d'ensemble":
                create_overview_tab(df_filtered)
            elif st.session_state['analysis_page'] == "Analyse Établissements":
                create_establishments_tab(df_filtered)
            elif st.session_state['analysis_page'] == "Analyse Élèves":
                create_students_tab(df_filtered)
            elif st.session_state['analysis_page'] == "Analyse Provinciale":
                create_provincial_tab(df_filtered)
            elif st.session_state['analysis_page'] == "Visualisations Personnalisées":
                create_custom_viz_tab(df_filtered)
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier: {str(e)}")
            st.info("💡 **Conseils pour optimiser les performances:**")
            st.markdown("""
            - Assurez-vous que le fichier ne dépasse pas 200MB
            - Vérifiez que toutes les colonnes requises sont présentes
            - Essayez de fermer d'autres applications pour libérer de la mémoire
            """)
            
            with st.expander("🔍 Détails de l'erreur"):
                import traceback
                st.text(traceback.format_exc())

    else:
        # Show instructions when no file is uploaded
        st.info("👆 Veuillez télécharger votre fichier Excel pour commencer l'analyse.")