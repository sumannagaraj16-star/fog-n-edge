import streamlit as st
import boto3
import pandas as pd
from decimal import Decimal
import time

# ==========================
# 🔄 AUTO REFRESH (LIVE)
# ==========================
st.set_page_config(layout="wide")
st.title("📊 IoT Sensor Dashboard")
st.caption("🔄 Auto-refreshing every 5 seconds")

# ==========================
# AWS CONFIG
# ==========================
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SensorData')

# ==========================
# LOAD ALL DATA (FIXED)
# ==========================
def load_data():
    data = []
    response = table.scan()
    data.extend(response['Items'])

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    return pd.DataFrame(data)

df = load_data()

# ==========================
# CHECK DATA
# ==========================
if df.empty:
    st.warning("No data found in DynamoDB")
    st.stop()

# ==========================
# FIX DECIMAL → FLOAT
# ==========================
def convert_decimal(val):
    if isinstance(val, Decimal):
        return float(val)
    return val

df = df.map(convert_decimal)

# ==========================
# CONVERT TYPES
# ==========================
numeric_cols = ["temperature", "humidity", "air_quality", "light", "motion"]

for col in numeric_cols:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ==========================
# SORT BY TIME
# ==========================
if 'timestamp' in df:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

# ==========================
# SIDEBAR FILTER
# ==========================
st.sidebar.header("🔍 Filters")

device_filter = st.sidebar.selectbox(
    "Select Device",
    options=df['device_id'].unique()
)

filtered_df = df[df['device_id'] == device_filter]

# ==========================
# DEBUG (IMPORTANT)
# ==========================
st.write("📊 Total Records:", len(filtered_df))

# ==========================
# EMPTY CHECK
# ==========================
if filtered_df.empty:
    st.warning("No data for selected device")
    st.stop()

# ==========================
# SET INDEX
# ==========================
if 'timestamp' in filtered_df:
    filtered_df = filtered_df.set_index('timestamp')

# ==========================
# 📈 CHARTS (FIXED)
# ==========================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡 Temperature Trend")
    if 'temperature' in filtered_df:
        st.line_chart(filtered_df[['temperature']].dropna())

with col2:
    st.subheader("💧 Humidity Trend")
    if 'humidity' in filtered_df:
        st.line_chart(filtered_df[['humidity']].dropna())

col3, col4 = st.columns(2)

with col3:
    st.subheader("🌫 Air Quality")
    if 'air_quality' in filtered_df:
        st.line_chart(filtered_df[['air_quality']].dropna())

with col4:
    st.subheader("🚶 Motion Detection Count")
    if 'motion' in filtered_df:
        st.bar_chart(filtered_df['motion'].value_counts())

# ==========================
# ALERTS
# ==========================
st.subheader("🚨 Fog Alerts Summary")

if 'fog_alerts' in filtered_df:
    alerts = filtered_df['fog_alerts'].explode()
    st.bar_chart(alerts.value_counts())

# ==========================
# RAW DATA
# ==========================
st.subheader("📄 Raw Data")
st.dataframe(filtered_df.tail(10))

# ==========================
# AUTO REFRESH
# ==========================
time.sleep(5)
st.rerun()