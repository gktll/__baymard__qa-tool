# utils/data_processing.py

import pandas as pd
import streamlit as st
import re
from typing import Dict
import os

def compute_overall_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes overall statistics from the DataFrame:
      - Total guidelines count.
      - Count of guidelines ids ending in 'D', 'M', and 'A'.
    """
    if df is None or df.empty:
        return pd.DataFrame({
            "Total Guidelines": [0],
            "Desktop": [0],
            "Mobile": [0],
            "App": [0]
        })
    
    guideline_id = df["Citation Code: Platform-Specific"].astype(str).str.strip()
    
    total = len(guideline_id)
    desktop_count = (guideline_id.str[-1].str.upper() == "D").sum()
    mobile_count  = (guideline_id.str[-1].str.upper() == "M").sum()
    app_count     = (guideline_id.str[-1].str.upper() == "A").sum()
    
    return pd.DataFrame({
        "Total Guidelines": [total],
        "Desktop": [desktop_count],
        "Mobile": [mobile_count],
        "App": [app_count]
    })


def apply_chart_filters(
    df: pd.DataFrame,
    search_term: str = "",
    theme_filter: str = "All",
    case_study_filter: str = "All",
    platform_filter: list = None,
    low_cost_filter: bool = False,
    sort_by_impact: bool = False,
    performance_analysis: bool = False
) -> pd.DataFrame:
    """
    Applies filters to the DataFrame and optionally analyzes performance.
    """
    filtered_df = df.copy()

    # Apply theme filter
    if theme_filter != "All":
        filtered_df = filtered_df[filtered_df['Catalog Theme Title'] == theme_filter]

    # Apply case study filter
    if case_study_filter != "All":
        filtered_df = filtered_df[filtered_df['Case Study Title'] == case_study_filter]

    # Apply platform filter
    if platform_filter is None:
        platform_filter = []
    if platform_filter:
        mask = pd.Series(False, index=filtered_df.index)
        for platform in platform_filter:
            if platform == "Desktop":
                mask |= filtered_df['Citation Code: Platform-Specific'].str.contains('D', na=False)
            elif platform == "Mobile":
                mask |= filtered_df['Citation Code: Platform-Specific'].str.contains('M', na=False)
            elif platform == "App":
                mask |= filtered_df['Citation Code: Platform-Specific'].str.contains('A', na=False)
        filtered_df = filtered_df[mask]

    # Apply search filter
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Title'].str.contains(search_term, case=False, na=False) |
            filtered_df['Citation Code: Platform-Specific'].str.contains(search_term, case=False, na=False) |
            filtered_df['Catalog Theme Title'].str.contains(search_term, case=False, na=False) |
            filtered_df['Catalog Topic Title'].str.contains(search_term, case=False, na=False)
        ]

    # Apply low cost filter
    if low_cost_filter:
        filtered_df = filtered_df[filtered_df["Estimated Cost"] == "low"]

    # Performance analysis
    if performance_analysis:
        performance_df = filtered_df.groupby('Case Study Title').agg({
            'Impact': ['mean', 'count']
        }).reset_index()
        performance_df.columns = ['Case Study Title', 'Average Impact', 'Guidelines Count']
        return performance_df.sort_values('Average Impact', ascending=False)

    # Apply impact sorting
    if sort_by_impact:
        impact_col = None
        for col in filtered_df.columns:
            if col.lower() == "impact":
                impact_col = col
                break
        if impact_col is None:
            st.warning("The 'Impact' column is missing in your dataset. Please verify your CSV file.")
        else:
            filtered_df["impact_numeric"] = pd.to_numeric(filtered_df[impact_col], errors='coerce')
            filtered_df = filtered_df.sort_values("impact_numeric", ascending=False)
            filtered_df = filtered_df.drop(columns=["impact_numeric"])

    return filtered_df


def process_datasets(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Processes the uploaded dataset to generate specific filtered subsets."""
    processed_dfs = {}

    processed_dfs = {}

    # Ensure the downloads folder exists
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    
    #--------------------------------------------------------------
    # Guidelines not yet rated
    if 'Judgement' in df.columns:
        not_rated = df[df['Judgement'] == 'not_rated'][['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Gemini URL']]
        processed_dfs['1. Not Rated Guidelines'] = not_rated
    
    #--------------------------------------------------------------
    # Guidelines missing pin links
    if 'implementation example urls' in df.columns:
        empty_link_judgement = df[
            (df['implementation example urls'].isna()) & 
            (df['Judgement'] != 'not_applicable') & 
            (df['Judgement'] != 'not_rated')
        ][['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Gemini URL']]
        processed_dfs['2. Guidelines Missing Pins'] = empty_link_judgement
    
    #--------------------------------------------------------------
    # Guidelines missing screenshots
    if 'Image URLs' in df.columns:
        empty_image_urls = df[df['Image URLs'].isna() & 
                              (df['Judgement'] != 'not_applicable') & 
                              (df['Judgement'] != 'not_rated')]
        processed_dfs['3. Guidelines Missing Screenshots'] = empty_image_urls[['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Judgement', 'Scenarios', 'Gemini URL']]

    #--------------------------------------------------------------
    # Non-empty 'Client-Facing Comment'
    if 'Client-Facing Comment' in df.columns:
        client_comment = df[df['Client-Facing Comment'].notna()][['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Gemini URL', 'Client-Facing Comment', 'Image URLs']]
        processed_dfs['4. Guidelines including Client-Facing Comments'] = client_comment

    #--------------------------------------------------------------
    # Non-empty 'Internal Comment'
    if 'Internal Comment' in df.columns:
        internal_comment = df[df['Internal Comment'].notna()][['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Judgement', 'Gemini URL', 'Internal Comment', 'Image URLs']]
        processed_dfs['5. Guidelines including Internal Comments'] = internal_comment

    #--------------------------------------------------------------
    # Mapping guidelines where "manual_judgment" = True
    if 'Is Manual Judgement?' in df.columns:
        df['Is Manual Judgement?'] = df['Is Manual Judgement?'].astype(bool)
        manual_judgement = df[df['Is Manual Judgement?']][
            ['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Judgement', 'Gemini URL', 'Client-Facing Comment', 'Internal Comment', 'Image URLs']
        ]
        processed_dfs['6. Guideline With Manual Judgement'] = manual_judgement

    #--------------------------------------------------------------
    # Mapping guidelines where "Is Nudged" = True
    if 'Is Nudged?' in df.columns:
        df['Is Nudged?'] = df['Is Nudged?'].astype(bool)
        nudged_true = df[df['Is Nudged?']][
            ['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Judgement', 'Gemini URL', 'Client-Facing Comment', 'Internal Comment', 'Image URLs']
        ]
        processed_dfs['7. Nudged Guidelines'] = nudged_true

    #--------------------------------------------------------------
    # Mapping guidelines where "Needs Discussion" = True
    if 'Needs Discussion?' in df.columns:
        df['Needs Discussion?'] = df['Needs Discussion?'].astype(bool)
        needs_discussion = df[df['Needs Discussion?']][
            ['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Gemini URL', 'Image URLs', 'Internal Comment']
        ]
        processed_dfs['8. Guidelines Needing Discussion'] = needs_discussion

    #--------------------------------------------------------------
    # Filtering "N/A" Judgments
    if 'Judgement' in df.columns:
        na_judgment_guidelines = df[df['Judgement'].str.strip().str.upper() == 'N/A']
        processed_dfs['9. All N/A Judgment Guidelines'] = na_judgment_guidelines[
            ['Citation Code: Platform-Specific', 'Case Study Title', 'Title', 'Judgement']
        ]
    
    #--------------------------------------------------------------
    # Missing Master Texts
    if 'Master Text(s)' in df.columns and 'Judgement' in df.columns:
        no_master_text_df = df[df['Master Text(s)'].isna() & df['Judgement'].isin(['adhered_high', 'violated_high'])][
            ['Citation Code: Platform-Specific', 'Title', 'Judgement', 'Master Text(s)']
        ].drop_duplicates(subset=['Citation Code: Platform-Specific', 'Judgement'])
        processed_dfs['10. Missing Master Texts'] = no_master_text_df


    #--------------------------------------------------------------
    # High-Impact Guidelines
    if 'Impact' in df.columns:
        df['Impact'] = pd.to_numeric(df['Impact'], errors='coerce')
        high_impact_df = df[(df['Impact'] >= 3) | (df['Impact'] <= -3)][
            ['Citation Code: Platform-Specific', 'Impact', 'Case Study Title', 'Title', 'Judgement', 'Gemini URL']
        ]
        processed_dfs['11. High-Impact Guidelines'] = high_impact_df


    #--------------------------------------------------------------
    # Make a df copy to keep the original untouched and modify 'ID' to 'Guideline' in df_temp
    df_temp = df.copy()
    df_temp['Guideline'] = df_temp['Citation Code: Platform-Specific'].apply(lambda id: id[:-1] if pd.notna(id) else id)

    # Print judgement differences across platforms (use df_temp)
    inconsistencies = []
    for (website, guideline), group in df_temp.groupby(['Case Study Title', 'Guideline']):
        if group['Judgement'].nunique() > 1:
            judgements = group[['Citation Code: Platform-Specific', 'Judgement', 'Gemini URL']].to_dict('records')
            inconsistencies.append({'Case Study Title': website, 'Guideline': guideline, 'Judgements': judgements})

    # Convert the inconsistencies list to a DataFrame and to csv
    inconsistencies_df = pd.DataFrame(inconsistencies)
    processed_dfs['Judgment Inconsistencies'] = inconsistencies_df


    #--------------------------------------------------------------
    # Most unusual site: Most nudged and manually rated
    if {'Case Study Title', 'Citation Code: Platform-Specific', 'Judgement'}.issubset(df.columns):
    
        # Ensure 'Citation Code: Platform-Specific' is a string and extract guideline ID
        df['guideline'] = df['Citation Code: Platform-Specific'].astype(str).str[:-1]

        # Group by Case Study and Guideline
        grouped = df.groupby(['Case Study Title', 'guideline'])

        # Identify inconsistent judgments
        inconsistencies = grouped.filter(lambda x: x['Judgement'].nunique() > 1)

        if inconsistencies.empty:
            print("✅ No judgment inconsistencies found.")
        else:
            # Collect inconsistent cases
            inconsistency_records = (
                inconsistencies.groupby(['Case Study Title', 'guideline'])
                .apply(lambda g: g[['Citation Code: Platform-Specific', 'Judgement', 'Gemini URL']].to_dict(orient='records'))
                .reset_index()
                .rename(columns={0: 'Judgements'})  # Ensure correct column assignment
            )

            processed_dfs['SItes by Deviation'] = inconsistency_records
    else:
        print("⚠️ Missing columns for deviation analysis.")

    return processed_dfs










