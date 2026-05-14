from scapy.all import *
import requests
import random

SERVER_URL = "http://127.0.0.1:8000/predict"

print("Live Packet Capture Started...")

# -----------------------------------
# PROCESS PACKETS
# -----------------------------------

def process_packet(packet):

    try:

        src_ip = "Unknown"
        dst_ip = "Unknown"

        packet_length = len(packet)

        ttl = random.randint(20, 128)
        proto = random.randint(1, 17)
        sport = random.randint(1000, 65000)
        dport = random.choice([80, 443, 53, 22, 8080])

        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            ttl = packet[IP].ttl
            proto = packet[IP].proto

        if TCP in packet:
            sport = packet[TCP].sport
            dport = packet[TCP].dport

        # -----------------------------------
        # ADD NOISE (IMPORTANT FOR VARIATION)
        # -----------------------------------

        noise = random.uniform(-0.5, 0.5)

        features = [
            (packet_length / 1500) + noise,
            (ttl / 255) + noise,
            (proto / 17) + noise,
            (sport / 65535) + noise,
            (dport / 65535) + noise
        ]

        # PAD TO 78 FEATURES
        while len(features) < 78:
            features.append(random.uniform(0, 1))

        # SEND TO SERVER
        response = requests.post(
            SERVER_URL,
            json={
                "features": features,
                "src_ip": src_ip,
                "dst_ip": dst_ip
            }
        )

        print(response.json())

    except Exception as e:
        print("Error:", e)

# -----------------------------------
# START SNIFFER
# -----------------------------------

sniff(prn=process_packet, store=False)