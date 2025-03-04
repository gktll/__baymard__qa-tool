import streamlit as st
import pandas as pd
from utils.data_processing import compute_overall_statistics
from utils.agent.tools import get_dataset_info, rank_case_studies_by_impact
import plotly.express as px
import plotly.graph_objects as go


def extract_platform_column(df: pd.DataFrame):
    """Extracts a 'platform' column from 'Citation Code: Platform-Specific'."""
    if "Citation Code: Platform-Specific" in df.columns:
        df = df.copy()
        df["platform"] = df["Citation Code: Platform-Specific"].astype(str).str.strip().str[-1].map({
            "D": "Desktop",
            "M": "Mobile",
            "A": "App"
        })
    return df


def filter_performance_by_platform(df: pd.DataFrame):
    """Filter and compute performance statistics by platform."""
    df = extract_platform_column(df)
    dataset_info = get_dataset_info(df)
    platforms = dataset_info["platforms"]
    
    if "Impact" not in df.columns or "platform" not in df.columns:
        return pd.DataFrame({"Error": ["Required columns ('Impact', 'platform') not found in dataset"]})
    
    # Ensure we filter the dataset based on extracted platforms
    df_filtered = df[df["platform"].isin(platforms)]
    
    if df_filtered.empty:
        return pd.DataFrame({"Error": ["No matching data for extracted platforms"]})
    
    performance_df = df_filtered.groupby("platform")["Impact"].mean().reset_index()
    return performance_df



def visualize_case_study_performance(df: pd.DataFrame):
    """Create an interactive visualization of performance by case study and platform using Plotly."""
    # Convert Impact to numeric and create a copy to avoid modifying original
    df = df.copy()
    df['Impact'] = pd.to_numeric(df['Impact'], errors='coerce')
    
    # Calculate average impact and count in one step
    avg_impact = (df.groupby(['Case Study Title', 'platform'])
                 .agg({'Impact': ['mean', 'size']})
                 .reset_index())
    
    # Flatten column names
    avg_impact.columns = ['Case Study Title', 'platform', 'avg_impact', 'count']
    
    # Create the scatter plot
    fig = px.scatter(
        avg_impact,
        x='avg_impact',
        y='platform',
        color='Case Study Title',
        size='count',
        size_max=50,
        hover_data={
            'avg_impact': ':.2f',
            'count': True,
            'Case Study Title': True
        },
        labels={
            'avg_impact': 'Average Impact Score',
            'platform': 'Platform',
            'count': 'Number of Guidelines'
        }
    )
    
    # Customize layout
    fig.update_layout(
        title='Case Study Performance by Platform',
        xaxis_title='Average Impact Score',
        yaxis_title='Platform',
        height=400,
        legend_title='Case Study',
        showlegend=True,
        hovermode='closest',
        template='plotly_white'
    )
    
    return fig



