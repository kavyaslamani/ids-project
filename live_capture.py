import time
import requests
import numpy as np
import pandas as pd

from collections import defaultdict
from scapy.all import sniff, IP, TCP, UDP, get_if_list

from attack_logger import log_attack


API_URL = "http://127.0.0.1:8000/predict"

FLOW_TIMEOUT = 15.0

FEATURE_NAMES = [
    "Dst Port",
    "Protocol",
    "Flow Duration",
    "Tot Fwd Pkts",
    "Tot Bwd Pkts",
    "TotLen Fwd Pkts",
    "TotLen Bwd Pkts",
    "Fwd Pkt Len Max",
    "Fwd Pkt Len Min",
    "Fwd Pkt Len Mean",
    "Fwd Pkt Len Std",
    "Bwd Pkt Len Max",
    "Bwd Pkt Len Min",
    "Bwd Pkt Len Mean",
    "Bwd Pkt Len Std",
    "Flow Byts/s",
    "Flow Pkts/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Tot",
    "Fwd IAT Mean",
    "Fwd IAT Std",
    "Fwd IAT Max",
    "Fwd IAT Min",
    "Bwd IAT Tot",
    "Bwd IAT Mean",
    "Bwd IAT Std",
    "Bwd IAT Max",
    "Bwd IAT Min",
    "Fwd PSH Flags",
    "Bwd PSH Flags",
    "Fwd URG Flags",
    "Bwd URG Flags",
    "Fwd Header Len",
    "Bwd Header Len",
    "Fwd Pkts/s",
    "Bwd Pkts/s",
    "Pkt Len Min",
    "Pkt Len Max",
    "Pkt Len Mean",
    "Pkt Len Std",
    "Pkt Len Var",
    "FIN Flag Cnt",
    "SYN Flag Cnt",
    "RST Flag Cnt",
    "PSH Flag Cnt",
    "ACK Flag Cnt",
    "URG Flag Cnt",
    "CWE Flag Count",
    "ECE Flag Cnt",
    "Down/Up Ratio",
    "Pkt Size Avg",
    "Fwd Seg Size Avg",
    "Bwd Seg Size Avg",
    "Fwd Byts/b Avg",
    "Fwd Pkts/b Avg",
    "Fwd Blk Rate Avg",
    "Bwd Byts/b Avg",
    "Bwd Pkts/b Avg",
    "Bwd Blk Rate Avg",
    "Subflow Fwd Pkts",
    "Subflow Fwd Byts",
    "Subflow Bwd Pkts",
    "Subflow Bwd Byts",
    "Init Fwd Win Byts",
    "Init Bwd Win Byts",
    "Fwd Act Data Pkts",
    "Fwd Seg Size Min",
    "Active Mean",
    "Active Std",
    "Active Max",
    "Active Min",
    "Idle Mean",
    "Idle Std",
    "Idle Max",
    "Idle Min"
]


flows = {}


def safe_mean(values):
    if not values:
        return 0.0

    return float(np.mean(values))


def safe_std(values):
    if len(values) < 2:
        return 0.0

    return float(np.std(values))


def safe_min(values):
    if not values:
        return 0.0

    return float(np.min(values))


def safe_max(values):
    if not values:
        return 0.0

    return float(np.max(values))


def packet_length(packet):
    try:
        return int(len(packet))
    except Exception:
        return 0


def get_protocol(packet):
    if TCP in packet:
        return 6

    if UDP in packet:
        return 17

    return int(packet[IP].proto)


def get_ports(packet):
    if TCP in packet:
        return int(packet[TCP].sport), int(packet[TCP].dport)

    if UDP in packet:
        return int(packet[UDP].sport), int(packet[UDP].dport)

    return 0, 0


def tcp_flags(packet):
    if TCP not in packet:
        return {
            "FIN": 0,
            "SYN": 0,
            "RST": 0,
            "PSH": 0,
            "ACK": 0,
            "URG": 0,
            "ECE": 0,
            "CWE": 0
        }

    flags = packet[TCP].flags

    return {
        "FIN": int(bool(flags & 0x01)),
        "SYN": int(bool(flags & 0x02)),
        "RST": int(bool(flags & 0x04)),
        "PSH": int(bool(flags & 0x08)),
        "ACK": int(bool(flags & 0x10)),
        "URG": int(bool(flags & 0x20)),
        "ECE": int(bool(flags & 0x40)),
        "CWE": int(bool(flags & 0x80))
    }


