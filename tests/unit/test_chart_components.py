import pytest
from src.dashboard.components.charts import create_oee_gauge, create_spc_chart, create_heatmap, create_pareto
import plotly.graph_objects as go

def test_create_oee_gauge():
    fig = create_oee_gauge(0.85)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == 'indicator'
    assert fig.data[0].value == 85.0

def test_create_spc_chart():
    dates = ["2023-01-01", "2023-01-02"]
    values = [95.0, 96.0]
    fig = create_spc_chart(dates, values, ucl=99.0, lcl=90.0, mean=94.5)
    assert isinstance(fig, go.Figure)
    # At least Value, Mean, UCL, LCL traces
    assert len(fig.data) >= 4 

def test_create_heatmap():
    suppliers = ["A", "B"]
    metrics = ["OEE", "Yield"]
    data = [[80, 90], [85, 95]]
    fig = create_heatmap(suppliers, metrics, data)
    assert isinstance(fig, go.Figure)
    # Plotly express heatmap creates an Image or Heatmap trace
    assert fig.data[0].type in ['heatmap', 'image']

def test_create_pareto():
    categories = ["Scratch", "Dent"]
    counts = [10, 5]
    fig = create_pareto(categories, counts)
    assert isinstance(fig, go.Figure)
    # Should have a bar trace and a line trace
    assert len(fig.data) == 2
    assert fig.data[0].type == 'bar'
    assert fig.data[1].type == 'scatter'
