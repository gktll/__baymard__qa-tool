# app.py

import streamlit as st
import pandas as pd
import numpy as np
import os
from streamlit_plotly_events import plotly_events

from utils.session_manager import save_uploaded_file, load_csv, validate_csv
from utils.data_processing import compute_overall_statistics, apply_chart_filters

from utils.tab1_qa_game.visualizations import create_pills_visualization
from utils.tab2_downloads.downloads import display_download_options
from utils.tab4_presentation.presentation import presentation_tab_4


st.set_page_config(
    page_title="Guidelines Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar controls if desired.
st.markdown("""
    <style>
        [data-testid="stSidebarCollapsedControl"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Session state initialization.
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_guideline' not in st.session_state:
    st.session_state.selected_guideline = None

def main():
    if st.session_state.selected_guideline:
        from pages.guideline_detail import render_guideline_detail
        if st.button("← Back to Dashboard"):
            st.session_state.selected_guideline = None
            st.rerun()
        render_guideline_detail(st.session_state.selected_guideline)
        return

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📥 Downloads", "📈 Presentation"])

    # ---------- TAB 2: QA Visualization ----------
    with tab1:
        if st.session_state.uploaded_file is None:
            st.title("Upload Your CSV File")
            uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
            if uploaded_file:
                file_path = save_uploaded_file(uploaded_file)
                df = load_csv(file_path)
                if validate_csv(df):
                    st.session_state.uploaded_file = file_path
                    st.session_state.df = df
                    st.rerun()
                else:
                    st.error("Uploaded CSV is missing required columns or contains invalid data.")

        else:
            df = st.session_state.df
            # Compute overall statistics using your helper function.
            stats_df = compute_overall_statistics(df)
            overall_total   = stats_df["Total Guidelines"].iloc[0]
            overall_desktop = stats_df["Desktop"].iloc[0]
            overall_mobile  = stats_df["Mobile"].iloc[0]
            overall_app     = stats_df["App"].iloc[0]

            # Inject custom CSS to style the st.metric component.
            st.markdown("""
                <style>
                div[data-testid="stMetric"] {
                    border: 1px solid #27292e;  
                    border-radius: 5px;        
                    padding: 10px;              
                }
                </style>
            """, unsafe_allow_html=True)

            # Create two columns: left (60%) and right (40%)
            left_col, right_col = st.columns([0.6, 0.4])

            with left_col:
                filename = os.path.basename(st.session_state.uploaded_file)
                max_length = 30
                display_filename = filename if len(filename) <= max_length else filename[:max_length] + "..."
                st.title(display_filename)
                
                if "Case Study Title" in df.columns:
                    unique_sites = sorted(
                        [str(site) for site in df["Case Study Title"].unique() if pd.notnull(site)],
                        key=str
                    )
                    st.markdown("#### Case Studies")

                    # Create an HTML string for the pills.
                    pills_html = " ".join(
                        [
                            f'<span style="background-color:#26282d; border:1px solid #69738a; border-radius:20px; padding:5px 15px; margin:2px; display:inline-block;">{site}</span>'
                            for site in unique_sites
                        ]
                    )
                    st.markdown(pills_html, unsafe_allow_html=True)
                else:
                    st.warning("CSV missing 'Case Study Title' column.")

            with right_col:
                # Open the summary box container.
                st.markdown("#### Dataset Summary")
                
                # First row: two columns
                row1_cols = st.columns(2)
                with row1_cols[0]:
                    st.metric("Total Guidelines", overall_total)
                with row1_cols[1]:
                    st.metric("Desktop Guidelines", overall_desktop)
                
                row2_cols = st.columns(2)
                with row2_cols[0]:
                    st.metric("Mobile Guidelines", overall_mobile)
                with row2_cols[1]:
                    st.metric("App Guidelines", overall_app)
                    
            st.markdown("######")


            #
            # Filtering
            #               
            col1, col2, col3 = st.columns(3)
            with col1:
                platform_filter = st.multiselect(
                    "Filter by Platform",
                    ["Desktop", "Mobile", "App"],
                    default=["Desktop", "Mobile", "App"]
                )
                
            with col2:
                theme_filter = st.selectbox(
                    "Filter by Theme",
                    ["All"] + sorted([x for x in df['Catalog Theme Title'].unique() if pd.notna(x)])
                )
            with col3:
                case_study_filter = st.selectbox(
                    "Filter by Case Study",
                    ["All"] + sorted([x for x in df['Case Study Title'].unique() if pd.notna(x)])
                )

            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                # search_term = st.text_input("🔍 Search Guidelines", "")
                search_term = st.text_input("Search", placeholder="🔍  Search by title, citation code, theme...", label_visibility="collapsed")
            with col2:
                low_cost_filter = st.checkbox("Is Low Cost")
            with col3:
                sort_by_impact = st.checkbox("High to Low Impact")


            filtered_df = apply_chart_filters(
                df,
                search_term=search_term,
                theme_filter=theme_filter,
                case_study_filter=case_study_filter,
                platform_filter=platform_filter,
                low_cost_filter=low_cost_filter,
                sort_by_impact=sort_by_impact
            )

            st.markdown("######")        


            # 
            # Visualization Section.
            #
            fig = create_pills_visualization(filtered_df, title="")

            selected_points = plotly_events(fig, click_event=True)

            if selected_points:
                point_index = selected_points[0].get('pointIndex', None)
                if point_index is None:
                    point_index = selected_points[0].get('pointNumber', None)
                if point_index is not None:
                    clicked_citation = filtered_df.iloc[point_index]['Citation Code: Platform-Specific']
                    st.session_state.selected_guideline = clicked_citation
                    st.rerun()


            st.markdown("######")


            #
            # Table
            #  

            if not filtered_df.empty:
                display_df = filtered_df.sort_values(['Citation Code: Platform-Specific'])
                
                # Create a display dataframe with the columns we want to show
                display_df = display_df[[
                    'Citation Code: Platform-Specific',
                    'Case Study Title',
                    'Title',
                    'Judgement',
                    'Gemini URL',
                    'Image URLs'
                ]].rename(columns={
                    'Citation Code: Platform-Specific': 'Citation',
                    'Case Study Title': 'Site',
                    'Title': 'Title'
                })
                
                # Create a mapping of each unique citation to an alternating style
                unique_citations = display_df['Citation'].unique()
                citation_style_map = {citation: i % 2 for i, citation in enumerate(unique_citations)}
                
                # Define styling function
                def style_rows(row):
                    # Get the citation for this row
                    citation = row['Citation']
                    
                    # Determine if this is an even or odd group
                    group_num = citation_style_map.get(citation, 0)
                    
                    # Apply row styling based on group number
                    if group_num == 0:
                        bg_color = '#1e1f24'  # Darker background for even groups
                    else:
                        bg_color = '#2c2d33'  # Lighter background for odd groups
                    
                    # Create styles for each column
                    styles = ['background-color: ' + bg_color] * len(row)
                    
                    # Override style for judgment column
                    judgment = row['Judgement']
                    judgment_str = str(judgment).lower().strip() if not pd.isna(judgment) else 'not_rated'
                    color_map = {
                        'adhered_high': '#769b37',
                        'adhered_low': '#a1b145',
                        'violated_high': '#b42625',
                        'violated_low': '#ea7a0d',
                        'not_applicable': '#9c9c9c',
                        'neutral': '#ffc302',
                        'issue_resolved': '#0273ff',
                        'not_rated': 'rgba(255,255,255,0.3)'
                    }
                    judgment_color = color_map.get(judgment_str, '#FFFFFF')
                    
                    # Find judgment column index
                    judgment_idx = list(row.index).index('Judgement')
                    styles[judgment_idx] = f'background-color: {judgment_color}; color: white; font-weight: bold'
                    
                    return styles
                
                # Apply styling
                styled_df = display_df.style.apply(style_rows, axis=1)
                
                # Display the styled dataframe
                st.dataframe(
                    styled_df,
                    column_config={
                        "Citation": st.column_config.TextColumn("Citation", width="auto"),
                        "Site": st.column_config.TextColumn("Site", width="auto"),
                        "Judgement": st.column_config.TextColumn("Judgment", width="auto"),
                        "Title": st.column_config.TextColumn("Title", width="auto"),
                        "Gemini URL": st.column_config.LinkColumn("Gemini", display_text="Open", width="auto"),
                        "Image URLs": st.column_config.TextColumn("Images", width="auto")
                    },
                    use_container_width=True,
                    hide_index=True,
                    height=800
                )
            else:
                st.info("No guidelines match your current filter criteria. Try adjusting your filters")






    # ---------- TAB 2: QA Downloads ----------
    with tab2:
        if "df" not in st.session_state or st.session_state.df is None:
            st.warning("Please upload a file first in the Overview tab")
            return
        
        display_download_options()

    # ---------- TAB 3: Presentation ----------
    with tab3:
        presentation_tab_4(df)


if __name__ == "__main__":
    main()
