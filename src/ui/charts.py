import plotly.graph_objects as go
import streamlit as st


def render_bmi_gauge(bmi: float, key: str | None = None) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=bmi,
            title={"text": "BMI"},
            gauge={
                "axis": {"range": [10, 50]},
                "bar": {"color": "#2c3e50"},
                "steps": [
                    {"range": [10, 18.5], "color": "#3498db"},
                    {"range": [18.5, 25], "color": "#2ecc71"},
                    {"range": [25, 30], "color": "#f39c12"},
                    {"range": [30, 35], "color": "#e67e22"},
                    {"range": [35, 40], "color": "#e74c3c"},
                    {"range": [40, 50], "color": "#c0392b"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.8,
                    "value": bmi,
                },
            },
        )
    )
    fig.update_layout(height=280, margin=dict(t=60, b=0, l=30, r=30))
    st.plotly_chart(fig, use_container_width=True, key=key)
