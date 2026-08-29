import streamlit as st
import pandas as pd
import sqlite3
import time
import ipaddress
import requests
import plotly.graph_objects as go

# ============================================================
# PAGE
# ============================================================
st.set_page_config(
    page_title="AHIDS // GLOBAL SOC",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_NAME = "ids.db"

# ============================================================
# REAL SOC THEME
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at 85% 10%, rgba(255,72,0,.07), transparent 28%),
        radial-gradient(circle at 10% 90%, rgba(255,190,0,.035), transparent 25%),
        #07090b;
    color: #d8dde2;
}
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
h1, h2, h3 {
    letter-spacing: .02em;
}
h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.55rem !important;
    color: #f2f4f5;
}
h2, h3 {
    color: #cfd4d8;
}
[data-testid="stMetric"] {
    background: #0c1013;
    border: 1px solid #22282d;
    border-radius: 5px;
    padding: 12px 14px;
}
[data-testid="stMetricLabel"] {
    color: #737d84 !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .67rem !important;
    letter-spacing: .08em;
}
[data-testid="stMetricValue"] {
    color: #e8ecef !important;
    font-family: 'IBM Plex Mono', monospace;
}
.soc-header {
    border-bottom: 1px solid #272d31;
    padding-bottom: 12px;
    margin-bottom: 16px;
}
.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #ff5a36;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .76rem;
    letter-spacing: .08em;
}
.dot {
    width: 8px;
    height: 8px;
    background: #ff4b23;
    border-radius: 50%;
    box-shadow: 0 0 12px rgba(255,75,35,.75);
}
.panel {
    background: #0a0e11;
    border: 1px solid #22282d;
    border-radius: 5px;
    padding: 14px;
    margin-bottom: 14px;
}
.panel-title {
    font-family: 'IBM Plex Mono', monospace;
    color: #7f8990;
    font-size: .72rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.alert-high {
    border-left: 3px solid #ff4b23;
    background: rgba(255,75,35,.055);
    padding: 10px 13px;
    color: #ff8b70;
    font-family: 'IBM Plex Mono', monospace;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #22282d;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================
@st.cache_data(ttl=3)
def load_data():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT id, timestamp, source_ip, destination_ip, protocol,
           attack, anomaly, confidence, reconstruction_error, risk
    FROM AttackHistory
    ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if df.empty:
    st.warning("No network flows captured yet. Start the live IDS pipeline.")
    time.sleep(3)
    st.rerun()

# ============================================================
# CLEAN
# ============================================================
df["anomaly"] = pd.to_numeric(df["anomaly"], errors="coerce").fillna(0).astype(int)
df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0)
df["reconstruction_error"] = pd.to_numeric(
    df["reconstruction_error"], errors="coerce"
).fillna(0)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

total_flows = len(df)
anomalies = int(df["anomaly"].sum())
benign = len(df[(df["attack"] == "Benign") & (df["anomaly"] == 0)])
unknown_attacks = len(df[df["attack"] == "Unknown Attack"])
known_attacks = len(df[
    (df["attack"] != "Benign") &
    (df["attack"] != "Unknown Attack") &
    (df["attack"] != "System Error") &
    (df["anomaly"] == 1)
])
total_attacks = known_attacks + unknown_attacks
high_risk = len(df[df["risk"] == "High"])
medium_risk = len(df[df["risk"] == "Medium"])
low_risk = len(df[df["risk"] == "Low"])
unknown_risk = len(df[df["risk"] == "Unknown"])
system_errors = len(df[df["attack"] == "System Error"])
anomaly_rate = (anomalies / total_flows * 100) if total_flows else 0

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="soc-header">
    <h1>ADAPTIVE HYBRID INTRUSION DETECTION SYSTEM</h1>
    <div class="status"><span class="dot"></span> AI DETECTION ENGINE // LIVE</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TOP METRICS
# ============================================================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("NETWORK FLOWS", f"{total_flows:,}")
c2.metric("ANOMALIES", f"{anomalies:,}")
c3.metric("KNOWN ATTACKS", f"{known_attacks:,}")
c4.metric("UNKNOWN ATTACKS", f"{unknown_attacks:,}")
c5.metric("ANOMALY RATE", f"{anomaly_rate:.2f}%")

if high_risk:
    st.markdown(
        f'<div class="alert-high">▲ HIGH-RISK ACTIVITY // {high_risk:,} FLOWS REQUIRE ATTENTION</div>',
        unsafe_allow_html=True
    )

st.write("")

# ============================================================
# GLOBAL THREAT MAP
# ============================================================
st.markdown('<div class="panel-title">GLOBAL THREAT MAP // SOURCE → DESTINATION</div>',
            unsafe_allow_html=True)

# Private/reserved addresses cannot be truthfully geolocated.
def is_public_ip(value):
    try:
        ip = ipaddress.ip_address(str(value))
        return not (
            ip.is_private or ip.is_loopback or ip.is_reserved or
            ip.is_multicast or ip.is_link_local or ip.is_unspecified
        )
    except ValueError:
        return False

@st.cache_data(ttl=3600, show_spinner=False)
def geolocate_ip(ip):
    if not is_public_ip(ip):
        return {
            "lat": None, "lon": None, "city": "LOCAL / PRIVATE",
            "country": "Local network", "ok": False
        }
    try:
        r = requests.get(
            f"https://ipwho.is/{ip}",
            timeout=2.5,
            headers={"User-Agent": "AHIDS-SOC/1.0"}
        )
        data = r.json()
        if data.get("success") is False:
            return {"lat": None, "lon": None, "city": "Unknown",
                    "country": "Unknown", "ok": False}
        return {
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
            "city": data.get("city") or "Unknown",
            "country": data.get("country") or "Unknown",
            "ok": True,
        }
    except Exception:
        return {"lat": None, "lon": None, "city": "Unknown",
                "country": "Unknown", "ok": False}

# Only geolocate the newest distinct public IPs to keep the dashboard fast.
map_events = df.head(80).copy()
ips = pd.unique(
    pd.concat([map_events["source_ip"], map_events["destination_ip"]], ignore_index=True)
)
ips = [str(x) for x in ips if is_public_ip(x)][:40]

geo = {ip: geolocate_ip(ip) for ip in ips}

# Build public source/destination points and attack lines.
points = []
lines_lat = []
lines_lon = []
line_meta = []

for _, row in map_events.iterrows():
    src = str(row["source_ip"])
    dst = str(row["destination_ip"])

    gs = geo.get(src)
    gd = geo.get(dst)

    if gs and gs["ok"] and gs["lat"] is not None:
        points.append({
            "ip": src,
            "lat": gs["lat"],
            "lon": gs["lon"],
            "city": gs["city"],
            "country": gs["country"],
            "role": "SOURCE",
            "attack": row["attack"],
            "risk": row["risk"],
            "error": row["reconstruction_error"],
        })

    if gd and gd["ok"] and gd["lat"] is not None:
        points.append({
            "ip": dst,
            "lat": gd["lat"],
            "lon": gd["lon"],
            "city": gd["city"],
            "country": gd["country"],
            "role": "DESTINATION",
            "attack": row["attack"],
            "risk": row["risk"],
            "error": row["reconstruction_error"],
        })

    if gs and gd and gs["ok"] and gd["ok"] and gs["lat"] is not None and gd["lat"] is not None:
        lines_lat.extend([gs["lat"], gd["lat"], None])
        lines_lon.extend([gs["lon"], gd["lon"], None])
        line_meta.append(
            f"{src} → {dst} | {row['attack']} | {row['risk']}"
        )

fig = go.Figure()

if lines_lat:
    fig.add_trace(go.Scattergeo(
        lat=lines_lat,
        lon=lines_lon,
        mode="lines",
        line=dict(width=1, color="#ff4b23"),
        opacity=.35,
        hoverinfo="skip",
        name="Threat path"
    ))

if points:
    p = pd.DataFrame(points).drop_duplicates(subset=["ip", "role"])
    fig.add_trace(go.Scattergeo(
        lat=p["lat"],
        lon=p["lon"],
        mode="markers",
        marker=dict(
            size=8,
            color="#ff5a36",
            line=dict(width=1, color="#ffb199"),
            opacity=.9
        ),
        customdata=p[["ip", "city", "country", "role", "attack", "risk", "error"]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[3]}<br>"
            "%{customdata[1]}, %{customdata[2]}<br>"
            "Attack: %{customdata[4]}<br>"
            "Risk: %{customdata[5]}<br>"
            "Reconstruction error: %{customdata[6]:.3f}"
            "<extra></extra>"
        ),
        name="Observed IP"
    ))

