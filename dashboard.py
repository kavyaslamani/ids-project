import streamlit as st
import pandas as pd
import sqlite3
import time

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Adaptive Hybrid IDS",
    page_icon="🛡️",
    layout="wide"
)

DB_NAME = "ids.db"


# ============================================================
# LOAD DATA FROM SQLITE
# ============================================================

def load_data():

    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT
        id,
        timestamp,
        source_ip,
        destination_ip,
        protocol,
        attack,
        anomaly,
        confidence,
        reconstruction_error,
        risk
    FROM AttackHistory
    ORDER BY id DESC
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


# ============================================================
# LOAD LIVE DATA
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error(
        f"Database error: {e}"
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🛡️ Adaptive Hybrid Intrusion Detection System"
)

st.caption(
    "Real-Time Security Operations Center | "
    "AI-Powered Network Monitoring"
)

st.success(
    "● AI DETECTION ENGINE ONLINE"
)


# ============================================================
# EMPTY DATABASE
# ============================================================

if df.empty:

    st.warning(
        "⚠️ No network flows captured yet."
    )

    st.info(
        "Start FastAPI and live_capture.py "
        "to begin monitoring."
    )

    time.sleep(3)
    st.rerun()


# ============================================================
# DATA CLEANING
# ============================================================

df["anomaly"] = pd.to_numeric(
    df["anomaly"],
    errors="coerce"
).fillna(0).astype(int)

df["confidence"] = pd.to_numeric(
    df["confidence"],
    errors="coerce"
).fillna(0)

df["reconstruction_error"] = pd.to_numeric(
    df["reconstruction_error"],
    errors="coerce"
).fillna(0)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)


# ============================================================
# BASIC COUNTS
# ============================================================

total_flows = len(df)

anomalies = int(
    df["anomaly"].sum()
)

benign = len(
    df[
        (df["attack"] == "Benign") &
        (df["anomaly"] == 0)
    ]
)

system_errors = len(
    df[
        df["attack"] == "System Error"
    ]
)

unknown_attacks = len(
    df[
        df["attack"] == "Unknown Attack"
    ]
)

known_attacks = len(
    df[
        (df["attack"] != "Benign") &
        (df["attack"] != "Unknown Attack") &
        (df["attack"] != "System Error") &
        (df["anomaly"] == 1)
    ]
)

total_attacks = (
    known_attacks +
    unknown_attacks
)

high_risk = len(
    df[
        df["risk"] == "High"
    ]
)

medium_risk = len(
    df[
        df["risk"] == "Medium"
    ]
)

low_risk = len(
    df[
        df["risk"] == "Low"
    ]
)

unknown_risk = len(
    df[
        df["risk"] == "Unknown"
    ]
)


# ============================================================
# ANOMALY RATE
# ============================================================

if total_flows > 0:

    anomaly_rate = (
        anomalies /
        total_flows
    ) * 100

else:

    anomaly_rate = 0


# ============================================================
# NETWORK OVERVIEW
# ============================================================

st.subheader(
    "📡 Network Overview"
)

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "NETWORK FLOWS",
    f"{total_flows:,}"
)

c2.metric(
    "ANOMALIES",
    f"{anomalies:,}"
)

c3.metric(
    "BENIGN TRAFFIC",
    f"{benign:,}"
)

c4.metric(
    "TOTAL ATTACKS",
    f"{total_attacks:,}"
)


# ============================================================
# THREAT INTELLIGENCE
# ============================================================

st.subheader(
    "🚨 Threat Intelligence"
)

c1, c2, c3, c4, c5 = st.columns(5)


c1.metric(
    "KNOWN ATTACKS",
    f"{known_attacks:,}"
)

c2.metric(
    "UNKNOWN ATTACKS",
    f"{unknown_attacks:,}"
)

c3.metric(
    "HIGH RISK",
    f"{high_risk:,}"
)

c4.metric(
    "MEDIUM RISK",
    f"{medium_risk:,}"
)

c5.metric(
    "ANOMALY RATE",
    f"{anomaly_rate:.2f}%"
)


