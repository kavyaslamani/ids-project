import sqlite3
import time
import winsound
from datetime import datetime

DB_NAME = "ids_recovered.db"
CHECK_INTERVAL = 2

# Alert only for these risk levels
ALERT_RISKS = {"HIGH", "CRITICAL"}


def get_latest_id():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(id)
        FROM AttackHistory
    """)

    result = cursor.fetchone()[0]

    conn.close()

    return result or 0


def get_new_records(last_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            source_ip,
            destination_ip,
            protocol,
            attack,
            anomaly,
            reconstruction_error,
            risk,
            confidence
        FROM AttackHistory
        WHERE id > ?
        ORDER BY id ASC
    """, (last_id,))

    records = cursor.fetchall()

    conn.close()

    return records


def show_alert(record):
    (
        record_id,
        timestamp,
        source_ip,
        destination_ip,
        protocol,
        attack,
        anomaly,
        reconstruction_error,
        risk,
        confidence
    ) = record

    print()
    print("=" * 65)
    print("🚨 REAL-TIME SECURITY ALERT")
    print("=" * 65)
    print(f"Alert ID           : {record_id}")
    print(f"Time               : {timestamp}")
    print(f"Attack             : {attack}")
    print(f"Risk               : {risk}")
    print(f"Source IP          : {source_ip}")
    print(f"Destination IP     : {destination_ip}")
    print(f"Protocol           : {protocol}")
    print(f"Anomaly            : {anomaly}")
    print(f"Reconstruction Err : {reconstruction_error}")
    print(f"Confidence         : {confidence}")
    print("=" * 65)

    # Windows built-in alert sound
    try:
       # Fun SOC-style rising security alarm
       winsound.Beep(700, 150)
       time.sleep(0.08)

       winsound.Beep(900, 150)
       time.sleep(0.08)

       winsound.Beep(1200, 350)

    except Exception:
       pass


def main():

    print("=" * 65)
    print("        ADAPTIVE HYBRID IDS - REAL-TIME ALERT MONITOR")
    print("=" * 65)
    print()
    print("Monitoring database:", DB_NAME)
    print("Alert levels:", ", ".join(ALERT_RISKS))
    print("Check interval:", CHECK_INTERVAL, "seconds")
    print()

    # Start from the current latest record.
    # This prevents thousands of old database records
    # from generating alerts when the monitor starts.
    last_id = get_latest_id()

    print("Existing records ignored:", last_id)
    print("Waiting for new detections...")
    print("Press CTRL+C to stop.")
    print()

    while True:

        try:

            records = get_new_records(last_id)

            for record in records:

                record_id = record[0]
                risk = str(record[8])

                last_id = record_id

                if risk.strip().upper() in ALERT_RISKS:
                    show_alert(record)

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:

            print()
            print("Alert monitor stopped.")
            break

        except Exception as e:

            print()
            print("Alert monitor error:", e)
            print("Retrying...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()