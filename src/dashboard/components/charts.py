import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any

def create_oee_gauge(value: float, title: str = "OEE") -> go.Figure:
    """Create an OEE gauge chart."""
    # Convert to percentage if it's a decimal < 1
    display_value = value * 100 if value <= 1.0 else value
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=display_value,
        title={'text': title},
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#ffffff"},
            'steps': [
                {'range': [0, 60], 'color': "#e94560"},      # Red (Poor)
                {'range': [60, 85], 'color': "#f39c12"},     # Orange (Fair)
                {'range': [85, 100], 'color': "#2ecc71"}     # Green (Good)
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_spc_chart(dates: List[str], values: List[float], ucl: float, lcl: float, mean: float, title: str = "SPC Chart") -> go.Figure:
    """Create a Statistical Process Control (SPC) chart for yield trend."""
    df = pd.DataFrame({'Date': dates, 'Value': values})
    
    fig = go.Figure()
    
    # Value line
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Value'], mode='lines+markers', name='Value', line=dict(color='#3498db')))
    
    # Mean line
    fig.add_trace(go.Scatter(x=df['Date'], y=[mean]*len(df), mode='lines', name='Mean', line=dict(color='green', dash='dash')))
    
    # UCL / LCL
    fig.add_trace(go.Scatter(x=df['Date'], y=[ucl]*len(df), mode='lines', name='UCL', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=df['Date'], y=[lcl]*len(df), mode='lines', name='LCL', line=dict(color='red', dash='dot')))
    
    # Identify out of control points
    out_of_control = df[(df['Value'] > ucl) | (df['Value'] < lcl)]
    if not out_of_control.empty:
         fig.add_trace(go.Scatter(
             x=out_of_control['Date'], 
             y=out_of_control['Value'], 
             mode='markers', 
             name='Out of Control', 
             marker=dict(color='red', size=10, symbol='x')
         ))

    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_heatmap(suppliers: List[str], metrics: List[str], data: List[List[float]], title: str = "Performance Heatmap") -> go.Figure:
    """Create a heatmap for supplier performance."""
    fig = px.imshow(
        data,
        labels=dict(x="Metric", y="Supplier", color="Score"),
        x=metrics,
        y=suppliers,
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_pareto(categories: List[str], counts: List[int], title: str = "Defect Pareto Chart") -> go.Figure:
    """Create a Pareto chart for defects."""
    df = pd.DataFrame({'Category': categories, 'Count': counts})
    df = df.sort_values(by='Count', ascending=False)
    
    df['Cumulative_Pct'] = df['Count'].cumsum() / df['Count'].sum() * 100
    
    fig = go.Figure()
    
    # Bar chart for counts
    fig.add_trace(go.Bar(
        x=df['Category'], 
        y=df['Count'], 
        name='Count',
        marker_color='#3498db'
    ))
    
    # Line chart for cumulative percentage
    fig.add_trace(go.Scatter(
        x=df['Category'], 
        y=df['Cumulative_Pct'], 
        name='Cumulative %',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#e94560')
    ))
    
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        yaxis=dict(title='Count', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 105]),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(x=0.01, y=0.99)
    )
    return fig
