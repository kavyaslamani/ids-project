import subprocess

blocked_ips = set()

def block_ip(ip):

    if ip == "Unknown":
        return

    if ip in blocked_ips:
        return

    try:
        rule_name = f"IDS_Block_{ip}"

        subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                "dir=in",
                "action=block",
                f"remoteip={ip}"
            ],
            check=True
        )

        blocked_ips.add(ip)

        print(f"[FIREWALL] Blocked {ip}")

    except Exception as e:
        print("Firewall Error:", e)