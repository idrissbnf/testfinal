import base64
import json
import os
from datetime import datetime
import streamlit as st

# Define the path for the users database
USERS_DB_PATH = "users.json"

def get_users():
    """Load the users database from JSON file"""
    if os.path.exists(USERS_DB_PATH):
        try:
            with open(USERS_DB_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    else:
        return {}

def save_users(users):
    """Save the users database to JSON file"""
    with open(USERS_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    Checks against the JSON file.
    """
    users = get_users()
    return username in users and users[username]["password"] == password

def register_user(username, password, email=""):
    """
    Register a new user.
    Returns:
    - "success" if registration successful
    - "exists" if username already exists
    - "error" on other errors
    """
    try:
        users = get_users()
        
        # Check if username already exists
        if username in users:
            return "exists"
        
        # Add new user
        users[username] = {
            "password": password,
            "email": email,
            "created_at": str(datetime.now())
        }
        
        # Save updated users database
        save_users(users)
        return "success"
    except Exception as e:
        print(f"Error registering user: {e}")
        return "error"

def check_authentication():
    """
    Check if the user is authenticated.
    """
    return "authenticated" in st.session_state and st.session_state.authenticated

# Initialize theme settings
def initialize_theme():
    """Initialize theme settings in session state"""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"  # Default to dark mode

# Function to toggle theme
def toggle_theme():
    """Toggle between dark and light mode"""
    if st.session_state.theme_mode == "dark":
        st.session_state.theme_mode = "light"
    else:
        st.session_state.theme_mode = "dark"

# Function to add background image
def add_bg_from_file(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    # CSS to set the background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def add_login_page_css():
    st.markdown("""
    <style>
        /* Hide sidebar ONLY for login page */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Hide default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
    </style>
    """, unsafe_allow_html=True)

def remove_sidebar_hiding():
    st.markdown("""
    <style>
        /* Remove the hiding of sidebar */
        [data-testid="stSidebar"] {
            display: block !important;
        }
    </style>
    """, unsafe_allow_html=True)

def add_custom_css():
    """Add custom CSS with theme support"""
    # Initialize theme if not already done
    initialize_theme()
    
    # Get current theme
    theme = st.session_state.get("theme_mode", "dark")
    
    # Define theme colors
    if theme == "dark":
        theme_colors = {
            "bg_primary": "#0f0f23",
            "bg_secondary": "#1a1a3e", 
            "bg_tertiary": "#2d2d5f",
            "navbar_bg": "#000000",
            "sidebar_bg": "rgba(0,0,0,0.8)",
            "text_primary": "#ffffff",
            "text_secondary": "#e5e7eb",
            "border_color": "rgba(255,255,255,0.1)",
            "hover_bg": "rgba(255,255,255,0.1)",
            "button_gradient": "linear-gradient(45deg, #2b5876, #4e4376)",
            "button_hover": "linear-gradient(45deg, #3a7bd5, #5d46a3)"
        }
    else:  # light mode
        theme_colors = {
            "bg_primary": "#f8fafc",
            "bg_secondary": "#e2e8f0",
            "bg_tertiary": "#cbd5e1",
            "navbar_bg": "#ffffff",
            "sidebar_bg": "rgba(255,255,255,0.95)",
            "text_primary": "#1f2937",
            "text_secondary": "#4b5563",
            "border_color": "rgba(0,0,0,0.1)",
            "hover_bg": "rgba(0,0,0,0.05)",
            "button_gradient": "linear-gradient(45deg, #3b82f6, #1e40af)",
            "button_hover": "linear-gradient(45deg, #2563eb, #1d4ed8)"
        }
    
    st.markdown(f"""
    <style>
/* Hide default navbar and elements */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Theme-based main background */
.stApp {{
    background: linear-gradient(135deg, 
        {theme_colors["bg_primary"]} 0%, 
        {theme_colors["bg_secondary"]} 25%, 
        {theme_colors["bg_tertiary"]} 50%, 
        {theme_colors["bg_secondary"]} 75%, 
        {theme_colors["bg_primary"]} 100%) !important;
    background-attachment: fixed !important;
    color: {theme_colors["text_primary"]} !important;
}}

/* Hide the default sidebar navigation titles */
[data-testid="stSidebarNavTitle"] {{display: none !important;}}
[data-testid="stSidebarNavItems"] {{display: none !important;}}
[data-baseweb="tab-list"] {{display: none !important;}}

/* Custom navbar styles - full width and fixed at top */
.custom-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 25px;
    background-color: {theme_colors["navbar_bg"]};
    color: {theme_colors["text_primary"]};
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    width: 100%;
    height: auto;
    min-height: 60px;
    border-bottom: 1px solid {theme_colors["border_color"]};
}}

