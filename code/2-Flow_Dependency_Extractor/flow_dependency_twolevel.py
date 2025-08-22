# ===========================
# Step 1: Two-Level Dependencies
# ===========================

import pandas as pd
import math
import os

# --- Paths (داینامیک) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RESULTS_PATH = os.path.join(BASE_DIR, "results")

flows_file = os.path.join(RESULTS_PATH, "flows_filtered.csv")
occurrences_file = os.path.join(RESULTS_PATH, "flow_occurrences.csv")
out_file = os.path.join(RESULTS_PATH, "twolevel_dependencies.csv")

# --- Parameters ---
T_dep = 2.0
N_dep = 5
S_dep_th = 0.3

# --- Load Data ---
print("\n[+] Loading input files...")
df = pd.read_csv(flows_file, sep=",")
occurrences = pd.read_csv(occurrences_file, sep=",")

df = df.merge(
    occurrences,
    on=["src", "src_port", "dst", "dst_port", "protocol"],
    how="left"
)

# --- Build Two-Level Dependencies ---
print("\n[+] Building Two-Level Dependencies...")

candidates = {}
for host, host_flows in df.groupby("src"):
    host_flows = host_flows.sort_values("start").reset_index(drop=True)
    for i, fi in host_flows.iterrows():
        Ni = fi["occurrences"]
        for j in range(i + 1, len(host_flows)):
            fj = host_flows.iloc[j]
            Nj = fj["occurrences"]
            if fj["start"] - fi["end"] > T_dep:
                break
            if abs(Ni - Nj) <= N_dep:
                key = (
                    fi["src"], fi["dst"], fi["src_port"], fi["dst_port"], fi["protocol"],
                    fj["src"], fj["dst"], fj["src_port"], fj["dst_port"], fj["protocol"]
                )
                if key not in candidates:
                    candidates[key] = {"Ni": Ni, "Nj": Nj, "Tij": 0}
                candidates[key]["Tij"] += 1

rows = []
for key, vals in candidates.items():
    Ni, Nj, Tij = vals["Ni"], vals["Nj"], vals["Tij"]
    S_dep = Tij / math.sqrt(Ni * Nj)
    if S_dep >= S_dep_th and Tij >= 1:
        rows.append({
            "src_fi": key[0], "dst_fi": key[1],
            "src_port_fi": key[2], "dst_port_fi": key[3],
            "protocol_fi": key[4],
            "src_fj": key[5], "dst_fj": key[6],
            "src_port_fj": key[7], "dst_port_fj": key[8],
            "protocol_fj": key[9],
            "Ni": Ni, "Nj": Nj, "Tij": Tij,
            "S_dep": S_dep
        })

df_dep = pd.DataFrame(rows)
df_dep.to_csv(out_file, sep=",", index=False)

print(f"[*] Two-level dependencies saved: {len(df_dep)} records at {out_file}")
