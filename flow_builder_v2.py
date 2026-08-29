
import time
import numpy as np

flows = {}


def update_flow(packet):

    forward_key = (
        packet["src_ip"],
        packet["dst_ip"],
        packet["src_port"],
        packet["dst_port"],
        packet["protocol"]
    )

    reverse_key = (
        packet["dst_ip"],
        packet["src_ip"],
        packet["dst_port"],
        packet["src_port"],
        packet["protocol"]
    )

    # -----------------------------------------
    # FLOW DIRECTION
    # -----------------------------------------

    if forward_key in flows:
        key = forward_key
        direction = "forward"

    elif reverse_key in flows:
        key = reverse_key
        direction = "backward"

    else:
        key = forward_key
        direction = "forward"

    now = time.time() * 1_000_000

    # -----------------------------------------
    # CREATE NEW FLOW
    # -----------------------------------------

    if key not in flows:

        flows[key] = {

            "start_time": now,
            "last_time": now,

            "protocol": packet["protocol"],
            "dst_port": packet["dst_port"],

            "total_fwd_packets": 0,
            "total_bwd_packets": 0,

            "total_fwd_bytes": 0,
            "total_bwd_bytes": 0,

            "fwd_lengths": [],
            "bwd_lengths": [],
            "packet_lengths": [],

            "flow_iats": [],
            "fwd_iats": [],
            "bwd_iats": [],

            "last_fwd_time": None,
            "last_bwd_time": None,

            "fwd_iat_total": 0,
            "bwd_iat_total": 0,

            # TCP flags
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
            "cwe": 0,
            "ece": 0,

            "fwd_header_len": 0,
            "bwd_header_len": 0,

            # TCP information
            "init_fwd_win": -1,
            "init_bwd_win": -1,

            # Active / idle
            "active_times": [],
            "idle_times": [],

            "last_packet_time": now
        }

    flow = flows[key]

    length = float(packet["packet_length"])
    flags = int(packet["tcp_flags"])

    # -----------------------------------------
    # BASIC FLOW DATA
    # -----------------------------------------

    flow["packet_lengths"].append(length)

    # -----------------------------------------
    # TCP FLAGS
    # -----------------------------------------

    if flags & 0x01:
        flow["fin"] += 1

    if flags & 0x02:
        flow["syn"] += 1

    if flags & 0x04:
        flow["rst"] += 1

    if flags & 0x08:
        flow["psh"] += 1

        if direction == "forward":
            flow["fwd_psh"] += 1
        else:
            flow["bwd_psh"] += 1

    if flags & 0x10:
        flow["ack"] += 1

    if flags & 0x20:
        flow["urg"] += 1

        if direction == "forward":
            flow["fwd_urg"] += 1
        else:
            flow["bwd_urg"] += 1

    if flags & 0x40:
        flow["ece"] += 1

    if flags & 0x80:
        flow["cwe"] += 1

    # -----------------------------------------
    # INITIAL TCP WINDOWS
    # -----------------------------------------

    tcp_window = packet.get("tcp_window", 0)

    if direction == "forward":

        if flow["total_fwd_packets"] == 0:
            flow["init_fwd_win"] = tcp_window

    else:

        if flow["total_bwd_packets"] == 0:
            flow["init_bwd_win"] = tcp_window

    # -----------------------------------------
    # FORWARD / BACKWARD
    # -----------------------------------------

    if direction == "forward":

        flow["total_fwd_packets"] += 1
        flow["total_fwd_bytes"] += length

        flow["fwd_lengths"].append(length)

        flow["fwd_header_len"] += packet.get(
            "header_length",
            20
        )

        if flow["last_fwd_time"] is not None:

            iat = now - flow["last_fwd_time"]

            flow["fwd_iats"].append(iat)
            flow["fwd_iat_total"] += iat

        flow["last_fwd_time"] = now

    else:

        flow["total_bwd_packets"] += 1
        flow["total_bwd_bytes"] += length

        flow["bwd_lengths"].append(length)

        flow["bwd_header_len"] += packet.get(
            "header_length",
            20
        )

        if flow["last_bwd_time"] is not None:

            iat = now - flow["last_bwd_time"]

            flow["bwd_iats"].append(iat)
            flow["bwd_iat_total"] += iat

        flow["last_bwd_time"] = now

    # -----------------------------------------
    # FLOW IAT
    # -----------------------------------------

    # -----------------------------------------