# ============================================================
# HIGH RISK ALERT
# ============================================================

if high_risk > 0:

    st.error(
        f"🚨 HIGH-RISK ACTIVITY DETECTED — "
        f"{high_risk:,} flows require attention."
    )

else:

    st.success(
        "✅ No high-risk activity detected."
    )


# ============================================================
# ATTACK INTELLIGENCE
# ============================================================

st.subheader(
    "🎯 Attack Intelligence"
)

attack_counts = (
    df["attack"]
    .value_counts()
)

st.bar_chart(
    attack_counts,
    use_container_width=True
)


# ============================================================
# RISK PROFILE
# ============================================================

st.subheader(
    "⚠️ Risk Profile"
)

risk_counts = pd.Series(
    {
        "High": high_risk,
        "Medium": medium_risk,
        "Low": low_risk,
        "Unknown": unknown_risk
    }
)

st.bar_chart(
    risk_counts,
    use_container_width=True
)


# ============================================================
# RECONSTRUCTION ERROR
# ============================================================

st.subheader(
    "🧠 Autoencoder Reconstruction Error"
)

error_df = df[
    [
        "timestamp",
        "reconstruction_error"
    ]
].copy()

error_df = error_df.dropna(
    subset=["timestamp"]
)

error_df = error_df.sort_values(
    "timestamp"
)

# Show only latest 200 flows
# so the graph remains readable

error_df = error_df.tail(
    200
)

error_df = error_df.set_index(
    "timestamp"
)

st.line_chart(
    error_df,
    use_container_width=True
)


# ============================================================
# COMPLETE DETECTION SUMMARY
# ============================================================

st.subheader(
    "📊 Complete Detection Summary"
)

summary = pd.DataFrame(
    {
        "Metric": [
            "Total Network Flows",
            "Anomalies Detected",
            "Benign Traffic",
            "Total Attacks",
            "Known Attacks",
            "Unknown Attacks",
            "High Risk",
            "Medium Risk",
            "Low Risk",
            "System Errors"
        ],
        "Count": [
            total_flows,
            anomalies,
            benign,
            total_attacks,
            known_attacks,
            unknown_attacks,
            high_risk,
            medium_risk,
            low_risk,
            system_errors
        ]
    }
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# RECENT SECURITY EVENTS
# ============================================================

st.subheader(
    "🔎 Recent Security Events"
)

recent_columns = [
    "timestamp",
    "source_ip",
    "destination_ip",
    "protocol",
    "attack",
    "anomaly",
    "confidence",
    "reconstruction_error",
    "risk"
]

recent = df[
    recent_columns
].head(25).copy()


recent["confidence"] = (
    recent["confidence"] * 100
).round(2).astype(str) + "%"


recent["reconstruction_error"] = (
    recent["reconstruction_error"]
    .round(6)
)


st.dataframe(
    recent,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# HYBRID AI ENGINE STATUS
# ============================================================

st.subheader(
    "🧠 Hybrid AI Detection Engine"
)

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        """
        ✓ **78 CICIDS-style network traffic features**

        ✓ **Autoencoder-based anomaly detection**

        ✓ **DNN attack classification**

        ✓ **Known attack identification**

        ✓ **Unknown anomaly detection**
        """
    )


with col2:

    st.markdown(
        """
        ✓ **Hybrid anomaly + classification decision**

        ✓ **Reconstruction-error-based risk assessment**

        ✓ **Persistent SQLite attack history**

        ✓ **Real-time network-flow monitoring**

        ✓ **Automatic dashboard refresh**
        """
    )


# ============================================================
# DATABASE STATUS
# ============================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "DATABASE RECORDS",
        f"{total_flows:,}"
    )

with col2:

    if total_flows > 0:

        latest_time = df["timestamp"].max()

        st.metric(
            "LATEST EVENT",
            latest_time.strftime(
                "%H:%M:%S"
            )
        )

with col3:

    st.metric(
        "REFRESH RATE",
        "3 seconds"
    )


# ============================================================
# AUTO REFRESH
# ============================================================

time.sleep(3)

st.rerun()