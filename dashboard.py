
import streamlit as st
import requests
import random
import time
import pandas as pd

st.set_page_config(
    page_title="Adaptive Hybrid IDS",
    layout="wide"
)

# ---------------------------------
# TITLE
# ---------------------------------

st.title("🔐 Adaptive Hybrid Intrusion Detection System — Live SOC Monitoring")

st.markdown("## ⚡ SYSTEM STATUS")
st.success("🚨 LIVE NETWORK MONITORING ACTIVE")

# ---------------------------------
# SESSION STATE
# ---------------------------------

if "traffic" not in st.session_state:
    st.session_state.traffic = 0

if "anomalies" not in st.session_state:
    st.session_state.anomalies = 0

if "high_risk" not in st.session_state:
    st.session_state.high_risk = 0

if "critical" not in st.session_state:
    st.session_state.critical = 0

if "incident_feed" not in st.session_state:
    st.session_state.incident_feed = []

# ---------------------------------
# GENERATE SAMPLE FEATURES
# ---------------------------------

features = [

    random.randint(1, 500),
    random.randint(100, 5000),
    random.uniform(0.1, 5),
    random.uniform(10, 500),
    random.uniform(1, 100),
    random.randint(1, 17),
    random.randint(60, 1500),
    random.randint(0, 20),
    random.randint(0, 20),
    random.uniform(0, 5)

]

# ---------------------------------
# API CALL
# ---------------------------------

try:

    response = requests.post(

        "http://127.0.0.1:8000/predict",

        json={"features": features}

    )

    result = response.json()

    prediction = result["prediction"]

    risk = result["risk_level"]

    score = result["anomaly_score"]

except:

    prediction = "API Offline"

    risk = "Unknown"

    score = 0

# ---------------------------------
# UPDATE COUNTERS
# ---------------------------------

st.session_state.traffic += random.randint(5, 20)

if prediction != "Normal Traffic":

    st.session_state.anomalies += 1

if risk == "High":

    st.session_state.high_risk += 1

if risk == "Critical":

    st.session_state.critical += 1

# ---------------------------------
# INCIDENT FEED
# ---------------------------------

incident = f"""
🚨 Attack: {prediction}

⚠️ Risk: {risk}

📈 Score: {score}
"""

st.session_state.incident_feed.append(incident)

# ---------------------------------
# METRICS
# ---------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("🌐 Traffic", st.session_state.traffic)

col2.metric("🧠 Anomalies", st.session_state.anomalies)

col3.metric("⚠️ High Risk", st.session_state.high_risk)

col4.metric("🔥 Critical", st.session_state.critical)

# ---------------------------------
# THREAT LANDSCAPE
# ---------------------------------

st.subheader("📊 Threat Landscape")

threat_data = pd.DataFrame({

    "Type": [

        "Normal",
        "Anomaly",
        "High Risk",
        "Critical"

    ],

    "Count": [

        st.session_state.traffic,
        st.session_state.anomalies,
        st.session_state.high_risk,
        st.session_state.critical

    ]

})

st.bar_chart(
    threat_data.set_index("Type")
)

# ---------------------------------
# AI SIGNAL
# ---------------------------------

st.subheader("📈 AI Threat Detection Signal (Reconstruction Error)")

signal = [random.uniform(0, score + 1) for _ in range(50)]

st.line_chart(signal)

# ---------------------------------
# INCIDENT FEED
# ---------------------------------

st.subheader("📝 LIVE INCIDENT FEED")

for item in st.session_state.incident_feed[-10:]:

    st.error(item)

# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")

st.success(
    "⚡ SOC ACTIVE | LIVE TRAFFIC MONITORING ENABLED"
)

st.markdown("## 🚨 AI ATTACK CLASSIFICATION")

# ---------------------------------
# AUTO REFRESH
# ---------------------------------

time.sleep(2)

st.rerun()