# FLOW IAT + ACTIVE / IDLE
# -----------------------------------------

    if flow["last_time"] is not None:

      flow_iat = now - flow["last_time"]

      flow["flow_iats"].append(flow_iat)

    # CICIDS-style active/idle separation
      if flow_iat > 1.0:
         flow["idle_times"].append(flow_iat)
      else:
         flow["active_times"].append(flow_iat)

    flow["last_time"] = now

    # -----------------------------------------
    # BASIC ARRAYS
    # -----------------------------------------

    pkt = np.asarray(
        flow["packet_lengths"],
        dtype=float
    )

    fwd = np.asarray(
        flow["fwd_lengths"],
        dtype=float
    )

    bwd = np.asarray(
        flow["bwd_lengths"],
        dtype=float
    )

    flow_iats = np.asarray(
        flow["flow_iats"],
        dtype=float
    )

    fwd_iats = np.asarray(
        flow["fwd_iats"],
        dtype=float
    )

    bwd_iats = np.asarray(
        flow["bwd_iats"],
        dtype=float
    )

    # -----------------------------------------
    # SAFE STATISTICS
    # -----------------------------------------

    def stats(arr):

        if len(arr) == 0:

            return 0.0, 0.0, 0.0, 0.0

        return (
            float(np.mean(arr)),
            float(np.std(arr)),
            float(np.max(arr)),
            float(np.min(arr))
        )

    pkt_mean, pkt_std, pkt_max, pkt_min = stats(pkt)

    fwd_mean, fwd_std, fwd_max, fwd_min = stats(fwd)

    bwd_mean, bwd_std, bwd_max, bwd_min = stats(bwd)

    flow_iat_mean, flow_iat_std, flow_iat_max, flow_iat_min = stats(
        flow_iats
    )

    fwd_iat_mean, fwd_iat_std, fwd_iat_max, fwd_iat_min = stats(
        fwd_iats
    )

    bwd_iat_mean, bwd_iat_std, bwd_iat_max, bwd_iat_min = stats(
        bwd_iats
    )
    
    # -----------------------------------------