/* Change sidebar background color */
[data-testid="stSidebar"] {{
    background-color: {theme_colors["sidebar_bg"]} !important;
    color: {theme_colors["text_primary"]} !important;
    margin-top: 60px;
    padding-top: 10px;
    z-index: 999;
    border-right: 1px solid {theme_colors["border_color"]};
}}

/* Make sidebar text match theme */
[data-testid="stSidebar"] .st-bq {{
    color: {theme_colors["text_primary"]} !important;
}}

[data-testid="stSidebar"] .st-cj {{
    color: {theme_colors["text_primary"]} !important;
}}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    color: {theme_colors["text_primary"]} !important;
}}

/* Navigation styles */
.custom-navigation {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px 15px;
    background-color: {theme_colors["navbar_bg"]};
    color: {theme_colors["text_primary"]};
    margin: 10px 0;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

.nav-item {{
    padding: 8px 15px;
    margin: 0 5px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}}

.nav-item:hover {{
    background-color: {theme_colors["hover_bg"]};
}}

.nav-item.active {{
    background-color: {theme_colors["hover_bg"]};
    font-weight: bold;
}}

/* Add padding to the top of content to account for fixed navbar */
.main-content {{
    padding-top: 80px;
}}

/* Style form buttons in main app */
div.stButton button {{
    background: {theme_colors["button_gradient"]};
    color: {theme_colors["text_primary"]} !important;
    font-weight: bold;
    border: none;
    padding: 12px 15px;
    width: 100%;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin: 10px 0;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}}

div.stButton button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    background: {theme_colors["button_hover"]};
}}

.social-icons {{
    display: flex;
    gap: 10px;
    align-items: center;
}}

.social-icon {{
    font-size: 20px;
    color: {theme_colors["text_primary"]};
    padding: 5px;
    border-radius: 5px;
    transition: all 0.3s ease;
    cursor: pointer;
}}

.social-icon:hover {{
    transform: translateY(-2px);
    background-color: {theme_colors["hover_bg"]};
}}

/* Sidebar button styling */
.css-1d391kg .stButton button,
section[data-testid="stSidebar"] .stButton button {{
    background-color: {theme_colors["hover_bg"]} !important;
    border: 1px solid {theme_colors["border_color"]} !important;
    color: {theme_colors["text_primary"]} !important;
}}

section[data-testid="stSidebar"] .stButton button:hover {{
    background-color: {theme_colors["button_gradient"]} !important;
    border: 1px solid {theme_colors["border_color"]} !important;
}}

/* Special styling for theme toggle button in sidebar */
.theme-toggle-sidebar {{
    background: {theme_colors["button_gradient"]} !important;
    color: {theme_colors["text_primary"]} !important;
    border: 1px solid {theme_colors["border_color"]} !important;
    border-radius: 8px !important;
    padding: 10px 15px !important;
    width: 100% !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
    margin: 5px 0 !important;
}}

.theme-toggle-sidebar:hover {{
    background: {theme_colors["button_hover"]} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
}}

/* Hide default radio buttons completely */
div[data-testid="stRadio"] {{
    display: none !important;
}}

/* Additional theme-specific styling */
.css-1lcbmhc, .css-1d391kg, .css-k1vhr4 {{
    background-color: {theme_colors["sidebar_bg"]} !important;
}}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    background-color: {theme_colors["sidebar_bg"]} !important;
}}

