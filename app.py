import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh

DB_FILE = 'telemetry.db'

def fetch_latest_packets(limit=50):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"""
        SELECT * FROM telemetry ORDER BY time DESC LIMIT {limit}
    """, conn)
    conn.close()
    return df

st.title("🚀 Telemetry Dashboard")

# Auto-refresh every 5000ms = 5 seconds
count = st_autorefresh(interval=5000, limit=None, key="datarefresh")

data = fetch_latest_packets()
if not data.empty:
    data['time'] = pd.to_datetime(data['time'])
    data['time'] = pd.to_datetime(data['time'])
    data = data.sort_values('time')

    st.line_chart(data.set_index('time')[['temperature', 'battery', 'signal', 'velocity']])
else:
    st.write("No telemetry data found yet.")

st.write(f"Auto refresh count: {count}")
