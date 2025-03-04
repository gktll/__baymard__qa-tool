import pandas as pd
from utils.data_processing import compute_overall_statistics


def get_dataset_info(df: pd.DataFrame) -> dict:
    """
    Extract dataset information such as available case studies, themes, topics, and platforms.
    Corrects platform extraction by mapping platform codes to readable platform names.
    """
    case_studies = [str(x) for x in df['Case Study Title'].unique() if pd.notna(x)]
    themes = [str(x) for x in df['Catalog Theme Title'].unique() if pd.notna(x)]
    topics = [str(x) for x in df['Catalog Topic Title'].unique() if pd.notna(x)]
    
    # ✅ Extract platform statistics from existing function
    platform_stats = compute_overall_statistics(df).to_dict(orient="records")[0]

    # ✅ Fix platforms list to return human-readable names instead of raw codes
    platforms = []
    if platform_stats["Desktop"] > 0:
        platforms.append("Desktop")
    if platform_stats["Mobile"] > 0:
        platforms.append("Mobile")
    if platform_stats["App"] > 0:
        platforms.append("App")

    return {
        'case_studies': case_studies,
        'themes': themes,
        'topics': topics,
        'platforms': platforms,  # ✅ Fixed: Now it returns readable names
        'total_rows': len(df),
        'columns': df.columns.tolist()
    }


