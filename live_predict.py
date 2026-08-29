import joblib
import pandas as pd
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
import requests
from flow_builder_v2 import update_flow, flows

API_URL = "http://127.0.0.1:8000/predict"

# Minimum packets before asking the AI model to predict
MIN_PACKETS = 5

# Don't repeatedly predict the same flow too quickly
PREDICTION_INTERVAL = 2.0

last_prediction = {}


def packet_to_dict(packet):

    if not packet.haslayer(IP):
        return None

    ip = packet[IP]

    src_port = 0
    dst_port = 0
    tcp_flags = 0
    header_length = ip.ihl * 4 if ip.ihl else 20

    tcp_window = 0
    tcp_seq = 0
    tcp_ack = 0

    if packet.haslayer(TCP):

        tcp = packet[TCP]

        src_port = int(tcp.sport)
        dst_port = int(tcp.dport)

        tcp_flags = int(tcp.flags)

        tcp_window = int(tcp.window)

        tcp_seq = int(tcp.seq)

        tcp_ack = int(tcp.ack)

        header_length = (
            ip.ihl * 4 +
            tcp.dataofs * 4
        )

    elif packet.haslayer(UDP):

        udp = packet[UDP]

        src_port = int(udp.sport)
        dst_port = int(udp.dport)

        header_length = ip.ihl * 4 + 8

    return {

        "src_ip": ip.src,
        "dst_ip": ip.dst,

        "src_port": src_port,
        "dst_port": dst_port,

        "protocol": int(ip.proto),

        "packet_length": len(ip),

        "tcp_flags": tcp_flags,

        "header_length": header_length,

        "tcp_window": tcp_window,

        "tcp_seq": tcp_seq,

        "tcp_ack": tcp_ack
    }


def process(packet):

    packet_data = packet_to_dict(packet)

    if packet_data is None:
        return

    try:

        # -----------------------------------------
        # BUILD / UPDATE FLOW
        # -----------------------------------------

        features = update_flow(packet_data)

        if features is None:
            return

        features = list(features)
        
                # =========================================
        # SCALER DIAGNOSTIC
        # =========================================

        scaler = joblib.load("models/scaler_combined.pkl")

        df_live = pd.DataFrame(
            [features],
            columns=scaler.feature_names_in_
        )

        scaled = scaler.transform(df_live)

        diagnostic = pd.DataFrame({
            "Feature": scaler.feature_names_in_,
            "Raw": features,
            "Mean": scaler.mean_,
            "Scale": scaler.scale_,
            "Scaled": scaled[0],
            "AbsScaled": np.abs(scaled[0])
        }).sort_values(
            "AbsScaled",
            ascending=False
        )

        print("\nTOP 15 SCALED FEATURES:")
        print(
            diagnostic.head(15).to_string(index=False)
        )

        # -----------------------------------------
        # IDENTIFY FLOW
        # -----------------------------------------

        forward_key = (
            packet_data["src_ip"],
            packet_data["dst_ip"],
            packet_data["src_port"],
            packet_data["dst_port"],
            packet_data["protocol"]
        )

        reverse_key = (
            packet_data["dst_ip"],
            packet_data["src_ip"],
            packet_data["dst_port"],
            packet_data["src_port"],
            packet_data["protocol"]
        )

        if forward_key in flows:
            flow_key = forward_key

        elif reverse_key in flows:
            flow_key = reverse_key

        else:
            return

        flow = flows[flow_key]

        total_packets = (
            flow["total_fwd_packets"] +
            flow["total_bwd_packets"]
        )

        # -----------------------------------------
        # IGNORE VERY SMALL FLOWS
        # -----------------------------------------

        if total_packets < MIN_PACKETS:

            print(
                f"Collecting flow... "
                f"{total_packets}/{MIN_PACKETS} packets"
            )

            return

        # -----------------------------------------
        # AVOID PREDICTING EVERY PACKET
        # -----------------------------------------

        import time

        now = time.time()

        previous = last_prediction.get(flow_key, 0)

        if now - previous < PREDICTION_INTERVAL:
            return

        last_prediction[flow_key] = now

        # -----------------------------------------
        # VALIDATE FEATURES
        # -----------------------------------------

        if len(features) != 78:

            print(
                "ERROR: Expected 78 features but got",
                len(features)
            )

            return

        # -----------------------------------------
        # DISPLAY FLOW
        # -----------------------------------------

        print("\n==============================")
        print("LIVE FLOW")
        print("==============================")

        print(
            "Source IP:",
            packet_data["src_ip"]
        )

        print(
            "Destination IP:",
            packet_data["dst_ip"]
        )

        print(
            "Source Port:",
            packet_data["src_port"]
        )

        print(
            "Destination Port:",
            packet_data["dst_port"]
        )

        print(
            "Protocol:",
            packet_data["protocol"]
        )

        print(
            "Total packets:",
            total_packets
        )

        print(
            "Number of features:",
            len(features)
        )
        print("\nRAW LIVE FEATURES:")
        for i, value in enumerate(features, start=1):
            print(f"{i:2d}. {value}")

        print("==============================")

        # -----------------------------------------
        # SEND TO IDS SERVER
        # -----------------------------------------

        response = requests.post(

            API_URL,

            json={
                "features": features,

                "src_ip":
                    packet_data["src_ip"],

                "dst_ip":
                    packet_data["dst_ip"],

                "protocol":
                    packet_data["protocol"]
            },

            timeout=10
        )

        print(
            "Status Code:",
            response.status_code
        )

        try:

            print(
                "Response:",
                response.json()
            )

        except Exception:

            print(
                "Response:",
                response.text
            )

    except Exception as e:

        print(
            "LIVE PREDICTION ERROR:",
            e
        )


print("======================================")
print("ADAPTIVE HYBRID IDS")
print("======================================")
print("Starting live packet capture...")
print("78-feature Combined AI Model")
print("Minimum packets:", MIN_PACKETS)
print("Prediction interval:", PREDICTION_INTERVAL)
print("======================================")


sniff(
    prn=process,
    store=False
)