def create_flow_key(packet):
    if IP not in packet:
        return None

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst

    src_port, dst_port = get_ports(packet)
    protocol = get_protocol(packet)

    endpoint1 = (src_ip, src_port)
    endpoint2 = (dst_ip, dst_port)

    if endpoint1 <= endpoint2:
        return (
            endpoint1[0],
            endpoint1[1],
            endpoint2[0],
            endpoint2[1],
            protocol
        )

    return (
        endpoint2[0],
        endpoint2[1],
        endpoint1[0],
        endpoint1[1],
        protocol
    )


def add_packet(packet):
    if IP not in packet:
        return

    key = create_flow_key(packet)

    if key is None:
        return

    timestamp = float(packet.time)

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst

    src_port, dst_port = get_ports(packet)
    protocol = get_protocol(packet)

    length = packet_length(packet)
    flags = tcp_flags(packet)

    # Create new flow
    if key not in flows:

        flows[key] = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": protocol,

            "start": timestamp,
            "last": timestamp,

            "fwd_packets": [],
            "bwd_packets": [],

            "fwd_times": [],
            "bwd_times": [],

            "fwd_bytes": 0,
            "bwd_bytes": 0,

            "fwd_header": 0,
            "bwd_header": 0,

            "fwd_psh": 0,
            "bwd_psh": 0,

            "fwd_urg": 0,
            "bwd_urg": 0,

            "fin": 0,
            "syn": 0,
            "rst": 0,
            "psh": 0,
            "ack": 0,
            "urg": 0,
            "ece": 0,
            "cwe": 0,

            "init_fwd_win": 0,
            "init_bwd_win": 0
        }

    flow = flows[key]

    flow["last"] = timestamp

    # Check packet direction
    is_forward = (
        src_ip == flow["src_ip"]
        and dst_ip == flow["dst_ip"]
        and src_port == flow["src_port"]
        and dst_port == flow["dst_port"]
    )

    if is_forward:

        flow["fwd_packets"].append(length)
        flow["fwd_times"].append(timestamp)

        flow["fwd_bytes"] += length

        flow["fwd_header"] += int(packet[IP].ihl * 4)

        if TCP in packet:
            flow["fwd_header"] += int(packet[TCP].dataofs * 4)

            if flow["init_fwd_win"] == 0:
                flow["init_fwd_win"] = int(packet[TCP].window)

        flow["fwd_psh"] += flags["PSH"]
        flow["fwd_urg"] += flags["URG"]

    else:

        flow["bwd_packets"].append(length)
        flow["bwd_times"].append(timestamp)

        flow["bwd_bytes"] += length

        flow["bwd_header"] += int(packet[IP].ihl * 4)

        if TCP in packet:
            flow["bwd_header"] += int(packet[TCP].dataofs * 4)

            if flow["init_bwd_win"] == 0:
                flow["init_bwd_win"] = int(packet[TCP].window)

        flow["bwd_psh"] += flags["PSH"]
        flow["bwd_urg"] += flags["URG"]

    # TCP flags
    flow["fin"] += flags["FIN"]
    flow["syn"] += flags["SYN"]
    flow["rst"] += flags["RST"]
    flow["psh"] += flags["PSH"]
    flow["ack"] += flags["ACK"]
    flow["urg"] += flags["URG"]
    flow["ece"] += flags["ECE"]
    flow["cwe"] += flags["CWE"]

def iat_values(times):
    if len(times) < 2:
        return []

    ordered = sorted(times)

    return [
        (ordered[i] - ordered[i - 1]) * 1000000
        for i in range(1, len(ordered))
    ]


