import os
from scapy.all import rdpcap, TCP, UDP, IP
from collections import defaultdict
import pandas as pd

# پیدا کردن ریشه پروژه به صورت داینامیک
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PCAP_PATH = os.path.join(BASE_DIR, "pcap", "EX-3.pcap")
RESULTS_PATH = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_PATH, exist_ok=True)

print("[*] Using pcap file:", PCAP_PATH)

# خواندن pcap
packets = rdpcap(PCAP_PATH)

FLOW_TIMEOUT = 60
flows = defaultdict(list)

# (باقی کد بدون تغییر همون باشه...)

for pkt in packets:
    if IP in pkt and (TCP in pkt or UDP in pkt):
        proto = "TCP" if TCP in pkt else "UDP"
        src_ip, dst_ip = pkt[IP].src, pkt[IP].dst
        src_port = pkt[proto].sport
        dst_port = pkt[proto].dport
        flow_key = (src_ip, src_port, dst_ip, dst_port, proto)

        ts = pkt.time

        if not flows[flow_key]:
            flows[flow_key].append({
                "start_time": ts,
                "end_time": ts,
                "num_packets": 1,
                "num_bytes": len(pkt)
            })
        else:
            last_flow = flows[flow_key][-1]
            if ts - last_flow["end_time"] > FLOW_TIMEOUT:
                flows[flow_key].append({
                    "start_time": ts,
                    "end_time": ts,
                    "num_packets": 1,
                    "num_bytes": len(pkt)
                })
            else:
                last_flow["end_time"] = ts
                last_flow["num_packets"] += 1
                last_flow["num_bytes"] += len(pkt)

# --- ذخیره خروجی ---
rows = []
for key, occ_list in flows.items():
    src, sport, dst, dport, proto = key
    for occ_id, f in enumerate(occ_list, 1):
        f["duration"] = f["end_time"] - f["start_time"]
        rows.append({
            "src": src, "src_port": sport,
            "dst": dst, "dst_port": dport,
            "protocol": proto,
            "start": f["start_time"],
            "end": f["end_time"],
            "duration": f["duration"],
            "packets": f["num_packets"],
            "bytes": f["num_bytes"],
            "occurrence_id": occ_id
        })

df = pd.DataFrame(rows)

MIN_BYTES = 100
MIN_PACKETS = 2
MAX_DURATION = 3600
MAX_BYTES = 1_000_000

df_filtered = df[
    (df["bytes"] >= MIN_BYTES) &
    (df["packets"] >= MIN_PACKETS) &
    (df["duration"] <= MAX_DURATION) &
    (df["bytes"] <= MAX_BYTES)
]

# مسیر خروجی‌ها
flows_csv = os.path.join(RESULTS_PATH, "flows.csv")
flows_filtered_csv = os.path.join(RESULTS_PATH, "flows_filtered.csv")

df.to_csv(flows_csv, sep=",", index=False)
df_filtered.to_csv(flows_filtered_csv, sep=",", index=False)

print("Total flows (with occurrences):", len(df))
print("Filtered flows:", len(df_filtered))
print(df.head(10))
print(f"[*] Saved -> {flows_csv}")
print(f"[*] Saved -> {flows_filtered_csv}")