fig.update_geos(
    projection_type="orthographic",
    showland=True,
    landcolor="#151a1e",
    showocean=True,
    oceancolor="#050709",
    showcountries=True,
    countrycolor="#30363b",
    showcoastlines=True,
    coastlinecolor="#596168",
    showframe=False,
    bgcolor="#07090b",
)
fig.update_layout(
    height=620,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="#07090b",
    plot_bgcolor="#07090b",
    font=dict(color="#d8dde2"),
    legend=dict(
        bgcolor="rgba(7,9,11,.75)",
        bordercolor="#30363b",
        borderwidth=1
    ),
)

if points:
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": False
    })
else:
    st.info(
        "No public IPs with geolocation available in the latest flows. "
        "Private addresses such as 192.168.x.x remain labeled LOCAL / PRIVATE."
    )

# ============================================================
# LIVE CONNECTION FEED
# ============================================================
left, right = st.columns([1.4, 1])

with left:
    st.markdown('<div class="panel-title">LIVE CONNECTION FEED</div>',
                unsafe_allow_html=True)
    recent = df.head(15)[[
        "timestamp", "source_ip", "destination_ip",
        "protocol", "attack", "risk", "reconstruction_error"
    ]].copy()
    recent["timestamp"] = recent["timestamp"].dt.strftime("%H:%M:%S")
    recent["reconstruction_error"] = recent["reconstruction_error"].round(3)
    st.dataframe(recent, use_container_width=True, hide_index=True)

