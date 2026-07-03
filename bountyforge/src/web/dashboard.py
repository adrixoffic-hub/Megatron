import streamlit as st
import sqlite3
import pandas as pd
import json

st.set_page_config(layout="wide")
st.title("🛡️ BountyForge Dashboard")

conn = sqlite3.connect("bounty.db")
st.sidebar.header("Filters")
severity_filter = st.sidebar.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])

# Metrics
try:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(critical_count), SUM(high_count) FROM scans")
    crit, high = cursor.fetchone()
    crit = crit or 0
    high = high or 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scans", total_scans)
    col2.metric("Critical Vulns", crit)
    col3.metric("High Vulns", high)
except:
    st.warning("No data found. Run a scan first.")

# Findings Table
query = "SELECT * FROM findings"
if severity_filter != "All":
    query += f" WHERE severity='{severity_filter}'"
df = pd.read_sql_query(query, conn)
st.dataframe(df)

# Charts
vuln_counts = pd.read_sql_query("SELECT severity, COUNT(*) as count FROM findings GROUP BY severity", conn)
if not vuln_counts.empty:
    st.bar_chart(vuln_counts.set_index("severity"))
