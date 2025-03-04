import pandas as pd


def get_judgment_color(judgment):
    if pd.isna(judgment):
        return '#FFFFFF'
    color_map = {
        'adhered_high': '#769b37',
        'adhered_low': '#a1b145',
        'violated_high': '#b42625',
        'violated_low': '#ea7a0d',
        'not_applicable': '#9c9c9c',
        'neutral': '#ffc302',
        'issue_resolved': '#0273ff',
        'not_rated': 'rgb(255,255,255, 0.3)'
    }
    judgment_str = str(judgment).lower().strip()
    return color_map.get(judgment_str, '#FFFFFF')