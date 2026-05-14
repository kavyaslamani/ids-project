import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Cyber War Room", layout="wide")

# ===============================
# 🎨 ADVANCED UI THEME (GLASS + NEON)
# ===============================
st.markdown("""
<style>

body {
    background-color: #070b14;
}

/* MAIN APP BACKGROUND */
.main {
    background: radial-gradient(circle at top, #0d1224, #070b14);
}

/* TITLE */
h1 {
    text-align: center;
    color: #00f5ff;
    font-size: 40px;
    font-weight: 900;
    letter-spacing: 2px;
}

/* SUBTITLE */
h3 {
    color: #b388ff;
}

/* GLASS CARDS */
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(0, 245, 255, 0.2);
    padding: 15px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.1);
}

/* SUCCESS */
.stSuccess {
    background: rgba(0, 255, 136, 0.1);
    border-left: 5px solid #00ff88;
}

/* WARNING */
.stWarning {
    background: rgba(255, 179, 0, 0.1);
    border-left: 5px solid #ffb300;
}

/* ERROR */
.stError {
    background: rgba(255, 0, 76, 0.1);
    border-left: 5px solid #ff004c;
}

/* INFO */
.stInfo {
    background: rgba(0, 195, 255, 0.1);
    border-left: 5px solid #00c3ff;
}

/* DATAFRAME */
.stDataFrame {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# TITLE (WAR ROOM STYLE)
# ===============================
st.title("🛡️ CYBER WAR ROOM")
st.markdown("### 🔐 Adaptive Hybrid Intrusion Detection System — Live SOC Monitoring")

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("attack_logs.csv").dropna()

# ===============================
# METRICS
# ===============================
traffic = len(df)
anomalies = df["anomaly"].sum()
high_alerts = len(df[df["severity"] == "HIGH"])
critical_alerts = len(df[df["severity"] == "CRITICAL"])

# ===============================
# ALERT BANNER (DYNAMIC UX)
# ===============================
st.markdown("## ⚡ SYSTEM STATUS")

if critical_alerts > 0:
    st.error("🚨 CRITICAL BREACH DETECTED — SYSTEM UNDER ATTACK")
elif high_alerts > 0:
    st.warning("⚠️ SUSPICIOUS ACTIVITY DETECTED — MONITORING ACTIVE")
elif anomalies > 0:
    st.info("🟡 ANOMALOUS TRAFFIC DETECTED — ANALYZING PATTERN")
else:
    st.success("🟢 NETWORK SECURE — NO THREATS DETECTED")

st.markdown("---")

# ===============================
# KPI DASHBOARD (MODERN GRID)
# ===============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("🌐 Traffic", traffic)
col2.metric("🧠 Anomalies", anomalies)
col3.metric("⚠️ High Risk", high_alerts)
col4.metric("🔥 Critical", critical_alerts)

st.markdown("---")

# ===============================
# VISUAL SECTION (2-COLUMN LAYOUT)
# ===============================
left, right = st.columns(2)

with left:
    st.subheader("📊 Threat Landscape")
    fig1 = px.histogram(
        df,
        x="attack_name",
        color="severity",
        color_discrete_sequence=["#00f5ff", "#ffb300", "#ff004c"]
    )
    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("🚨 Security Breakdown")
    fig2 = px.pie(
        df,
        names="severity",
        color_discrete_sequence=["#00ff88", "#ffb300", "#ff004c"]
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ===============================
# AI SIGNAL VIEW (CORE ML VISUAL)
# ===============================
st.subheader("📈 AI Threat Detection Signal (Reconstruction Error)")

fig3 = px.line(
    df,
    y="reconstruction_error",
    markers=True,
    line_shape="spline"
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ===============================
# LIVE INCIDENT FEED (SOC STYLE)
# ===============================
st.subheader("📝 LIVE INCIDENT FEED")

st.dataframe(
    df.tail(15)[["timestamp", "attack_name", "severity", "anomaly", "reconstruction_error"]],
    use_container_width=True
)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown("⚡ SOC ACTIVE | AI-POWERED THREAT DETECTION | REAL-TIME MONITORING ENABLED")