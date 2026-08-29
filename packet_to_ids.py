
from scapy.all import sniff, IP, TCP
from collections import defaultdict
import requests
import time

API_URL = "http://127.0.0.1:8000/predict"

flows = defaultdict(lambda: {
    "start": time.time(),
    "packets": 0,
    "bytes": 0,
    "syn": 0,
    "ack": 0
})

# -----------------------------
# Extract Flow Features
# -----------------------------

def extract(packet):

    if not packet.haslayer(IP):
        return None

    ip = packet[IP]

    src = ip.src
    dst = ip.dst
    proto = ip.proto

    pkt_len = len(packet)

    key = (src, dst, proto)

    flow = flows[key]

    flow["packets"] += 1
    flow["bytes"] += pkt_len

    if packet.haslayer(TCP):

        flags = str(packet[TCP].flags)

        if "S" in flags:
            flow["syn"] += 1

        if "A" in flags:
            flow["ack"] += 1

    duration = time.time() - flow["start"]

    features = [

        flow["packets"],
        flow["bytes"],
        duration,
        flow["bytes"] / (duration + 0.001),
        flow["packets"] / (duration + 0.001),
        proto,
        pkt_len,
        flow["syn"],
        flow["ack"],
        flow["syn"] / (flow["ack"] + 0.001)

    ]

    return features

# -----------------------------
# Send Features to FastAPI
# -----------------------------

def send(features, packet):

    try:

        payload = {
            "features": features,

            "src_ip": packet[IP].src,
            "dst_ip": packet[IP].dst,
            "protocol": packet[IP].proto
        }

        response = requests.post(
            API_URL,
            json=payload
        )

        result = response.json()

        print("\n==========================")
        print("LIVE IDS DETECTION")
        print("==========================")
        print("Source IP :", payload["src_ip"])
        print("Destination IP :", payload["dst_ip"])
        print("Prediction :", result["attack"])
        print("Risk :", result["risk"])
        print("Confidence :", result["confidence"])
        print("Reconstruction Error :", result["reconstruction_error"])

    except Exception as e:

        print("API ERROR:", e)
# -----------------------------
# Process Packets
# -----------------------------

def process(packet):

    features = extract(packet)

    if features:
        send(features, packet)

# -----------------------------
# Start IDS
# -----------------------------

print("🔐 REAL-TIME IDS STARTED")
print("📡 Monitoring Live Network Traffic...\n")

sniff(

    prn=process,

    store=False

)
