import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_page():
    
    st.header("📊 Décrochage Scolaire et Aides Sociales")
    
    # Enhanced Custom CSS for the dashboard
    st.markdown("""
    <style>
    /* Global Dashboard Styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Metric Containers */
    .metric-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Filter Section */
    .filter-section {
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(255, 159, 67, 0.1) 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.125);
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
    }
    
    /* Chart Containers */
    .chart-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Dashboard Sections */
    .dashboard-section {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.1) 0%, rgba(80, 201, 195, 0.1) 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 25px 0;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 40px 0 rgba(31, 38, 135, 0.4);
    }
    
    /* Analysis Buttons */
    .analysis-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.3);
        margin: 5px;
    }
    
    .analysis-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px 0 rgba(31, 38, 135, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
        margin: 10px 0;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    .kpi-title {
        font-size: 14px;
        font-weight: 600;
        color: #8892b0;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #64ffda;
        margin-bottom: 5px;
    }
    
    .kpi-delta {
        font-size: 12px;
        font-weight: 500;
        color: #ffd700;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px;
        font-weight: 700;
        margin: 20px 0;
        text-align: center;
    }
    
    /* Chart Titles */
    .chart-title {
        font-size: 18px;
        font-weight: 600;
        color: #ccd6f6;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* Data Preview */
    .data-preview {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Responsive Grid for Charts */
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .chart-item {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Animation for loading */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animated-section {
        animation: slideInUp 0.6s ease-out;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # File uploader section with enhanced styling
    st.markdown('<div class="filter-section animated-section">', unsafe_allow_html=True)
    st.markdown("### 📁 Import de Données")
    uploaded_file = st.file_uploader(
        "", 
        type=["xlsx", "csv"],
        help="Importez votre fichier de données d'étudiants (CSV ou Excel)"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    @st.cache_data
    def load_data(file):
        """Load data from uploaded file"""
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier: {str(e)}")
            return None

    if uploaded_file:
        df = load_data(uploaded_file)
        
        if df is not None:
            # Column renaming for consistency
            cols_mapping = {
                'id_situation': 'situation',
                'GenreFr': 'genre',
                'cycle': 'cycle',
                'niveux': 'niveau',
                'LL_MIL': 'milieu',
                'll_com': 'commune',
                'NOM_ETABL': 'etab',
                'Age': 'age'
            }
            
            # Rename columns if they exist
            df.rename(columns={c: cols_mapping[c] for c in cols_mapping if c in df.columns}, inplace=True)

            # Data preview section with enhanced styling
            with st.expander("👀 Aperçu des données", expanded=False):
                st.markdown('<div class="data-preview">', unsafe_allow_html=True)
                st.dataframe(df.head(), use_container_width=True)
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; margin-top: 10px; padding: 10px; background: rgba(100, 255, 218, 0.1); border-radius: 8px;">
                    <span><strong>📊 Lignes:</strong> {len(df):,}</span>
                    <span><strong>📋 Colonnes:</strong> {len(df.columns)}</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Verify required columns
            required_columns = ['situation', 'age']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colonnes manquantes: {', '.join(missing_columns)}")
                st.info("Les colonnes requises sont: " + ", ".join(required_columns))
                st.stop()

            # Initialize social aids columns
            aides = ["Internat", "Dar talib", "Programme Tayssir", "Fournitures scolaires",
                     "Transport scolaire", "Restauration", "Un million de cartables"]
            
            for aide in aides:
                if aide not in df.columns:
                    df[aide] = 0

            # Sidebar filters with enhanced styling
            st.sidebar.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: white; text-align: center; margin: 0;">🔍 Filtres de Données</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Age filter
            age_min, age_max = int(df['age'].min()), int(df['age'].max())
            age_range = st.sidebar.slider(
                "📅 Tranche d'âge", 
                age_min, age_max, 
                (age_min, age_max),
                help="Sélectionnez la tranche d'âge à analyser"
            )

            # Genre filter
            genre_options = []
            if 'genre' in df.columns:
                genre_options = sorted(df['genre'].dropna().unique())
                genre_selection = st.sidebar.multiselect(
                    "👥 Genre", 
                    options=genre_options,
                    help="Filtrer par genre"
                )
            else:
                genre_selection = []

            # Milieu filter
            milieu_options = []
            if 'milieu' in df.columns:
                milieu_options = sorted(df['milieu'].dropna().unique())
                milieu_selection = st.sidebar.multiselect(
                    "🏘️ Milieu", 
                    options=milieu_options,
                    help="Filtrer par milieu (urbain/rural)"
                )
            else:
                milieu_selection = []

            # Commune filter
            commune_options = []
            if 'commune' in df.columns:
                commune_options = sorted(df['commune'].dropna().unique())
                commune_selection = st.sidebar.multiselect(
                    "🏙️ Commune", 
                    options=commune_options,
                    help="Filtrer par commune"
                )
            else:
                commune_selection = []

            # Établissement filter (dependent on commune)
            etab_options = []
            if 'etab' in df.columns:
                if commune_selection and 'commune' in df.columns:
                    etab_options = sorted(df[df['commune'].isin(commune_selection)]['etab'].dropna().unique())
                else:
                    etab_options = sorted(df['etab'].dropna().unique())
                
                etab_selection = st.sidebar.multiselect(
                    "🏫 Établissement", 
                    options=etab_options,
                    help="Filtrer par établissement"
                )
            else:
                etab_selection = []

            # Cycle filter
            cycle_options = []
            if 'cycle' in df.columns:
                cycle_options = sorted(df['cycle'].dropna().unique())
                cycle_selection = st.sidebar.multiselect(
                    "📚 Cycle", 
                    options=cycle_options,
                    help="Filtrer par cycle d'études"
                )
            else:
                cycle_selection = []

            # Niveau filter (dependent on cycle)
            niveau_options = []
            if 'niveau' in df.columns:
                if cycle_selection and 'cycle' in df.columns:
                    niveau_options = sorted(df[df['cycle'].isin(cycle_selection)]['niveau'].dropna().unique())
                else:
                    niveau_options = sorted(df['niveau'].dropna().unique())
                
                niveau_selection = st.sidebar.multiselect(
                    "📖 Niveau", 
                    options=niveau_options,
                    help="Filtrer par niveau d'études"
                )
            else:
                niveau_selection = []

            # Apply filters
            filtered_data = df.copy()
            
            # Age filter
            filtered_data = filtered_data[filtered_data['age'].between(age_range[0], age_range[1])]
            
            # Other filters
            if genre_selection:
                filtered_data = filtered_data[filtered_data['genre'].isin(genre_selection)]
            if milieu_selection:
                filtered_data = filtered_data[filtered_data['milieu'].isin(milieu_selection)]
            if commune_selection:
                filtered_data = filtered_data[filtered_data['commune'].isin(commune_selection)]
            if etab_selection:
                filtered_data = filtered_data[filtered_data['etab'].isin(etab_selection)]
            if cycle_selection:
                filtered_data = filtered_data[filtered_data['cycle'].isin(cycle_selection)]
            if niveau_selection:
                filtered_data = filtered_data[filtered_data['niveau'].isin(niveau_selection)]

            # Calculate KPIs
            total_students = len(filtered_data)
            
            # Define abandonment situations
            abandon_mask = filtered_data['situation'].isin([2, 5])
            non_reinscrit_mask = filtered_data['situation'] == 2
            quit_school_mask = filtered_data['situation'] == 5
            
            total_abandons = filtered_data[abandon_mask].shape[0]
            total_non_reinscrit = filtered_data[non_reinscrit_mask].shape[0]
            total_quit_school = filtered_data[quit_school_mask].shape[0]
            
            # Calculate beneficiaries of social aids
            aid_beneficiaries = filtered_data[aides].any(axis=1)
            total_beneficiaries = aid_beneficiaries.sum()

            # Continue with Part 2...
            # Continuation from Part 1...

            
# Display KPIs with enhanced styling and GREEN arrows
            st.markdown('<div class="section-header animated-section">📈 Indicateurs Clés de Performance</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">👥 Total Étudiants</div>
                    <div class="kpi-value">{total_students:,}</div>
                    <div class="kpi-delta" style="color: #00ff88;">Base de données</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                abandon_rate = (total_abandons / total_students * 100) if total_students > 0 else 0
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">❌ Abandons Totaux</div>
                    <div class="kpi-value">{total_abandons:,}</div>
                    <div class="kpi-delta" style="color: #00ff88;">↗️ {abandon_rate:.1f}% du total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                non_reinscrit_rate = (total_non_reinscrit / total_students * 100) if total_students > 0 else 0
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">🔄 Non Ré-inscrits</div>
                    <div class="kpi-value">{total_non_reinscrit:,}</div>
                    <div class="kpi-delta" style="color: #00ff88;">↗️ {non_reinscrit_rate:.1f}% du total</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                quit_rate = (total_quit_school / total_students * 100) if total_students > 0 else 0
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">🚪 Quittent l'École</div>
                    <div class="kpi-value">{total_quit_school:,}</div>
                    <div class="kpi-delta" style="color: #00ff88;">↗️ {quit_rate:.1f}% du total</div>
                </div>
                """, unsafe_allow_html=True)

            # Beneficiaries metric with green arrow
            beneficiary_rate = (total_beneficiaries / total_students * 100) if total_students > 0 else 0
            st.markdown(f"""
            <div class="dashboard-section animated-section">
                <div class="kpi-card" style="max-width: 400px; margin: 0 auto;">
                    <div class="kpi-title">🤝 Bénéficiaires d'Aides Sociales</div>
                    <div class="kpi-value">{total_beneficiaries:,}</div>
                    <div class="kpi-delta" style="color: #00ff88;">↗️ {beneficiary_rate:.1f}% reçoivent une aide</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Visualization buttons with enhanced styling
            st.markdown('<div class="section-header">📊 Tableaux de Bord Analytiques</div>', unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
            
            with col_btn1:
                show_age = st.button("📅 Dashboard Âge", use_container_width=True, type="primary")
            with col_btn2:
                show_etab = st.button("🏫 Dashboard Établissement", use_container_width=True, type="primary")
            with col_btn3:
                show_milieu = st.button("🏘️ Dashboard Milieu", use_container_width=True, type="primary")
            with col_btn4:
                show_genre = st.button("👥 Dashboard Genre", use_container_width=True, type="primary")
            with col_btn5:
                show_commune = st.button("🏙️ Dashboard Commune", use_container_width=True, type="primary")

            # Enhanced chart creation function
            def create_enhanced_chart(data, chart_type, x, y, title, color_column=None, height=500):
                """Create enhanced charts with custom styling"""
                if data.empty:
                    st.warning(f"Aucune donnée disponible pour {title}")
                    return None
                
                color_palette = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
                
                if chart_type == "bar":
                    fig = px.bar(
                        data, x=x, y=y, title=title, color=color_column,
                        text=data[y].apply(lambda x: f"{x:,}"),
                        color_discrete_sequence=color_palette
                    )
                elif chart_type == "pie":
                    fig = px.pie(
                        data, names=x, values=y, title=title,
                        color_discrete_sequence=color_palette
                    )
                elif chart_type == "line":
                    fig = px.line(
                        data, x=x, y=y, title=title, color=color_column,
                        color_discrete_sequence=color_palette
                    )
                
                # Enhanced styling
                fig.update_layout(
                    title={
                        'text': title,
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#ccd6f6', 'family': 'Arial Black'}
                    },
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#8892b0'},
                    height=height,
                    showlegend=True if color_column else False,
                    legend=dict(
                        bgcolor="rgba(255,255,255,0.1)",
                        bordercolor="rgba(255,255,255,0.2)",
                        borderwidth=1
                    )
                )
                
                if chart_type in ["bar", "line"]:
                    fig.update_xaxes(
                        gridcolor='rgba(255,255,255,0.1)',
                        title_font={'color': '#64ffda', 'size': 14}
                    )
                    fig.update_yaxes(
                        gridcolor='rgba(255,255,255,0.1)',
                        title_font={'color': '#64ffda', 'size': 14}
                    )
                
                if chart_type == "bar":
                    fig.update_traces(textposition="outside")
                
                return fig

            # Age Analysis Dashboard
            if show_age:
                st.markdown('<div class="dashboard-section animated-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">📅 Dashboard d\'Analyse par Âge</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    abandon_age_data = filtered_data[abandon_mask].groupby('age').size().reset_index(name='Abandons')
                    if not abandon_age_data.empty:
                        fig_abandon_age = create_enhanced_chart(
                            abandon_age_data, "bar", "age", "Abandons", "Distribution des Abandons par Âge"
                        )
                        st.plotly_chart(fig_abandon_age, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    beneficiary_age_data = filtered_data[aid_beneficiaries].groupby('age').size().reset_index(name='Bénéficiaires')
                    if not beneficiary_age_data.empty:
                        fig_benef_age = create_enhanced_chart(
                            beneficiary_age_data, "bar", "age", "Bénéficiaires", "Bénéficiaires d'Aides par Âge"
                        )
                        st.plotly_chart(fig_benef_age, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Age distribution pie chart
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                age_groups = pd.cut(filtered_data['age'], bins=[0, 12, 15, 18, 25, 100], labels=['<12', '12-15', '15-18', '18-25', '25+'])
                age_dist = age_groups.value_counts().reset_index()
                age_dist.columns = ['Groupe_Age', 'Nombre']
                fig_age_dist = create_enhanced_chart(age_dist, "pie", "Groupe_Age", "Nombre", "Répartition par Groupes d'Âge")
                st.plotly_chart(fig_age_dist, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

            # Genre Analysis Dashboard
            if show_genre and 'genre' in filtered_data.columns:
                st.markdown('<div class="dashboard-section animated-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">👥 Dashboard d\'Analyse par Genre</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    abandon_genre_data = filtered_data[abandon_mask].groupby('genre').size().reset_index(name='Abandons')
                    if not abandon_genre_data.empty:
                        fig_abandon_genre = create_enhanced_chart(
                            abandon_genre_data, "pie", "genre", "Abandons", "Répartition des Abandons par Genre"
                        )
                        st.plotly_chart(fig_abandon_genre, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    beneficiary_genre_data = filtered_data[aid_beneficiaries].groupby('genre').size().reset_index(name='Bénéficiaires')
                    if not beneficiary_genre_data.empty:
                        fig_benef_genre = create_enhanced_chart(
                            beneficiary_genre_data, "bar", "genre", "Bénéficiaires", "Bénéficiaires par Genre"
                        )
                        st.plotly_chart(fig_benef_genre, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Social aids distribution by genre
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                aid_by_genre = filtered_data.groupby('genre')[aides].sum().reset_index()
                aid_melted = aid_by_genre.melt(id_vars='genre', var_name='Type_Aide', value_name='Nombre')
                
                fig_aids_genre = px.bar(
                    aid_melted, x='Type_Aide', y='Nombre', color='genre',
                    title="Distribution des Aides Sociales par Genre",
                    barmode='group', color_discrete_sequence=['#667eea', '#764ba2', '#f093fb']
                )
                fig_aids_genre.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#8892b0'}, height=500, xaxis_tickangle=-45,
                    title={'x': 0.5, 'xanchor': 'center', 'font': {'color': '#ccd6f6'}}
                )
                st.plotly_chart(fig_aids_genre, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                # Établissement Analysis Dashboard
# Établissement Analysis Dashboard
            if show_etab and 'etab' in filtered_data.columns:
                st.markdown('<div class="dashboard-section animated-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🏫 Dashboard d\'Analyse par Établissement</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Top establishments with most abandons
                    abandon_etab_data = filtered_data[abandon_mask].groupby('etab').size().reset_index(name='Abandons').sort_values('Abandons', ascending=False).head(10)
                    if not abandon_etab_data.empty:
                        fig_abandon_etab = create_enhanced_chart(
                            abandon_etab_data, "bar", "etab", "Abandons", "Top 10 - Abandons par Établissement"
                        )
                        fig_abandon_etab.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_abandon_etab, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Beneficiaries by establishment
                    beneficiary_etab_data = filtered_data[aid_beneficiaries].groupby('etab').size().reset_index(name='Bénéficiaires').sort_values('Bénéficiaires', ascending=False).head(10)
                    if not beneficiary_etab_data.empty:
                        fig_benef_etab = create_enhanced_chart(
                            beneficiary_etab_data, "bar", "etab", "Bénéficiaires", "Top 10 - Bénéficiaires par Établissement"
                        )
                        fig_benef_etab.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_benef_etab, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed establishment analysis
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📊 Analyse Détaillée des Établissements</div>', unsafe_allow_html=True)
                
                # Calculate abandon rate by establishment
                etab_stats = filtered_data.groupby('etab').agg({
                    'situation': ['count', lambda x: sum(x.isin([2, 5]))]
                }).round(2)
                etab_stats.columns = ['Total_Étudiants', 'Total_Abandons']
                etab_stats['Taux_Abandon'] = (etab_stats['Total_Abandons'] / etab_stats['Total_Étudiants'] * 100).round(1)
                etab_stats = etab_stats.reset_index().sort_values('Taux_Abandon', ascending=False).head(15)
                
                if not etab_stats.empty:
                    fig_etab_rate = px.bar(
                        etab_stats, x='etab', y='Taux_Abandon',
                        title="Taux d'Abandon par Établissement (%)",
                        text='Taux_Abandon',
                        color='Taux_Abandon',
                        color_continuous_scale=['#00f2fe', '#4facfe', '#f5576c']
                    )
                    fig_etab_rate.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#8892b0'}, height=500, xaxis_tickangle=-45,
                        title={'x': 0.5, 'xanchor': 'center', 'font': {'color': '#ccd6f6'}}
                    )
                    fig_etab_rate.update_traces(texttemplate='%{text}%', textposition='outside')
                    st.plotly_chart(fig_etab_rate, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Milieu Analysis Dashboard
            if show_milieu and 'milieu' in filtered_data.columns:
                st.markdown('<div class="dashboard-section animated-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🏘️ Dashboard d\'Analyse par Milieu</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Abandons by milieu
                    abandon_milieu_data = filtered_data[abandon_mask].groupby('milieu').size().reset_index(name='Abandons')
                    if not abandon_milieu_data.empty:
                        fig_abandon_milieu = create_enhanced_chart(
                            abandon_milieu_data, "pie", "milieu", "Abandons", "Répartition des Abandons par Milieu"
                        )
                        st.plotly_chart(fig_abandon_milieu, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Beneficiaries by milieu
                    beneficiary_milieu_data = filtered_data[aid_beneficiaries].groupby('milieu').size().reset_index(name='Bénéficiaires')
                    if not beneficiary_milieu_data.empty:
                        fig_benef_milieu = create_enhanced_chart(
                            beneficiary_milieu_data, "bar", "milieu", "Bénéficiaires", "Bénéficiaires d'Aides par Milieu"
                        )
                        st.plotly_chart(fig_benef_milieu, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Comparative analysis urban vs rural
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🆚 Comparaison Urbain vs Rural</div>', unsafe_allow_html=True)
                
                # Create comparison metrics
                milieu_comparison = filtered_data.groupby('milieu').agg({
                    'situation': ['count', lambda x: sum(x.isin([2, 5]))],
                    **{aide: 'sum' for aide in aides}
                }).round(2)
                
                milieu_comparison.columns = ['Total_Étudiants', 'Total_Abandons'] + [f'Aide_{aide}' for aide in aides]
                milieu_comparison['Taux_Abandon'] = (milieu_comparison['Total_Abandons'] / milieu_comparison['Total_Étudiants'] * 100).round(1)
                milieu_comparison['Total_Aides'] = milieu_comparison[[f'Aide_{aide}' for aide in aides]].sum(axis=1)
                milieu_comparison = milieu_comparison.reset_index()
                
                if len(milieu_comparison) >= 2:
                    # Create comparison chart
                    metrics = ['Total_Étudiants', 'Total_Abandons', 'Total_Aides', 'Taux_Abandon']
                    comparison_melted = milieu_comparison.melt(
                        id_vars='milieu', 
                        value_vars=metrics,
                        var_name='Métrique', 
                        value_name='Valeur'
                    )
                    
                    fig_comparison = px.bar(
                        comparison_melted, x='Métrique', y='Valeur', color='milieu',
                        title="Comparaison des Métriques par Milieu",
                        barmode='group',
                        color_discrete_sequence=['#667eea', '#f5576c']
                    )
                    fig_comparison.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#8892b0'}, height=500,
                        title={'x': 0.5, 'xanchor': 'center', 'font': {'color': '#ccd6f6'}}
                    )
                    st.plotly_chart(fig_comparison, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Commune Analysis Dashboard
            if show_commune and 'commune' in filtered_data.columns:
                st.markdown('<div class="dashboard-section animated-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🏙️ Dashboard d\'Analyse par Commune</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Top communes with most abandons
                    abandon_commune_data = filtered_data[abandon_mask].groupby('commune').size().reset_index(name='Abandons').sort_values('Abandons', ascending=False).head(10)
                    if not abandon_commune_data.empty:
                        fig_abandon_commune = create_enhanced_chart(
                            abandon_commune_data, "bar", "commune", "Abandons", "Top 10 - Abandons par Commune"
                        )
                        fig_abandon_commune.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_abandon_commune, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    # Top communes with most beneficiaries
                    beneficiary_commune_data = filtered_data[aid_beneficiaries].groupby('commune').size().reset_index(name='Bénéficiaires').sort_values('Bénéficiaires', ascending=False).head(10)
                    if not beneficiary_commune_data.empty:
                        fig_benef_commune = create_enhanced_chart(
                            beneficiary_commune_data, "bar", "commune", "Bénéficiaires", "Top 10 - Bénéficiaires par Commune"
                        )
                        fig_benef_commune.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_benef_commune, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

           
    else:
        # Enhanced welcome message when no file is uploaded
        st.markdown(f"""
        <div class="dashboard-section animated-section" style="text-align: center; padding: 80px 40px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; margin-bottom: 20px;">
                🎯 Tableau de Bord Analytique
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 600; margin-bottom: 30px;">
                Décrochage Scolaire & Aides Sociales
            </div>
            <div style="font-size: 18px; color: #8892b0; margin-bottom: 40px; line-height: 1.6;">
                Explorez et analysez les données éducatives avec des visualisations interactives<br>
                et des insights approfondis sur les tendances scolaires.
            </div>
            <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%); padding: 30px; border-radius: 20px; backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.18); margin: 20px 0;">
                <div style="font-size: 16px; color: #64ffda; margin-bottom: 15px;">
                    📁 Pour commencer, importez vos données
                </div>
                <div style="font-size: 14px; color: #ccd6f6;">
                    Formats supportés: Excel (.xlsx) • CSV (.csv)
                </div>
            </div>
        """, unsafe_allow_html=True)