# ACTIVE / IDLE STATISTICS
# -----------------------------------------

    active = np.asarray(
       flow["active_times"],
       dtype=float
    )

    idle = np.asarray(
       flow["idle_times"],
       dtype=float
    )

    active_mean, active_std, active_max, active_min = stats(active)

    idle_mean, idle_std, idle_max, idle_min = stats(idle)

    # -----------------------------------------
    # DURATION
    # -----------------------------------------

    duration = now - flow["start_time"]

    if duration <= 0:
        duration = 1e-3

    # -----------------------------------------
    # RATES
    # -----------------------------------------

    total_packets = (
        flow["total_fwd_packets"] +
        flow["total_bwd_packets"]
    )

    total_bytes = (
        flow["total_fwd_bytes"] +
        flow["total_bwd_bytes"]
    )

    flow_bytes_sec = total_bytes / duration

    flow_packets_sec = total_packets / duration

    fwd_packets_sec = (
        flow["total_fwd_packets"] / duration
    )

    bwd_packets_sec = (
        flow["total_bwd_packets"] / duration
    )

    # -----------------------------------------
    # RATIOS
    # -----------------------------------------

    if flow["total_fwd_packets"] > 0:

        down_up_ratio = (
            flow["total_bwd_packets"] /
            flow["total_fwd_packets"]
        )

    else:

        down_up_ratio = 0.0

    # -----------------------------------------
    # PACKET SIZE AVERAGE
    # -----------------------------------------

    if len(pkt) > 0:
        pkt_size_avg = float(np.mean(pkt))
    else:
        pkt_size_avg = 0.0

    # -----------------------------------------
    # SEGMENT SIZE
    # -----------------------------------------

    fwd_seg_size_avg = fwd_mean
    bwd_seg_size_avg = bwd_mean

    # -----------------------------------------
    # 78 CICIDS FEATURES
    #
    # EXACT TRAINING ORDER
    # -----------------------------------------

    features = [

        # 1
        float(flow["dst_port"]),

        # 2
        float(flow["protocol"]),

        # 3
        float(duration),

        # 4
        float(flow["total_fwd_packets"]),

        # 5
        float(flow["total_bwd_packets"]),

        # 6
        float(flow["total_fwd_bytes"]),

        # 7
        float(flow["total_bwd_bytes"]),

        # 8
        fwd_max,

        # 9
        fwd_min,

        # 10
        fwd_mean,

        # 11
        fwd_std,

        # 12
        bwd_max,

        # 13
        bwd_min,

        # 14
        bwd_mean,

        # 15
        bwd_std,

        # 16
        flow_bytes_sec,

        # 17
        flow_packets_sec,

        # 18
        flow_iat_mean,

        # 19
        flow_iat_std,

        # 20
        flow_iat_max,

        # 21
        flow_iat_min,

        # 22
        flow["fwd_iat_total"],

        # 23
        fwd_iat_mean,

        # 24
        fwd_iat_std,

        # 25
        fwd_iat_max,

        # 26
        fwd_iat_min,

        # 27
        flow["bwd_iat_total"],

        # 28
        bwd_iat_mean,

        # 29
        bwd_iat_std,

        # 30
        bwd_iat_max,

        # 31
        bwd_iat_min,

        # 32
        float(flow["fwd_psh"]),

        # 33
        float(flow["bwd_psh"]),

        # 34
        float(flow["fwd_urg"]),

        # 35
        float(flow["bwd_urg"]),

        # 36
        float(flow["fwd_header_len"]),

        # 37
        float(flow["bwd_header_len"]),

        # 38
        fwd_packets_sec,

        # 39
        bwd_packets_sec,

        # 40
        pkt_min,

        # 41
        pkt_max,

        # 42
        pkt_mean,

        # 43
        pkt_std,

        # 44
        float(np.var(pkt)) if len(pkt) else 0.0,

        # 45
        float(flow["fin"]),

        # 46
        float(flow["syn"]),

        # 47
        float(flow["rst"]),

        # 48
        float(flow["psh"]),

        # 49
        float(flow["ack"]),

        # 50
        float(flow["urg"]),

        # 51
        float(flow["cwe"]),

        # 52
        float(flow["ece"]),

        # 53
        float(down_up_ratio),

        # 54
        pkt_size_avg,

        # 55
        fwd_seg_size_avg,

        # 56
        bwd_seg_size_avg,

        # 57
        0.0,  # Fwd Byts/b Avg

        # 58
        0.0,  # Fwd Pkts/b Avg

        # 59
        0.0,  # Fwd Blk Rate Avg

        # 60
        0.0,  # Bwd Byts/b Avg

        # 61
        0.0,  # Bwd Pkts/b Avg

        # 62
        0.0,  # Bwd Blk Rate Avg

        # 63
        float(flow["total_fwd_packets"]),

        # 64
        float(flow["total_fwd_bytes"]),

        # 65
        float(flow["total_bwd_packets"]),

        # 66
        float(flow["total_bwd_bytes"]),

        # 67
        float(flow["init_fwd_win"]),

        # 68
        float(flow["init_bwd_win"]),

        # 69
        max(
            0,
            flow["total_fwd_packets"] - 1
        ),

        # 70
        float(
            np.min(fwd)
        ) if len(fwd) else 0.0,

        # 71
active_mean,

# 72
active_std,

# 73
active_max,

# 74
active_min,

# 75
idle_mean,

# 76
idle_std,

# 77
idle_max,

# 78
idle_min
    ]

    # -----------------------------------------
    # FINAL VALIDATION
    # -----------------------------------------

    if len(features) != 78:

        raise ValueError(
            f"Feature builder generated {len(features)} features, expected 78"
        )

    return features