/* Text elements color */
.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, 
.css-1d391kg p, .css-1d391kg span, .css-1d391kg div {{
    color: {theme_colors["text_primary"]} !important;
}}

/* Main content text */
.stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {{
    color: {theme_colors["text_primary"]} !important;
}}

/* Input fields */
.stTextInput input, .stSelectbox select, .stTextArea textarea {{
    background-color: {theme_colors["sidebar_bg"]} !important;
    color: {theme_colors["text_primary"]} !important;
    border: 1px solid {theme_colors["border_color"]} !important;
}}

/* Metrics and other components */
.stMetric {{
    background-color: {theme_colors["sidebar_bg"]} !important;
    color: {theme_colors["text_primary"]} !important;
    border: 1px solid {theme_colors["border_color"]} !important;
    border-radius: 8px !important;
    padding: 10px !important;
}}
    </style>
    """, unsafe_allow_html=True)

def add_navbar():
    """Add custom navbar with social media icons (without theme toggle)"""
    # Create navbar HTML
    navbar_html = f"""
    <div class="custom-navbar">
        <div class="navbar-brand">
            <span>📊 DataAnalyzer Pro</span>
        </div>
        <div class="navbar-actions">
            <div class="social-icons">
                <a href="https://wa.me/qr/RJX7SXREUWZAM1" class="social-icon" title="WhatsApp" style="color: #25D366;"><i class="fab fa-whatsapp"></i></a>
                <a href="https://www.linkedin.com/in/idriss-benfanich-70231b348?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app" class="social-icon" title="LinkedIn"><i class="fab fa-linkedin"></i></a>
            </div>
        </div>
    </div>
    
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Add div for main content with padding to account for fixed navbar -->
    <div class="main-content">
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