def rank_case_studies_by_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Rank case studies by their average impact score."""
    return (df.groupby('Case Study Title')
            .agg({
                'Impact': ['mean', 'size', 'std']
            })
            .round(2)
            .reset_index())



# def presentation_tab_4(df: pd.DataFrame):
#     """Streamlit UI for Tab 4 - Performance Analysis with interactive visualizations."""
#     st.title("Tab 4: Performance Analysis")
    
#     # Ensure we have platform data and numeric Impact
#     df = extract_platform_column(df)
#     df = df.copy()
#     df['Impact'] = pd.to_numeric(df['Impact'], errors='coerce')
    
#     # 1. Overview Statistics
#     with st.expander("1. Overview - General Statistics", expanded=True):
#         st.write(compute_overall_statistics(df))
    
#     # 2. Overall Performance
#     with st.expander("2. Performance Overall - Visualization & Data", expanded=True):
#         st.subheader("Performance Visualization")
#         fig = visualize_case_study_performance(df)
#         st.plotly_chart(fig, use_container_width=True)
        
#         st.subheader("Performance Data")
#         summary_stats = (df.groupby('Case Study Title')
#                         .agg({
#                             'Impact': ['mean', 'size', 'std']
#                         })
#                         .round(2))
#         summary_stats.columns = ['Average Impact', 'Number of Guidelines', 'Std Dev']
#         summary_stats = summary_stats.sort_values('Average Impact', ascending=False)
#         st.dataframe(summary_stats, use_container_width=True)
    
#     # 3. Platform-specific Analysis
#     dataset_info = get_dataset_info(df)
#     for platform in dataset_info["platforms"]:
#         with st.expander(f"3. {platform} Performance - Visualization & Data"):
#             platform_df = df[df["platform"] == platform]
#             if not platform_df.empty:
#                 st.subheader(f"{platform} Performance Visualization")
#                 fig = visualize_case_study_performance(platform_df)
#                 st.plotly_chart(fig, use_container_width=True)
                
#                 st.subheader(f"{platform} Performance Data")
#                 platform_stats = (platform_df.groupby('Case Study Title')
#                                 .agg({
#                                     'Impact': ['mean', 'size', 'std']
#                                 })
#                                 .round(2))
#                 platform_stats.columns = ['Average Impact', 'Number of Guidelines', 'Std Dev']
#                 platform_stats = platform_stats.sort_values('Average Impact', ascending=False)
#                 st.dataframe(platform_stats, use_container_width=True)
#             else:
#                 st.error(f"No data available for {platform}.")

def presentation_tab_4(df: pd.DataFrame):
    """Streamlit UI for Tab 4 - Performance Analysis with interactive visualizations."""
    st.title("Tab 4: Performance Analysis")
    
    # ✅ Ensure platform data exists
    df = extract_platform_column(df)
    df = df.copy()
    df['Impact'] = pd.to_numeric(df['Impact'], errors='coerce')

    # ✅ Debug: Check Impact values
    st.write("🔍 Checking Impact values before aggregation:")
    st.write(df[['Case Study Title', 'platform', 'Impact', "Title"]].dropna().head(10))

    # ✅ 1. Overview Statistics
    with st.expander("1. Overview - General Statistics", expanded=True):
        st.write(compute_overall_statistics(df))
    
    # ✅ 2. Overall Performance
    with st.expander("2. Performance Overall - Visualization & Data", expanded=True):
        st.subheader("Performance Visualization")
        fig = visualize_case_study_performance(df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Performance Data")
        summary_stats = (df.groupby('Case Study Title')
                        .agg({'Impact': ['mean', 'size', 'std']})
                        .round(2))
        summary_stats.columns = ['Average Impact', 'Number of Guidelines', 'Std Dev']
        summary_stats = summary_stats.sort_values('Average Impact', ascending=False)
        st.dataframe(summary_stats, use_container_width=True)

    # ✅ 3. Platform-specific Analysis
    dataset_info = get_dataset_info(df)
    st.write("🔍 Platforms extracted from dataset:", dataset_info["platforms"])  # Debug platforms

    for platform in dataset_info["platforms"]:
        with st.expander(f"3. {platform} Performance - Visualization & Data"):
            platform_df = df[df["platform"] == platform]

            if not platform_df.empty:
                st.subheader(f"{platform} Performance Visualization")
                fig = visualize_case_study_performance(platform_df)
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader(f"{platform} Performance Data")
                platform_stats = (platform_df.groupby('Case Study Title')
                                .agg({'Impact': ['mean', 'size', 'std']})
                                .round(2))
                platform_stats.columns = ['Average Impact', 'Number of Guidelines', 'Std Dev']
                platform_stats = platform_stats.sort_values('Average Impact', ascending=False)
                st.dataframe(platform_stats, use_container_width=True)
            else:
                st.error(f"No data available for {platform}.")








# questions

# total guidelines
# guidelines by platform

# case studies 

# sort high to low and low to high
# - impact of each site
# - impact of each site overall 
# - impact of each site by platform 
# - impact of each site by theme
# - impact of each site by platform and theme

# sort themes by impact
# most impactiful guidelines
# most impactiful guidelines within the theme 

# low cost guidelines (aka missed opportunities)

# for each single guideline, should retrieve what other site do overall and by platofrm.

# search guideline number = guideline title + theme
# tell me all guidelines within a theme

# what guidelines are most impactful within a theme, topic 
# what guidelines are low cost within the theme, topic

# site with most impactiful guidelines adhered_high or low
# site with most low cost guidelines adhered_high or low
# site with most low cost guidelines violated_high or low
# site with most impactful guidelines violated_high or low

# most violated_high or low guidelines overall, by platform, by theme, by topic 
# most adhered high guidelines overall, by platform, by theme, by topic

# what guidelines where n/a for all, for specific sites. 

# i must be able to search for specific guideline and see how it is implemented across sites




# performance of the sites overall (get overall impact, all themes, case studies)
# perfromance of the sites by platform (impact by platform, case studies)
# perfromance of the sites by platform/theme (impact, case studies)

# perfromance of the site by desktop/theme (impact, case studies)
# most adhered high impact guidelines
# some images
# most violated high impact guidelines
# some images
# most low cost guidelines adhered high
# images
# most low cost guidelines violated high
# images


