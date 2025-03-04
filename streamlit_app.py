import streamlit as st
import pandas as pd
import os
from streamlit_plotly_events import plotly_events

from utils.session_manager import save_uploaded_file, load_csv, validate_csv
from utils.data_processing import compute_overall_statistics, apply_chart_filters

from utils.tab1_qa_game.visualizations import create_pills_visualization
from utils.tab2_downloads.downloads import display_download_options
from utils.tab4_presentation.presentation import presentation_tab_4

from utils.chat import chat_interface

import plotly.express as px


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
                st.markdown("#### Guidelines")
                
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

            # Filtering section
            search_term = st.text_input("🔍 Search Guidelines", "")

            col1, col2, col3 = st.columns(3)
            with col1:
                theme_filter = st.selectbox(
                    "Filter by Theme",
                    ["All"] + sorted([x for x in df['Catalog Theme Title'].unique() if pd.notna(x)])
                )
            with col2:
                case_study_filter = st.selectbox(
                    "Filter by Case Study",
                    ["All"] + sorted([x for x in df['Case Study Title'].unique() if pd.notna(x)])
                )
            with col3:
                platform_filter = st.multiselect(
                    "Filter by Platform",
                    ["Desktop", "Mobile", "App"],
                    default=["Desktop", "Mobile", "App"]
                )

            low_cost_filter = st.checkbox("Is Low Cost")
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

            # Visualization Section.
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

            # Table Section.
            st.dataframe(
                filtered_df[[
                    'Citation Code: Platform-Specific',
                    'Case Study Title',
                    'Title',
                    'Judgement',
                    'Importance Key',
                    'Gemini URL'
                ]].rename(columns={
                    'Citation Code: Platform-Specific': 'Citation',
                    'Case Study Title': 'Site',
                    'Title': 'Title'
                }),
                column_config={
                    "Citation": st.column_config.TextColumn("Citation", width="small"),
                    "Site": st.column_config.TextColumn("Site", width="small"),
                    "Title": st.column_config.TextColumn("Title", width="auto"),
                    "Judgement": st.column_config.TextColumn("Judgment", width="small"),
                    "Importance Key": st.column_config.TextColumn("Importance", width="small"),
                    "Gemini URL": st.column_config.LinkColumn("Link", display_text="View in Gemini", width="small")
                },
                use_container_width=True,
                hide_index=True,
                height=800
            )

    # ---------- TAB 2: QA Downloads ----------
    with tab2:
        if "df" not in st.session_state or st.session_state.df is None:
            st.warning("Please upload a file first in the Overview tab")
            return
        
        display_download_options()

    # ---------- TAB 3: Chat ----------
    # with tab3:
    #     if "df" not in st.session_state or st.session_state.df is None:
    #         st.warning("Please upload a file first in the Overview tab")
    #         return
            
    #     chat_interface(st.session_state.df)
    
    # ---------- TAB 4: Presentation ----------

    with tab3:
        presentation_tab_4(df)


if __name__ == "__main__":
    main()