def build_features(flow):
    fwd = flow["fwd_packets"]
    bwd = flow["bwd_packets"]

    all_packets = fwd + bwd

    duration = (
        flow["last"] - flow["start"]
    ) * 1000000

    if duration < 0:
        duration = 0

    total_packets = len(all_packets)

    total_bytes = (
        flow["fwd_bytes"] +
        flow["bwd_bytes"]
    )

    duration_seconds = duration / 1000000

    if duration_seconds > 0:

        flow_bytes_sec = (
            total_bytes /
            duration_seconds
        )

        flow_packets_sec = (
            total_packets /
            duration_seconds
        )

        fwd_packets_sec = (
            len(fwd) /
            duration_seconds
        )

        bwd_packets_sec = (
            len(bwd) /
            duration_seconds
        )

    else:

        flow_bytes_sec = 0
        flow_packets_sec = 0
        fwd_packets_sec = 0
        bwd_packets_sec = 0

    all_times = (
        flow["fwd_times"] +
        flow["bwd_times"]
    )

    all_iat = iat_values(all_times)
    fwd_iat = iat_values(flow["fwd_times"])
    bwd_iat = iat_values(flow["bwd_times"])

    pkt_min = safe_min(all_packets)
    pkt_max = safe_max(all_packets)
    pkt_mean = safe_mean(all_packets)
    pkt_std = safe_std(all_packets)
    pkt_var = float(np.var(all_packets)) if all_packets else 0.0

    fwd_mean = safe_mean(fwd)
    bwd_mean = safe_mean(bwd)

    down_up_ratio = (
        len(bwd) / len(fwd)
        if len(fwd) > 0
        else 0
    )

    fwd_byts_b = (
        flow["fwd_bytes"] / len(fwd)
        if fwd
        else 0
    )

    fwd_pkts_b = (
        len(fwd) / total_packets
        if total_packets
        else 0
    )

    bwd_byts_b = (
        flow["bwd_bytes"] / len(bwd)
        if bwd
        else 0
    )

    bwd_pkts_b = (
        len(bwd) / total_packets
        if total_packets
        else 0
    )

    active_mean = 0.0
    active_std = 0.0
    active_max = 0.0
    active_min = 0.0

    idle_mean = 0.0
    idle_std = 0.0
    idle_max = 0.0
    idle_min = 0.0

    values = [
        flow["dst_port"],
        flow["protocol"],
        duration,

        len(fwd),
        len(bwd),

        flow["fwd_bytes"],
        flow["bwd_bytes"],

        safe_max(fwd),
        safe_min(fwd),
        fwd_mean,
        safe_std(fwd),

        safe_max(bwd),
        safe_min(bwd),
        bwd_mean,
        safe_std(bwd),

        flow_bytes_sec,
        flow_packets_sec,

        safe_mean(all_iat),
        safe_std(all_iat),
        safe_max(all_iat),
        safe_min(all_iat),

        sum(fwd_iat),
        safe_mean(fwd_iat),
        safe_std(fwd_iat),
        safe_max(fwd_iat),
        safe_min(fwd_iat),

        sum(bwd_iat),
        safe_mean(bwd_iat),
        safe_std(bwd_iat),
        safe_max(bwd_iat),
        safe_min(bwd_iat),

        flow["fwd_psh"],
        flow["bwd_psh"],

        flow["fwd_urg"],
        flow["bwd_urg"],

        flow["fwd_header"],
        flow["bwd_header"],

        fwd_packets_sec,
        bwd_packets_sec,

        pkt_min,
        pkt_max,
        pkt_mean,
        pkt_std,
        pkt_var,

        flow["fin"],
        flow["syn"],
        flow["rst"],
        flow["psh"],
        flow["ack"],
        flow["urg"],
        flow["cwe"],
        flow["ece"],

        down_up_ratio,

        pkt_mean,

        fwd_mean,
        bwd_mean,

        fwd_byts_b,
        fwd_pkts_b,
        0.0,

        bwd_byts_b,
        bwd_pkts_b,
        0.0,

        len(fwd),
        flow["fwd_bytes"],
        len(bwd),
        flow["bwd_bytes"],

        flow["init_fwd_win"],
        flow["init_bwd_win"],

        sum(
            1 for x in fwd
            if x > 0
        ),

        safe_min(fwd),

        active_mean,
        active_std,
        active_max,
        active_min,

        idle_mean,
        idle_std,
        idle_max,
        idle_min
    ]

    if len(values) != 78:
        raise ValueError(
            f"Feature count error: {len(values)}"
        )

    return values


