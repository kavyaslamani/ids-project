from scapy.all import sniff
from packet_features import extract_features
from flow_builder_v2 import update_flow
from live_predict import predict_attack
from attack_logger import log_attack

print("="*60)
print("REAL TIME PACKET CAPTURE STARTED")
print("="*60)

def process(packet):

    features = extract_features(packet)

    if features["src_ip"] == "":
        return

    flow = update_flow(features)
    print(flow)
    prediction = predict_attack(flow)

    log_attack(features, prediction)

    print("\n" + "="*60)
    print("LIVE PACKET")
    print("="*60)

    print("Source IP      :", features["src_ip"])
    print("Destination IP :", features["dst_ip"])
    print("Protocol       :", features["protocol"])
    print("Source Port    :", features["src_port"])
    print("Destination Port:", features["dst_port"])
    print("Packet Length  :", features["packet_length"])
    print("TCP Flags      :", features["tcp_flags"])

    print("\nFLOW FEATURES")
    print("Flow Duration      :", flow["flow_duration"])
    print("Forward Packets    :", flow["total_fwd_packets"])
    print("Backward Packets   :", flow["total_backward_packets"])
    print("Flow Bytes/sec     :", flow["flow_bytes_sec"])
    print("Flow Packets/sec   :", flow["flow_packets_sec"])
    print("Down/Up Ratio    :", flow["down_up_ratio"])
    
    print("\nAI PREDICTION")
    print("Attack              :", prediction["attack"])
    print("Anomaly             :", prediction["anomaly"])
    print("Risk                :", prediction["risk"])
    print("Confidence          :", round(prediction["confidence"] * 100, 2), "%")
    print("Reconstruction Error:", round(prediction["reconstruction_error"], 6))

sniff(
    prn=process,
    store=False
)