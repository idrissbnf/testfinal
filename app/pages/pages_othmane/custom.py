import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def create_custom_viz_tab(df):
    """Crée l'onglet Visualisations Personnalisées"""
    st.header("📈 Visualisations Personnalisées")
    
    # Statistiques descriptives
    st.subheader("📊 Statistiques Descriptives")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    if numeric_cols:
        col_stats, col_groupby = st.columns(2)
        with col_stats:
            selected_numeric_col = st.selectbox("Colonne numérique", numeric_cols)
        with col_groupby:
            groupby_col = st.selectbox("Grouper par (optionnel)", [None] + categorical_columns)
        
        if st.button("📈 Calculer les statistiques"):
            try:
                if groupby_col is None:
                    # Statistiques globales
                    stats_data = {
                        'Statistique': ['Nombre', 'Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max', 'Q1', 'Q3'],
                        'Valeur': [
                            df[selected_numeric_col].count(),
                            round(df[selected_numeric_col].mean(), 2),
                            round(df[selected_numeric_col].median(), 2),
                            round(df[selected_numeric_col].std(), 2),
                            df[selected_numeric_col].min(),
                            df[selected_numeric_col].max(),
                            round(df[selected_numeric_col].quantile(0.25), 2),
                            round(df[selected_numeric_col].quantile(0.75), 2)
                        ]
                    }
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(pd.DataFrame(stats_data))
                    with col2:
                        fig_hist = px.histogram(df, x=selected_numeric_col, 
                                              title=f"Distribution de {selected_numeric_col}")
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    fig_box = px.box(df, y=selected_numeric_col, title=f"Box Plot - {selected_numeric_col}")
                    st.plotly_chart(fig_box, use_container_width=True)
                else:
                    # Statistiques groupées
                    grouped_stats = df.groupby(groupby_col)[selected_numeric_col].agg([
                        'count', 'mean', 'median', 'std', 'min', 'max',
                        lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)
                    ]).round(2)
                    grouped_stats.columns = ['Nombre', 'Moyenne', 'Médiane', 'Écart-type', 'Min', 'Max', 'Q1', 'Q3']
                    
                    st.dataframe(grouped_stats, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_box_grouped = px.box(df, x=groupby_col, y=selected_numeric_col,
                                               title=f"Box Plot - {selected_numeric_col} par {groupby_col}")
                        fig_box_grouped.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_box_grouped, use_container_width=True)
                    
                    with col2:
                        means_data = df.groupby(groupby_col)[selected_numeric_col].mean().reset_index()
                        fig_means = px.bar(means_data, x=groupby_col, y=selected_numeric_col,
                                         title=f"Moyenne de {selected_numeric_col} par {groupby_col}")
                        fig_means.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_means, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    
    # Graphiques personnalisés
    st.markdown("---")
    st.subheader("🎛️ Créer votre propre visualisation")
    
    all_columns = df.columns.tolist()
    col1, col2 = st.columns(2)
    
    with col1:
        x_axis = st.selectbox("Axe X", all_columns)
        chart_type = st.selectbox("Type de graphique", 
                                ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram"])
    with col2:
        y_axis = st.selectbox("Axe Y", all_columns, index=1 if len(all_columns) > 1 else 0)
        color_by = st.selectbox("Colorer par", [None] + categorical_columns)
    
    if st.button("🎨 Générer le graphique"):
        try:
            chart_functions = {
                "Bar Chart": lambda: px.bar(df.groupby(x_axis)[y_axis].count().reset_index(), x=x_axis, y=y_axis) 
                            if df[x_axis].dtype == 'object' 
                            else px.bar(df, x=x_axis, y=y_axis, color=color_by),
                "Line Chart": lambda: px.line(df, x=x_axis, y=y_axis, color=color_by),
                "Scatter Plot": lambda: px.scatter(df, x=x_axis, y=y_axis, color=color_by),
                "Box Plot": lambda: px.box(df, x=x_axis, y=y_axis, color=color_by),
                "Histogram": lambda: px.histogram(df, x=x_axis, color=color_by)
            }
            
            fig = chart_functions[chart_type]()
            fig.update_layout(title=f"{chart_type}: {y_axis} vs {x_axis}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur: {str(e)}")