import streamlit as st
import pandas as pd

def show_donnees_brutes(filtered_data):
    st.subheader("📋 Données Brutes Complètes")
    
    # Vérifier que les données ne sont pas vides
    if filtered_data is None or filtered_data.empty:
        st.warning("Aucune donnée disponible à afficher")
        return
    
    # Vérifier que la colonne 'Type' existe
    if 'Type' not in filtered_data.columns:
        st.error("La colonne 'Type' n'existe pas dans les données")
        return
    
    # Interface avec boutons au lieu d'onglets
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        btn_prive = st.button("🏢 Établissements Privés", key="btn_prive", use_container_width=True)
    
    with col2:
        btn_public = st.button("🏛️ Établissements Publics", key="btn_public", use_container_width=True)
    
    # Initialiser le state si nécessaire
    if 'selected_type' not in st.session_state:
        st.session_state.selected_type = 'Privé'  # Par défaut
    
    # Gestion des clics de boutons
    if btn_prive:
        st.session_state.selected_type = 'Privé'
    elif btn_public:
        st.session_state.selected_type = 'Public'
    
    # Séparation des données selon le type sélectionné
    try:
        if st.session_state.selected_type == 'Privé':
            selected_data = filtered_data[filtered_data["Type"] == "Privé"].copy()
            section_title = "Services - Établissements Privés"
            download_filename = "services_prive.csv"
            search_key = "search_current_private"
            items_key = "items_current_private"
            page_key = "page_current_private"
            download_key = "download_current_private"
        else:
            selected_data = filtered_data[filtered_data["Type"] == "Public"].copy()
            section_title = "Services - Établissements Publics"
            download_filename = "services_public.csv"
            search_key = "search_current_public"
            items_key = "items_current_public"
            page_key = "page_current_public"
            download_key = "download_current_public"
        
        # Supprimer la colonne Type pour l'affichage
        if not selected_data.empty and "Type" in selected_data.columns:
            selected_data = selected_data.drop(columns=["Type"])
            
    except Exception as e:
        st.error(f"Erreur lors du filtrage des données: {e}")
        return
    
    # Affichage du bouton actif
    st.markdown(f"### 📊 {section_title}")
    st.markdown(f"**Type sélectionné:** {st.session_state.selected_type}")
    
    if not selected_data.empty:
        # Définir les colonnes à afficher
        colonnes_disponibles = selected_data.columns.tolist()
        colonnes_à_supprimer = ['Services', 'Noms_Services']
        colonnes_display = [col for col in colonnes_disponibles if col not in colonnes_à_supprimer]
        
        # Ajouter une recherche
        search_term = st.text_input(f"🔍 Rechercher dans les données {st.session_state.selected_type.lower()}s", key=search_key)
        
        # Filtrer les données selon la recherche
        if search_term:
            try:
                filtered_data_display = selected_data[
                    selected_data.astype(str).apply(
                        lambda row: row.str.contains(search_term, case=False, na=False).any(), axis=1
                    )
                ]
            except Exception as e:
                st.error(f"Erreur lors de la recherche: {e}")
                filtered_data_display = selected_data
        else:
            filtered_data_display = selected_data
        
        # Pagination
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            items_per_page = st.selectbox("Lignes par page", [10, 20, 50, 100], key=items_key)
        
        with col2:
            total_pages = max(1, (len(filtered_data_display) + items_per_page - 1) // items_per_page)
            page_num = st.number_input("Page", 1, total_pages, 1, key=page_key)
        
        with col3:
            st.metric("Total entrées", len(filtered_data_display))
        
        # Calcul des indices
        start_idx = (page_num - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_data_display))
        
        # Affichage du tableau
        if len(filtered_data_display) > 0:
            display_data = filtered_data_display[colonnes_display].iloc[start_idx:end_idx]
            st.dataframe(
                display_data,
                height=400,
                use_container_width=True
            )
            
            st.info(f"Affichage de {start_idx + 1} à {end_idx} sur {len(filtered_data_display)} entrées")
            
            # Bouton de téléchargement
            csv_data = filtered_data_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📥 Télécharger les données {st.session_state.selected_type.lower()}s (CSV)",
                data=csv_data,
                file_name=download_filename,
                mime="text/csv",
                key=download_key
            )
        else:
            st.warning("Aucun résultat trouvé pour votre recherche")
            
    else:
        st.warning(f"Aucune donnée de service {st.session_state.selected_type.lower()} disponible")