def create_enhanced_sidebar_navigation():     
    """Create enhanced sidebar navigation with theme support and theme toggle button"""
    # Initialize theme
    initialize_theme()
    
    # Get current page from session state or default     
    nav_options = ["🏠 Accueil", "🔀 Fusion", "📊 Visualisation", "Analyse stratégique", "🤖 Prédiction", "dashboard"]     
    current_page = st.session_state.get('current_page', nav_options[0])          
    
    # Create custom navigation that matches the design in the image     
    # Use a hidden container for the state management but don't display radio buttons     
    with st.sidebar.container():         
        # This hidden radio button maintains the state but won't be shown         
        page = st.radio(             
            "Navigation",              
            nav_options,              
            index=nav_options.index(current_page),              
            label_visibility="collapsed",             
            key="hidden_nav"         
        )                  
        
        # Update current page in session state         
        if page != current_page:             
            st.session_state['current_page'] = page          
        
        # Custom navigation items styling for card-style buttons with theme support
        current_theme = st.session_state.get("theme_mode", "dark")
        
        st.sidebar.markdown(f"""  
        <style>     
            /* Hide the default radio buttons completely */     
            div[data-testid="stRadio"] {{         
                display: none !important;     
            }}          
            
            /* Card-style navigation item with theme support */     
            .card-nav-item {{         
                background-color: {'rgba(255,255,255,0.1)' if current_theme == 'dark' else 'rgba(0,0,0,0.05)'};         
                border-radius: 10px;         
                padding: 15px;         
                margin-bottom: 8px;         
                display: flex;         
                align-items: center;         
                cursor: pointer;         
                transition: all 0.3s ease;
                border: 1px solid {'rgba(255,255,255,0.1)' if current_theme == 'dark' else 'rgba(0,0,0,0.1)'};     
            }}          
            
            .card-nav-item.active {{         
                background-color: {'rgba(255,255,255,0.2)' if current_theme == 'dark' else 'rgba(0,0,0,0.1)'};         
                border-left: 4px solid {'#ffffff' if current_theme == 'dark' else '#3b82f6'};
                border: 1px solid {'rgba(255,255,255,0.3)' if current_theme == 'dark' else 'rgba(0,0,0,0.2)'};     
            }}          
            
            .card-nav-item:hover {{         
                background-color: {'rgba(255,255,255,0.15)' if current_theme == 'dark' else 'rgba(0,0,0,0.08)'};         
                transform: translateX(5px);
                border: 1px solid {'rgba(255,255,255,0.2)' if current_theme == 'dark' else 'rgba(0,0,0,0.15)'};     
            }}          
            
            .card-nav-icon {{         
                margin-right: 15px;         
                font-size: 24px;         
                color: {'#ffffff' if current_theme == 'dark' else '#1f2937'};     
            }}          
            
            .card-nav-text {{         
                color: {'#ffffff' if current_theme == 'dark' else '#1f2937'};         
                font-size: 18px;         
                font-weight: 500;     
            }}          
            
            /* Button styling with theme support */     
            div.stButton > button {{         
                margin-top: 2px !important;         
                margin-bottom: 2px !important;
                background-color: transparent !important;
                border: 1px solid {'rgba(255,255,255,0.1)' if current_theme == 'dark' else 'rgba(0,0,0,0.1)'} !important;
                color: {'#ffffff' if current_theme == 'dark' else '#1f2937'} !important;     
            }}
            
            div.stButton > button:hover {{
                background-color: {'rgba(255,255,255,0.1)' if current_theme == 'dark' else 'rgba(0,0,0,0.05)'} !important;
                border: 1px solid {'rgba(255,255,255,0.2)' if current_theme == 'dark' else 'rgba(0,0,0,0.15)'} !important;
            }}          
        </style>     
        """, unsafe_allow_html=True)
    
    # Theme toggle button at the top of sidebar
    current_theme = st.session_state.get("theme_mode", "dark")
    theme_icon = "🌙" if current_theme == "light" else "☀️"
    theme_text = "Mode Sombre" if current_theme == "light" else "Mode Clair"
    
    # Add some spacing and the theme toggle button
    st.sidebar.markdown("### 🎨 Thème")
    
    if st.sidebar.button(f"{theme_icon} {theme_text}", key="sidebar_theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()
    
    # Navigation section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Accueil", key="nav_home", use_container_width=True):
        st.session_state['current_page'] = "🏠 Accueil"
        st.rerun()
    
    if st.sidebar.button("🔀 Fusion", key="nav_fusion", use_container_width=True):
        st.session_state['current_page'] = "🔀 Fusion"
        st.rerun()
    
    if st.sidebar.button("📊 Visualisation", key="nav_viz", use_container_width=True):
        st.session_state['current_page'] = "📊 Visualisation"
        st.rerun()
        
    if st.sidebar.button("🤖 Prédiction", key="nav_pred", use_container_width=True):
        st.session_state['current_page'] = "🤖 Prédiction"
        st.rerun()
        
    if st.sidebar.button("dashboard", key="nav_dashboard", use_container_width=True):
        st.session_state['current_page'] = "dashboard"
        st.rerun()
    
    return page

def display_enhanced_filter_options():
    """Display enhanced filter options with theme support"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtres")
    
    # Initialize session state variables if they don't exist
    if "show_filter_category" not in st.session_state:
        st.session_state["show_filter_category"] = False
    if "show_filter_numeric" not in st.session_state:
        st.session_state["show_filter_numeric"] = False
    
    # Boutons pour le filtrage
    cat_filter_clicked = st.sidebar.button("📊 Catégories", key="cat_filter", use_container_width=True)
    num_filter_clicked = st.sidebar.button("🔢 Numériques", key="num_filter", use_container_width=True)
    
    # Logic for filter buttons
    if cat_filter_clicked:
        st.session_state["show_filter_category"] = not st.session_state["show_filter_category"]
        st.session_state["show_filter_numeric"] = False
        st.rerun()

    if num_filter_clicked:
        st.session_state["show_filter_numeric"] = not st.session_state["show_filter_numeric"]
        st.session_state["show_filter_category"] = False
        st.rerun()