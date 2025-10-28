import streamlit as st
import sqlite3
import pandas as pd
import json
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

DB_FILE = 'telemetry.db'
THRESH_FILE = 'thresholds.json'
metrics = ['temperature', 'battery', 'signal', 'velocity']

def fetch_latest_packets(limit=50):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"""
        SELECT * FROM telemetry ORDER BY time DESC LIMIT {limit}
    """, conn)
    conn.close()
    return df

def load_thresholds():
    with open(THRESH_FILE, 'r') as f:
        return json.load(f)

def in_range(value, range_tuple):
    """Check if value is within a given range (inclusive)."""
    return range_tuple[0] <= value <= range_tuple[1]

st.set_page_config(layout="wide")
st.title("🚀 Telemetry Dashboard")

# Auto-refresh every 5000ms = 5 seconds
count = st_autorefresh(interval=5000, limit=None, key="datarefresh")

# Slider for number of packets
limit = st.slider("Number of packets to display", 10, 200, 50, step=10)

data = fetch_latest_packets(limit=limit)
thresholds = load_thresholds()

if not data.empty:
    data['time'] = pd.to_datetime(data['time'])
    data = data.sort_values('time')
    cols = st.columns(2)

    for i, metric in enumerate(metrics):
        col = cols[i % 2]
        chart_data = data.set_index('time')[[metric]]
        latest = chart_data.iloc[-1][metric]
        t = thresholds[metric]

        # Display alerts
        if in_range(latest, t["red"]):
            color = "red"
            st.error(f"🚨 {metric.capitalize()} out of range ({latest}) — currently {color.upper()}")
        elif in_range(latest, t["yellow"]):
            color = "yellow"
            st.warning(f"⚠️ {metric.capitalize()} out of range ({latest}) — currently {color.upper()}")
        else:
            color = "green"

        # Reset index for Plotly
        chart_data_reset = chart_data.reset_index()

        # Create Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_data_reset['time'],
            y=chart_data_reset[metric],
            mode='lines+markers',
            line=dict(color='blue'),
            name=metric
        ))

        # Add background threshold bands
        shapes = []
        if "red" in t:
            shapes.append(dict(
                type="rect",
                xref="paper", x0=0, x1=1,
                yref="y", y0=t['red'][0], y1=t['red'][1],
                fillcolor="red", opacity=0.2, layer="below", line_width=0
            ))
        if "yellow" in t:
            shapes.append(dict(
                type="rect",
                xref="paper", x0=0, x1=1,
                yref="y", y0=t['yellow'][0], y1=t['yellow'][1],
                fillcolor="yellow", opacity=0.2, layer="below", line_width=0
            ))
        fig.update_layout(shapes=shapes, title=f"{metric.capitalize()} over time",
                          xaxis_title="Time", yaxis_title=metric)

        # Display metric and chart
        col.subheader(f"{metric.capitalize()} over time")
        col.metric(f"Latest {metric}", f"{latest}")
        col.plotly_chart(fig, use_container_width=True)

else:
    st.write("No telemetry data found yet.")

st.write(f"Auto refresh count: {count}")
