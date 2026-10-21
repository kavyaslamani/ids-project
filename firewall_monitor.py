import sqlite3
import time
import ipaddress
from firewall import block_ip

DB_NAME = "ids_recovered.db"
CHECK_INTERVAL = 2

# Safety mode: keep True while validating detections.
# False attempts real Windows Firewall blocking.
DRY_RUN = True

BLOCK_RISKS = {"HIGH", "CRITICAL"}
MAX_UNIQUE_PUBLIC_IPS_PER_CYCLE = 5

# Avoid re-evaluating the same public IP during this process run.
# This is intentionally in-memory; restarting the monitor resets this set.
seen_public_ips = set()


def get_latest_id():
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("SELECT MAX(id) FROM AttackHistory").fetchone()
    return row[0] or 0


def get_new_records(last_id):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("""
            SELECT id, timestamp, source_ip, destination_ip, attack, risk,
                   anomaly, reconstruction_error, confidence
            FROM AttackHistory
            WHERE id > ?
            ORDER BY id ASC
        """, (last_id,)).fetchall()


def is_public_ip(ip):
    try:
        return ipaddress.ip_address(str(ip).strip()).is_global
    except ValueError:
        return False


def handle_firewall(record):
    (record_id, timestamp, source_ip, destination_ip, attack, risk,
     anomaly, reconstruction_error, confidence) = record

    source_ip = str(source_ip).strip()
    print()
    print("=" * 65)
    print("FIREWALL RESPONSE")
    print("=" * 65)
    print(f"Alert ID           : {record_id}")
    print(f"Time               : {timestamp}")
    print(f"Attack             : {attack}")
    print(f"Risk               : {risk}")
    print(f"Source IP          : {source_ip}")
    print(f"Destination IP     : {destination_ip}")
    print(f"Reconstruction Err : {reconstruction_error}")
    print(f"Confidence         : {confidence}")

    if source_ip in ("", "Unknown", "None"):
        print("Firewall Action    : SKIPPED - Invalid source IP")
    elif not is_public_ip(source_ip):
        print(f"Firewall Action    : SKIPPED - Non-public/local IP {source_ip}")
    elif source_ip in seen_public_ips:
        print(f"Firewall Action    : SKIPPED - Already evaluated this run: {source_ip}")
    elif DRY_RUN:
        seen_public_ips.add(source_ip)
        print(f"Firewall Action    : WOULD BLOCK {source_ip}")
        print("Mode               : DRY RUN")
    else:
        # Only mark seen after the block operation reports success.
        try:
            result = block_ip(source_ip)
            if result is False:
                print(f"Firewall Action    : FAILED - block function did not confirm success")
            else:
                seen_public_ips.add(source_ip)
                print(f"Firewall Action    : BLOCK REQUESTED for {source_ip}")
                print("Verify the rule in Windows Firewall to confirm it is active.")
        except Exception as exc:
            print(f"Firewall Action    : FAILED - {exc}")

    print("=" * 65)


def main():
    print("=" * 65)
    print("ADAPTIVE HYBRID IDS - FIREWALL MONITOR")
    print("=" * 65)
    print("Database:", DB_NAME)
    print("Firewall trigger:", ", ".join(sorted(BLOCK_RISKS)))
    print("Check interval:", CHECK_INTERVAL, "seconds")
    print("Maximum unique public IPs per cycle:", MAX_UNIQUE_PUBLIC_IPS_PER_CYCLE)
    print("DRY RUN:", DRY_RUN)
    print("Public IP blocking only: ENABLED")
    print()

    last_id = get_latest_id()
    print("Existing records ignored:", last_id)
    print("Waiting for new high-risk detections...")
    print("Press CTRL+C to stop.")
    print()

    while True:
        try:
            records = get_new_records(last_id)
            unique_public_this_cycle = set()

            for record in records:
                record_id = record[0]
                risk = str(record[5]).strip().upper()

                if risk in BLOCK_RISKS:
                    source_ip = str(record[2]).strip()
                    valid_public = is_public_ip(source_ip)

                    # Stop before consuming the next unseen public IP when
                    # the per-cycle cap is reached; it will be read next cycle.
                    if (valid_public and source_ip not in seen_public_ips
                            and source_ip not in unique_public_this_cycle
                            and len(unique_public_this_cycle) >= MAX_UNIQUE_PUBLIC_IPS_PER_CYCLE):
                        break

                    if valid_public and source_ip not in seen_public_ips:
                        unique_public_this_cycle.add(source_ip)
                    handle_firewall(record)

                # Advance only after this record was handled/skipped.
                last_id = record_id

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\nFirewall monitor stopped.")
            break
        except Exception as exc:
            print("\nFirewall monitor error:", exc)
            print("Retrying...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