def rank_case_studies_by_impact(
    df: pd.DataFrame,
    group_by: list = None,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Ranks case studies by performance, supporting different levels of grouping.
    
    Parameters:
    - df (pd.DataFrame): The dataset.
    - group_by (list): List of columns to group by (e.g., ['Citation Code: Platform-Specific', 'Catalog Theme Title']).
    - ascending (bool): Whether to sort in ascending order (low to high) or descending order (high to low).

    Returns:
    - pd.DataFrame: Ranked impact of case studies.
    """

    if "Impact" not in df.columns or df.empty:
        return pd.DataFrame({"Error": ["No impact data available"]})

    df = df.copy()
    df["Impact_Score"] = pd.to_numeric(df["Impact"], errors="coerce")  # Convert impact to numeric

    # If no grouping is provided, rank case studies overall
    if group_by:
        result = df.groupby(group_by).agg(
            Average_Impact=("Impact_Score", "mean"),
            Guidelines_Count=("Impact_Score", "count")
        ).reset_index()
    else:
        result = df.groupby("Case Study Title").agg(
            Average_Impact=("Impact_Score", "mean"),
            Guidelines_Count=("Impact_Score", "count")
        ).reset_index()

    # Sort by impact
    result = result.sort_values("Average_Impact", ascending=ascending).reset_index(drop=True)

    return result


def compare_guideline_across_sites(df: pd.DataFrame, guideline_id: str, platform: str = None) -> pd.DataFrame:
    """Compare how sites implement a specific guideline across platforms."""
    df = df.copy()
    
    # Ensure guideline exists
    if guideline_id not in df['Title'].unique():
        return pd.DataFrame({"Error": [f"Guideline '{guideline_id}' not found"]})

    # Filter by guideline
    guideline_df = df[df['Title'] == guideline_id]

    # Normalize platform input
    platform_mapping = {"desktop": "D", "mobile": "M", "app": "A"}
    if platform and platform.lower() in platform_mapping:
        guideline_df = guideline_df[
            guideline_df['Citation Code: Platform-Specific'].str.contains(platform_mapping[platform.lower()], na=False)
        ]
    
    return guideline_df[['Case Study Title', 'Impact', 'Citation Code: Platform-Specific', 'Estimated Cost']]



def search_guideline(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Search guidelines by number, title, theme, or topic."""
    return df[
        df['Title'].str.contains(search_term, case=False, na=False) |
        df['Catalog Theme Title'].str.contains(search_term, case=False, na=False) |
        df['Catalog Topic Title'].str.contains(search_term, case=False, na=False)
    ][['Title', 'Catalog Theme Title', 'Catalog Topic Title', 'Implementation Status', 'Impact']]



def get_theme_guidelines(df: pd.DataFrame, theme: str, topic: str = None) -> pd.DataFrame:
    """Get guidelines within a given theme and optionally filter by topic."""
    if theme not in df['Catalog Theme Title'].unique():
        return pd.DataFrame({"Error": [f"Theme '{theme}' not found"]})

    mask = df['Catalog Theme Title'] == theme
    if topic:
        if topic not in df['Catalog Topic Title'].unique():
            return pd.DataFrame({"Error": [f"Topic '{topic}' not found within theme '{theme}'"]})
        mask &= df['Catalog Topic Title'] == topic

    return df[mask][['Title', 'Catalog Theme Title', 'Catalog Topic Title', 'Impact']]



def analyze_guidelines_by_criteria(
    df: pd.DataFrame,
    theme: str = None,
    topic: str = None,
    platform: str = None,
    low_cost: bool = False,
    high_impact: bool = False,
    violated: bool = False,
    adhered: bool = False,
    na: bool = False
) -> pd.DataFrame:
    """Flexible analysis of guidelines based on multiple criteria."""
    filtered = df.copy()
    
    if theme:
        filtered = filtered[filtered['Catalog Theme Title'] == theme]
    if topic:
        filtered = filtered[filtered['Catalog Topic Title'] == topic]

    # Handle platform mapping
    platform_mapping = {"desktop": "D", "mobile": "M", "app": "A"}
    if platform and platform.lower() in platform_mapping:
        filtered = filtered[filtered['Citation Code: Platform-Specific'].str.contains(platform_mapping[platform.lower()], na=False)]

    if low_cost:
        filtered = filtered[filtered["Estimated Cost"] == "low"]
    
    if high_impact:
        filtered = filtered[pd.to_numeric(filtered['Impact'], errors='coerce').fillna(0) >= 4]

    if violated:
        filtered = filtered[filtered['Implementation Status'] == 'violated']
    if adhered:
        filtered = filtered[filtered['Implementation Status'] == 'adhered']
    if na:
        filtered = filtered[filtered['Implementation Status'].isna()]

    return filtered[['Title', 'Catalog Theme Title', 'Catalog Topic Title', 'Impact', 'Implementation Status']]



def analyze_site_adherence(
    df: pd.DataFrame,
    status: str,
    platform: str = None,
    low_cost: bool = False,
    high_impact: bool = False
) -> pd.DataFrame:
    """Analyze sites based on guideline adherence patterns."""
    df = df.copy()
    df['Impact_Score'] = pd.to_numeric(df['Impact'], errors='coerce').fillna(0)

    mask = df['Implementation Status'] == status

    platform_mapping = {"desktop": "D", "mobile": "M", "app": "A"}
    if platform and platform.lower() in platform_mapping:
        mask &= df['Citation Code: Platform-Specific'].str.contains(platform_mapping[platform.lower()], na=False)

    if low_cost:
        mask &= df['Estimated Cost'] == 'low'
    if high_impact:
        mask &= df['Impact_Score'] >= 4

    return df[mask].groupby('Case Study Title').size().sort_values(ascending=False)




def execute_function_call(df: pd.DataFrame, function_name: str, arguments: dict):
    """
    Executes a function based on OpenAI's tool calling response.
    """
    if function_name == "get_dataset_info":
        return get_dataset_info(df)

    elif function_name == "compute_overall_statistics":
        return compute_overall_statistics(df).to_dict(orient="records")
    
    elif function_name in ["rank_case_studies_by_impact", "rank_case_studies_by_performance"]:
        return rank_case_studies_by_impact(
            df,
            group_by=arguments.get("group_by", None),
            ascending=arguments.get("ascending", False)
        ).to_dict(orient="records")
    
    elif function_name == "compare_guideline_across_sites":
        guideline_id = arguments["guideline_id"].strip().lower()
        platform = arguments.get("platform", None)
        
        # Normalize possible formats (strip whitespace and enforce lowercase)
        df["Title"] = df["Title"].astype(str).str.strip().str.lower()
        
        # Exact match instead of contains to prevent false positives
        matches = df[df['Title'] == guideline_id]
        
        if matches.empty:
            return pd.DataFrame({"Error": [f"Guideline '{arguments['guideline_id']}' not found"]}).to_dict(orient="records")
        
        # Normalize platform input
        platform_mapping = {"desktop": "D", "mobile": "M", "app": "A"}
        if platform and platform.lower() in platform_mapping:
            matches = matches[matches['Citation Code: Platform-Specific'].str.contains(platform_mapping[platform.lower()], na=False)]
        
        return matches[['Case Study Title', 'Impact', 'Citation Code: Platform-Specific', 'Estimated Cost']].to_dict(orient="records")
    
    elif function_name == "search_guideline":
        required_columns = ["Title", "Catalog Theme Title", "Catalog Topic Title", "Implementation Status", "Impact"]
        available_columns = [col for col in required_columns if col in df.columns]
        
        if not available_columns:
            return pd.DataFrame({"Error": ["No matching columns found in dataset"]}).to_dict(orient="records")
        
        return df[
            (df['Title'].str.contains(arguments["search_term"], case=False, na=False)) | 
            (df['Catalog Theme Title'].str.contains(arguments["search_term"], case=False, na=False)) | 
            (df['Catalog Topic Title'].str.contains(arguments["search_term"], case=False, na=False))
        ][available_columns].to_dict(orient="records")
    
    elif function_name == "get_theme_guidelines":
        return get_theme_guidelines(
            df,
            theme=arguments["theme"],
            topic=arguments.get("topic", None)
        ).to_dict(orient="records")
    
    elif function_name == "analyze_guidelines_by_criteria":
        return analyze_guidelines_by_criteria(
            df,
            theme=arguments.get("theme", None),
            topic=arguments.get("topic", None),
            platform=arguments.get("platform", None),
            low_cost=arguments.get("low_cost", None),
            high_impact=arguments.get("high_impact", None),
            violated=arguments.get("violated", None),
            adhered=arguments.get("adhered", None),
            na=arguments.get("na", None)
        ).to_dict(orient="records")
    
    elif function_name == "analyze_site_adherence":
        return analyze_site_adherence(
            df,
            status=arguments["status"],
            platform=arguments.get("platform", None),
            low_cost=arguments.get("low_cost", None),
            high_impact=arguments.get("high_impact", None)
        ).to_dict(orient="records")
    
    else:
        raise ValueError(f"Unknown function: {function_name}")
