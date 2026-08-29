import csv
import os
from datetime import datetime
from database import insert_attack

LOG_FILE = "attack_logs.csv"

def log_attack(features, result):

    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp",
                "Source IP",
                "Destination IP",
                "Protocol",
                "Attack",
                "Anomaly",
                "Confidence",
                "Reconstruction Error",
                "Risk"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            features.get("src_ip", "Unknown"),
            features.get("dst_ip", "Unknown"),
            features.get("protocol", 0),
            result.get("attack", "Unknown"),
            result.get("anomaly", False),
            round(result.get("confidence", 0), 4),
            round(result.get("reconstruction_error", 0), 6),
            result.get("risk", "Unknown")
        ])
        
        insert_attack(
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    features["src_ip"],
    features["dst_ip"],
    str(features["protocol"]),
    result["attack"],
    int(result["anomaly"]),
    float(result["reconstruction_error"]),
    result["risk"],
    float(result.get("confidence", 0))
)