import streamlit as st
import json
import os
from utils import authenticate_user, register_user, add_login_page_css

def add_custom_css():
    """
    Add custom CSS for the login page with animated particles background
    """
    st.markdown(
        """
        <style>
        /* Main app background with animated particles - matching main.py */
        .stApp {
            background: linear-gradient(135deg, 
                #0f0f23 0%, 
                #1a1a3e 25%, 
                #2d2d5f 50%, 
                #1a1a3e 75%, 
                #0f0f23 100%);
            background-attachment: fixed;
        }
        
        /* Create animated particles - matching main.py */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.25) 0%, transparent 50%),
                radial-gradient(circle at 70% 70%, rgba(255, 200, 87, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 30% 60%, rgba(134, 255, 119, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(188, 119, 255, 0.15) 0%, transparent 50%);
            animation: floatParticles 20s ease-in-out infinite;
        }
        
        /* Add floating animation keyframes */
        @keyframes floatParticles {
            0%, 100% {
                transform: translateY(0px) rotate(0deg);
                opacity: 1;
            }
            25% {
                transform: translateY(-20px) rotate(90deg);
                opacity: 0.8;
            }
            50% {
                transform: translateY(-40px) rotate(180deg);
                opacity: 0.6;
            }
            75% {
                transform: translateY(-20px) rotate(270deg);
                opacity: 0.8;
            }
        }
        
        /* Login Card Styling with Glass Effect */
        div[data-testid="stForm"] {
            background-color: rgba(0, 0, 0, 0.75) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 12px !important;
            padding: 30px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            margin-bottom: 20px !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stForm"]:hover {
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Form Input Fields */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stTextInput"] textarea {
            background-color: rgba(255, 255, 255, 0.07) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 6px !important;
            color: white !important;
            padding: 12px !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stTextInput"] input:focus, 
        div[data-testid="stTextInput"] textarea:focus {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Label Text */
        div[data-testid="stTextInput"] label {
            color: #E5E7EB !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
        }
        
        /* Form Submit Button */
        div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
            background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            height: 48px !important;
            text-transform: uppercase !important;
            font-size: 0.9rem !important;
        }
        
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:active {
            transform: translateY(1px) !important;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4) !important;
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0 !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
            backdrop-filter: blur(8px) !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 5px 5px 0 5px !important;
            border-bottom: none !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            color: #E5E7EB !important;
            background-color: rgba(0, 0, 0, 0.2) !important;
            margin-right: 4px !important;
            transition: all 0.2s ease !important;
            border: none !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: rgba(0, 0, 0, 0.75) !important;
            color: white !important;
            border-bottom: 3px solid #3B82F6 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(0, 0, 0, 0.4) !important;
            color: white !important;
        }
        
        /* Header styling */
        h1, h2, h3 {
            color: white !important;
            font-weight: 600 !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8) !important;
        }
        
        h1 {
            font-family: 'Poppins', sans-serif !important;
            letter-spacing: 1px !important;
            text-align: center !important;
        }
        
        .stSubheader {
            font-size: 1.3rem !important;
            margin-bottom: 20px !important;
            text-align: center !important;
            color: #E5E7EB !important;
        }
        
        /* Success and Error Messages */
        .stSuccess, .stError {
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-weight: 500 !important;
            margin: 10px 0 !important;
        }
        
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.2) !important;
            border-left: 4px solid #10B981 !important;
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.2) !important;
            border-left: 4px solid #EF4444 !important;
        }
        
        /* Hide default Streamlit sidebar */
        section[data-testid="stSidebar"] {
            display: none;
        }
        
        /* Remove default Streamlit footer */
        footer.css-1lsmgbg,
        footer.css-12ttj6m {
            display: none !important;
        }
        
        /* Responsiveness */
        @media (max-width: 768px) {
            div[data-testid="stForm"] {
                padding: 20px !important;
            }
            
            h1 {
                font-size: 1.8rem !important;
            }
            
            .stSubheader {
                font-size: 1.1rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_login_page():
    # Add custom CSS for the login page
    add_custom_css()
    # Also use the imported CSS function if needed
    add_login_page_css()
    
    # App header with styled title
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">Analyse de Données</h1>
        <p style="color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">Application professionnelle d'analyse et préparation des données</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create 3-column layout with content in the middle
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create tabs for login and sign up
        tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Veuillez vous connecter")
                username = st.text_input("Nom d'utilisateur")
                password = st.text_input("Mot de passe", type="password")
                
                # Add a checkbox for "remember me"
                remember_me = st.checkbox("Se souvenir de moi")
                
                submitted = st.form_submit_button("Se connecter")
                
                if submitted:
                    if not username or not password:
                        st.error("Veuillez saisir votre nom d'utilisateur et mot de passe.")
                    elif authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("Connexion réussie!")
                        # Use javascript to reload the page without showing "rerun" message
                        st.markdown(
                            """
                            <script>
                                setTimeout(function() {
                                    window.location.reload();
                                }, 1000);
                            </script>
                            """,
                            unsafe_allow_html=True
                        )
                        st.rerun()
                    else:
                        st.error("Nom d'utilisateur ou mot de passe invalide")
        
        with tab2:
            with st.form("signup_form"):
                st.subheader("Créer un nouveau compte")
                new_username = st.text_input("Choisir un nom d'utilisateur")
                new_password = st.text_input("Choisir un mot de passe", type="password")
                confirm_password = st.text_input("Confirmer le mot de passe", type="password")
                email = st.text_input("Email (optionnel)")
                submitted_signup = st.form_submit_button("S'inscrire")
                
                if submitted_signup:
                    if not new_username or not new_password:
                        st.error("Veuillez remplir tous les champs obligatoires")
                    elif new_password != confirm_password:
                        st.error("Les mots de passe ne correspondent pas")
                    else:
                        result = register_user(new_username, new_password, email)
                        if result == "success":
                            st.success("Compte créé avec succès! Vous pouvez maintenant vous connecter.")
                            # Switch to login tab
                            st.markdown(
                                """
                                <script>
                                    setTimeout(function() {
                                        document.querySelector('[data-baseweb="tab"] div').click();
                                    }, 1500);
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                        elif result == "exists":
                            st.error("Ce nom d'utilisateur existe déjà. Veuillez en choisir un autre.")
                        else:
                            st.error("Une erreur s'est produite lors de la création du compte.")
        
        # Add a footer
        st.markdown("""
        <div style="text-align: center; margin-top: 20px; color: white; text-shadow: 1px 1px 2px black;">
            <p>© 2025 Analyse de Données | Tous droits réservés</p>
        </div>
        """, unsafe_allow_html=True)