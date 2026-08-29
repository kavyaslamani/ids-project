from scapy.layers.inet import IP, TCP, UDP

def extract_features(packet):

    features = {
        "src_ip": "",
        "dst_ip": "",
        "protocol": 0,
        "src_port": 0,
        "dst_port": 0,
        "packet_length": len(packet),
        "tcp_flags": 0
    }

    if IP in packet:

        features["src_ip"] = packet[IP].src
        features["dst_ip"] = packet[IP].dst
        features["protocol"] = packet[IP].proto

        if TCP in packet:
            features["src_port"] = packet[TCP].sport
            features["dst_port"] = packet[TCP].dport
            features["tcp_flags"] = int(packet[TCP].flags)

        elif UDP in packet:
            features["src_port"] = packet[UDP].sport
            features["dst_port"] = packet[UDP].dport

    return features