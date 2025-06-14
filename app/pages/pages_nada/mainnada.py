import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Import des modules de pages
from .accueil import show_accueil
from .donnees_brutes import show_donnees_brutes
from .statistiques import show_statistiques
from .visualisations import show_visualisations

from .utils import load_service_data, import_files

# CSS personnalisé
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.8em;
        margin-top: 30px;
    }
    .stSelectbox, .stTextInput {
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

def show_page():
    """Main function to show the page - renamed from main_app for consistency"""
    # Initialisation manuelle de l'état de session
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = True
 
    
    # Initialize navigation state if not exists
    if 'nada_page' not in st.session_state:
        st.session_state['nada_page'] = "Accueil"

    # Vérifie si les fichiers sont importés
    if 'files_imported' not in st.session_state or not st.session_state['files_imported']:
        import_files()
        return

    # Chargement des données
    service_data = load_service_data()
    
    if service_data.empty:
        st.error("Impossible de charger les données. Veuillez importer les fichiers à nouveau.")
        # Réinitialiser l'état d'importation
        st.session_state['files_imported'] = False
        st.rerun()
        return
    
    # Afficher l'en-tête avec informations utilisateur
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("Système d'Analyse Intelligente des Données Scolaires")
  
    
    # Sidebar - Navigation en haut, puis filtres
    with st.sidebar:
        # Navigation section (moved to top)
        st.markdown("<h3 style='color: #1e3a8a;'>🚀 Navigation</h3>", unsafe_allow_html=True)
        
        # Navigation buttons
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state['nada_page'] = "Accueil"
            st.rerun()
            
        if st.button("📋 Données Brutes", use_container_width=True):
            st.session_state['nada_page'] = "Données Brutes"
            st.rerun()
            
        if st.button("📊 Statistiques", use_container_width=True):
            st.session_state['nada_page'] = "Statistiques"
            st.rerun()
            
        if st.button("📈 Visualisations", use_container_width=True):
            st.session_state['nada_page'] = "Visualisations"
            st.rerun()
        
        # Display current page
        st.markdown(f"**Page actuelle:** {st.session_state['nada_page']}")
        
        st.markdown("---")
        
        # Filtres universels (moved below navigation)
        st.markdown("<h3 style='color:#1e3a8a;'>🔧 Filtres Universels</h3>", unsafe_allow_html=True)
        
        filtered_data = service_data.copy()
        
        # Filtres avec design amélioré
        type_ecole = st.selectbox("Type d'établissement", ["Tous", "Privé", "Public"])
        genre = st.selectbox("Genre", ["Tous", "Fille", "Garçon"])
        lieu = st.selectbox("Localisation", ["Tous", "Urbain", "Rural"])
        
        # Filtrage des données de service
        if type_ecole != "Tous":
            filtered_data = filtered_data[filtered_data["Type"] == type_ecole]
        if genre != "Tous":
            filtered_data = filtered_data[filtered_data["GenreFr"] == genre]
        if lieu != "Tous":
            filtered_data = filtered_data[filtered_data["LL_MIL"] == lieu]
        
        # Bouton de déconnexion (optionnel, à la fin)
        
       
    
    # Navigation vers les différentes pages
    if st.session_state['nada_page'] == "Accueil":
        show_accueil(filtered_data)
    elif st.session_state['nada_page'] == "Données Brutes":
        show_donnees_brutes(filtered_data)
    elif st.session_state['nada_page'] == "Statistiques":
        show_statistiques(filtered_data)
    elif st.session_state['nada_page'] == "Visualisations":
        show_visualisations(filtered_data)

def main_app():
    """Legacy function name - calls show_page for backward compatibility"""
    show_page()

# Only call main_app() if this file is run directly, not when imported
if __name__ == "__main__":
    main_app()