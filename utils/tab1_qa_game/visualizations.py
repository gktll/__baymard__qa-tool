
# visualizations.py

import plotly.graph_objects as go
from ..helpers import get_judgment_color

def create_pills_visualization(input_df, title=""):
    df = input_df.copy()
    df = df.loc[df['Judgement'].notna()].reset_index(drop=True)
    
    total_pills = len(df)
    pills_per_row = 50  
    num_rows = (total_pills + pills_per_row - 1) // pills_per_row  

    dot_size = 15
    dot_spacing_x = dot_size * 0.5  
    dot_spacing_y = dot_size * 2    

    # Build hover text for each pill.
    df['hover_text'] = (
        'Citation: ' + df['Citation Code: Platform-Specific'].fillna('') + '<br>' +
        'Title: ' + df['Title'].fillna('') + '<br>' +
        'Case Study: ' + df['Case Study Title'].fillna('') + '<br>' +
        'Judgment: ' + df['Judgement'].fillna('') + '<br>' +
        'Theme: ' + df['Catalog Theme Title'].fillna('') + '<br>' +
        'Topic: ' + df['Catalog Topic Title'].fillna('')
    )

    # Precompute arrays for a single trace.
    x_positions, y_positions, colors, hover_texts, links = [], [], [], [], []
    for i, (_, row) in enumerate(df.iterrows()):
        x_positions.append((i % pills_per_row) * dot_spacing_x)
        y_positions.append(-(i // pills_per_row) * dot_spacing_y)
        colors.append(get_judgment_color(row['Judgement']))
        hover_texts.append(row['hover_text'])
        links.append(row['Citation Code: Platform-Specific'])
    
    fig = go.Figure(data=go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers',
        marker=dict(
            size=dot_size,
            color=colors,
            line=dict(color='black', width=1)
        ),
        text=hover_texts,
        hoverinfo='text',
        customdata=links,  # Each pill carries its linking info
        showlegend=False
    ))
    
    # Update layout to remove padding and enable responsiveness.
    fig.update_layout(
        title=title,
        autosize=True,
        showlegend=False,
        plot_bgcolor='rgb(15,17,22)',
        paper_bgcolor='rgb(15,17,22)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-dot_spacing_x, pills_per_row * dot_spacing_x]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-num_rows * dot_spacing_y, dot_spacing_y]
        ),
        clickmode='event+select',
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",  
            font=dict(color="black")  
        )
    )
    return fig