def send_flow(key, flow):
    try:

        values = build_features(flow)

        df = pd.DataFrame(
            [values],
            columns=FEATURE_NAMES
        )

        print()
        print("=" * 60)
        print("REAL LIVE FLOW")
        print("=" * 60)

        print(
            "Source IP:",
            flow["src_ip"]
        )

        print(
            "Destination IP:",
            flow["dst_ip"]
        )

        print(
            "Source Port:",
            flow["src_port"]
        )

        print(
            "Destination Port:",
            flow["dst_port"]
        )

        print(
            "Protocol:",
            flow["protocol"]
        )

        print(
            "Packets:",
            len(
                flow["fwd_packets"]
            ) + len(
                flow["bwd_packets"]
            )
        )

        print(
            "Features:",
            len(values)
        )

        response = requests.post(
            API_URL,
            json={
                "src_ip": flow["src_ip"],
                "dst_ip": flow["dst_ip"],
                "protocol": flow["protocol"],
                "features": values
            },
            timeout=10
        )
        print("LIVE RAW FEATURES:")
        print(df.iloc[0].to_dict())

        print(
            "Status Code:",
            response.status_code
        )

        result = response.json()

        print(
            "Detection:",
            result.get("attack")
        )

        print(
            "Detection Type:",
            result.get("detection_type")
        )

        print(
            "Anomaly:",
            result.get("anomaly")
        )

        print(
            "Reconstruction Error:",
            result.get(
                "reconstruction_error"
            )
        )

        print(
            "Risk:",
            result.get("risk")
        )

        print(
            "Confidence:",
            result.get("confidence")
        )

        log_features = {
            "src_ip": flow["src_ip"],
            "dst_ip": flow["dst_ip"],
            "protocol": flow["protocol"]
        }

        log_result = {
            "attack": result.get(
                "attack",
                "System Error"
            ),
            "anomaly": result.get(
                "anomaly",
                False
            ),
            "reconstruction_error": result.get(
                "reconstruction_error",
                0
            ),
            "risk": result.get(
                "risk",
                "Unknown"
            ),
            "confidence": result.get(
                "confidence",
                0
            )
        }

        log_attack(
            log_features,
            log_result
        )

    except Exception as e:

        print()
        print(
            "LIVE FLOW ERROR:",
            str(e)
        )


def flush_old_flows():
    current_time = time.time()

    expired = []

    for key, flow in list(flows.items()):

        if (
            current_time -
            flow["last"]
        ) >= FLOW_TIMEOUT:

            expired.append(
                (key, flow)
            )

    for key, flow in expired:

        try:
            send_flow(key, flow)
        except Exception as e:
            print(
                "Flow processing error:",
                e
            )

        del flows[key]


def packet_callback(packet):
    try:

        if IP not in packet:
            return

        add_packet(packet)

        flush_old_flows()

    except Exception as e:

        print(
            "Packet processing error:",
            e
        )


def main():

    print()
    print("=" * 60)
    print(
        "ADAPTIVE HYBRID IDS"
    )
    print(
        "REAL-TIME PACKET CAPTURE"
    )
    print("=" * 60)

    print(
        "API:",
        API_URL
    )

    print(
        "Flow timeout:",
        FLOW_TIMEOUT,
        "seconds"
    )

    print(
        "Features:",
        len(FEATURE_NAMES)
    )

    print()
    print(
        "Available interfaces:"
    )

    for interface in get_if_list():
        print(
            " -",
            interface
        )

    print()
    print(
        "Starting real network capture..."
    )

    print(
        "Press CTRL+C to stop."
    )

    print()

    try:

        sniff(
            prn=packet_callback,
            store=False
        )

    except KeyboardInterrupt:

        print()
        print(
            "Stopping capture..."
        )

        for key, flow in list(
            flows.items()
        ):

            try:
                send_flow(
                    key,
                    flow
                )
            except Exception:
                pass

        print(
            "Capture stopped."
        )

    except Exception as e:

        print()
        print(
            "CAPTURE ERROR:",
            str(e)
        )


if __name__ == "__main__":
    main()