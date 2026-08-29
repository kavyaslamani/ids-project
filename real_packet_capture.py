from scapy.all import sniff
from packet_features import extract_features
from flow_builder_v2 import update_flow
from live_predict import predict_attack
from attack_logger import log_attack


def protocol_name(proto):
    protocols = {
        1: "ICMP",
        6: "TCP",
        17: "UDP"
    }
    return protocols.get(proto, f"Protocol-{proto}")


def tcp_flag_name(flag):
    flags = {
        2: "SYN",
        16: "ACK",
        17: "FIN-ACK",
        18: "SYN-ACK",
        24: "PSH-ACK",
        25: "FIN-PSH-ACK"
    }
    return flags.get(flag, str(flag))


def process_packet(packet):

    # Extract packet features
    features = extract_features(packet)

    # Ignore packets without IP layer
    if features["src_ip"] == "":
        return

    # Build flow statistics
    flow = update_flow(features)

    # ---------------- IDS Prediction ----------------
    try:

        result = predict_attack(flow)

        # Save prediction to CSV
        log_attack(features, result)

        anomaly = result["anomaly"]
        attack = result["attack"]
        reconstruction_error = result["reconstruction_error"]
        risk = result["risk"]
        confidence = result["confidence"]

    except Exception as e:

        print(e)

        anomaly = "N/A"
        attack = "Prediction Pending"
        reconstruction_error = 0
        risk = "Unknown"
        confidence = 0

    print("\n" + "=" * 70)
    print("📦 LIVE NETWORK PACKET")
    print("=" * 70)

    print(f"🌐 Source IP          : {features['src_ip']}")
    print(f"🌐 Destination IP     : {features['dst_ip']}")
    print(f"📡 Protocol           : {protocol_name(features['protocol'])}")
    print(f"🔌 Source Port        : {features['src_port']}")
    print(f"🔌 Destination Port   : {features['dst_port']}")
    print(f"📦 Packet Length      : {features['packet_length']} Bytes")
    print(f"🚩 TCP Flags          : {tcp_flag_name(features['tcp_flags'])}")

    print("\n📊 FLOW FEATURES")
    print(f"Protocol               : {flow['protocol']}")
    print(f"Source Port            : {flow['src_port']}")
    print(f"Destination Port       : {flow['dst_port']}")
    print(f"Flow Duration          : {flow['flow_duration']:.2f}")
    print(f"Forward Packets        : {flow['total_fwd_packets']}")
    print(f"Backward Packets       : {flow['total_backward_packets']}")
    print(f"Flow Bytes/sec         : {flow['flow_bytes_sec']:.2f}")
    print(f"Flow Packets/sec       : {flow['flow_packets_sec']:.2f}")
    print(f"Packet Length Mean     : {flow['packet_length_mean']:.2f}")
    print(f"Packet Length Std      : {flow['packet_length_std']:.2f}")

    print("\n📊 FORWARD PACKET FEATURES")
    print(f"Total Forward Bytes    : {flow['totlen_fwd_pkts']}")
    print(f"Fwd Packet Max         : {flow['fwd_pkt_len_max']}")
    print(f"Fwd Packet Min         : {flow['fwd_pkt_len_min']}")
    print(f"Fwd Packet Mean        : {flow['fwd_pkt_len_mean']:.2f}")
    print(f"Fwd Packet Std         : {flow['fwd_pkt_len_std']:.2f}")

    print("\n📊 BACKWARD PACKET FEATURES")
    print(f"Total Backward Bytes   : {flow['totlen_bwd_pkts']}")
    print(f"Bwd Packet Max         : {flow['bwd_pkt_len_max']}")
    print(f"Bwd Packet Min         : {flow['bwd_pkt_len_min']}")
    print(f"Bwd Packet Mean        : {flow['bwd_pkt_len_mean']:.2f}")
    print(f"Bwd Packet Std         : {flow['bwd_pkt_len_std']:.2f}")

    print("\n📊 IAT FEATURES")
    print(f"Flow IAT Mean          : {flow['flow_iat_mean']:.6f}")
    print(f"Flow IAT Std           : {flow['flow_iat_std']:.6f}")
    print(f"Flow IAT Max           : {flow['flow_iat_max']:.6f}")
    print(f"Flow IAT Min           : {flow['flow_iat_min']:.6f}")

    print(f"Fwd IAT Mean           : {flow['fwd_iat_mean']:.6f}")
    print(f"Fwd IAT Std            : {flow['fwd_iat_std']:.6f}")

    print(f"Bwd IAT Mean           : {flow['bwd_iat_mean']:.6f}")
    print(f"Bwd IAT Std            : {flow['bwd_iat_std']:.6f}")

    print("\n🚨 IDS PREDICTION")
    print(f"Anomaly                : {anomaly}")
    print(f"Attack Type            : {attack}")
    print(f"Confidence             : {confidence:.2%}")
    print(f"Risk Level             : {risk}")
    print(f"Reconstruction Error   : {reconstruction_error:.6f}")

    print("=" * 70)


print("=" * 70)
print("🔐 ADAPTIVE HYBRID IDS - PHASE 2")
print("🌐 REAL NETWORK PACKET CAPTURE STARTED")
print("=" * 70)

sniff(
    prn=process_packet,
    store=False
)