with right:
    st.markdown('<div class="panel-title">THREAT PROFILE</div>',
                unsafe_allow_html=True)
    threat = pd.Series({
        "UNKNOWN": unknown_attacks,
        "KNOWN": known_attacks,
        "BENIGN": benign,
    })
    st.bar_chart(threat, height=260, use_container_width=True)

# ============================================================
# RECONSTRUCTION ERROR
# ============================================================
st.markdown('<div class="panel-title">AUTOENCODER // RECONSTRUCTION ERROR</div>',
            unsafe_allow_html=True)
error_df = df[["timestamp", "reconstruction_error"]].dropna().sort_values("timestamp").tail(200)
error_df = error_df.set_index("timestamp")
st.line_chart(error_df, use_container_width=True, height=280)

# ============================================================
# RISK / ATTACK COUNTS
# ============================================================
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="panel-title">ATTACK INTELLIGENCE</div>',
                unsafe_allow_html=True)
    st.bar_chart(df["attack"].value_counts(), use_container_width=True, height=300)

with c2:
    st.markdown('<div class="panel-title">RISK PROFILE</div>',
                unsafe_allow_html=True)
    st.bar_chart(pd.Series({
        "HIGH": high_risk,
        "MEDIUM": medium_risk,
        "LOW": low_risk,
        "UNKNOWN": unknown_risk,
    }), use_container_width=True, height=300)

# ============================================================
# ENGINE / DATABASE
# ============================================================
st.markdown('<div class="panel-title">HYBRID AI ENGINE STATUS</div>',
            unsafe_allow_html=True)

e1, e2, e3 = st.columns(3)
e1.metric("FEATURES", "78")
e2.metric("DATABASE RECORDS", f"{total_flows:,}")
e3.metric("REFRESH", "3 SEC")

st.markdown("""
<div class="panel">
<div class="panel-title">DETECTION PIPELINE</div>
<code>
LIVE PACKETS → FLOW BUILDER → 78 FEATURES → SCALER → AUTOENCODER
→ RECONSTRUCTION ERROR → DNN CLASSIFIER → HYBRID DECISION
→ RISK ASSESSMENT → SQLITE → SOC DASHBOARD
</code>
</div>
""", unsafe_allow_html=True)

st.caption(
    "IP locations are approximate geolocation data for public IP addresses. "
    "Private/local addresses are not assigned a fabricated geographic location."
)

time.sleep(3)
st.rerun()
