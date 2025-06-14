import streamlit as st
import pandas as pd
import numpy as np
import os

# Dictionnaire des services (ID -> Nom)
SERVICES = {
    1: "Internat",
    2: "Programme Tayssir",
    3: "Fournitures scolaires",
    4: "Transport scolaire",
    5: "Restauration",
    6: "Uniforme scolaire",
    7: "Un million de cartables",
    8: "Appui psychologique social",
    9: "cycles de réhabilitation",
    10: "Cours d'appui",
}

# Récupérer le nom d'un service à partir de son ID
def get_service_name(service_id):
    return SERVICES.get(service_id, f"Service {service_id}")

# Fonction pour l'importation de fichiers
def import_files():
    st.markdown('<h2 style="text-align: center;">Importation des Fichiers de Données</h2>', unsafe_allow_html=True)
    
    with st.expander("Instructions d'importation", expanded=True):
        st.markdown("""
        1. Vous devez importer deux fichiers CSV:
           - Un fichier pour les établissements publics
           - Un fichier pour les établissements privés
        2. Les fichiers doivent avoir les colonnes nécessaires (Id_TypeService, GenreFr, LL_MIL, etc.)
        3. Le séparateur attendu est le point-virgule (;)
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Fichier des établissements publics")
        uploaded_file_public = st.file_uploader("Importer les données des établissements publics", type="csv", key="public")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Fichier des établissements privés")
        uploaded_file_private = st.file_uploader("Importer les données des établissements privés", type="csv", key="private")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialiser les messages d'état
    status_public = ""
    status_private = ""
    
    # Traiter le fichier public
    if uploaded_file_public is not None:
        try:
            df_public = pd.read_csv(uploaded_file_public, sep=";", encoding='utf-8')
            # Vérifier que les colonnes nécessaires sont présentes
            required_cols = ["Id_TypeService", "resultatFr", "GenreFr", "SituationFr", "LL_MIL"]
            missing_cols = [col for col in required_cols if col not in df_public.columns]
            
            if missing_cols:
                status_public = f"❌ Erreur: Colonnes manquantes: {', '.join(missing_cols)}"
            else:
                # Sauvegarder le fichier
                df_public.to_csv("tous_public.csv", sep=";", index=False, encoding='utf-8')
                status_public = "✅ Fichier public importé avec succès!"
                st.session_state['public_imported'] = True
        except Exception as e:
            status_public = f"❌ Erreur lors de l'importation: {str(e)}"
    
    # Traiter le fichier privé
    if uploaded_file_private is not None:
        try:
            df_private = pd.read_csv(uploaded_file_private, sep=";", encoding='utf-8')
            # Vérifier que les colonnes nécessaires sont présentes
            required_cols = ["Id_TypeService", "resultatFr", "GenreFr", "SituationFr", "LL_MIL"]
            missing_cols = [col for col in required_cols if col not in df_private.columns]
            
            if missing_cols:
                status_private = f"❌ Erreur: Colonnes manquantes: {', '.join(missing_cols)}"
            else:
                # Sauvegarder le fichier
                df_private.to_csv("tous_privé.csv", sep=";", index=False, encoding='utf-8')
                status_private = "✅ Fichier privé importé avec succès!"
                st.session_state['private_imported'] = True
        except Exception as e:
            status_private = f"❌ Erreur lors de l'importation: {str(e)}"
    
    # Afficher les statuts
    if status_public:
        st.write(status_public)
    if status_private:
        st.write(status_private)
    
    # Bouton pour continuer si les deux fichiers sont importés
    if st.session_state.get('public_imported', False) and st.session_state.get('private_imported', False):
        if st.button("Continuer vers l'analyse"):
            st.session_state['files_imported'] = True
            st.rerun()
    
    # Option pour utiliser des données de démonstration
    st.markdown("---")
    if st.button("Utiliser des données de démonstration"):
        st.session_state['files_imported'] = True
        st.session_state['using_demo_data'] = True
        st.rerun()

# Fonction de chargement des données de service
@st.cache_data
def load_service_data():
    try:
        # Si nous utilisons des données de démonstration ou si les fichiers ont été importés
        if st.session_state.get('using_demo_data', False) or (os.path.exists("tous_public.csv") and os.path.exists("tous_privé.csv")):
            # Chargement des données CSV des services
            service_public = pd.read_csv("tous_public.csv", sep=";", encoding='utf-8')
            service_prive = pd.read_csv("tous_privé.csv", sep=";", encoding='utf-8')
            
            # Ajout d'un identifiant du type d'établissement
            service_public["Type"] = "Public"
            service_prive["Type"] = "Privé"
            
            # Combinaison des deux datasets
            combined_service = pd.concat([service_public, service_prive], ignore_index=True)
            
            # Création d'une colonne pour le taux de réussite
            combined_service['Taux_Reussite'] = combined_service['resultatFr'].apply(
                lambda x: 1 if x == 'Admis' else 0 if x == 'Non Admis' else np.nan
            )
            # Extraction des services lorsqu'ils existent
            def parse_services(service_str):
                if pd.isna(service_str) or service_str == '':
                    return []
                try:
                    return [int(s.strip()) for s in str(service_str).split(',')]
                except:
                    return []
                    
            combined_service['Services'] = combined_service['Id_TypeService'].apply(parse_services)
            
            # Ajouter les noms des services
            combined_service['Noms_Services'] = combined_service['Services'].apply(
                lambda services: [get_service_name(s) for s in services] if isinstance(services, list) else []
            )
            
            # Ajouter le nombre de services par élève
            combined_service['Nb_Services'] = combined_service['Services'].apply(len)
            
            return combined_service
        else:
            return pd.DataFrame()  # Retourner un DataFrame vide si les fichiers n'existent pas
    except Exception as e:
        st.error(f"Erreur lors du chargement des données de service: {e}")
        return pd.DataFrame()
    