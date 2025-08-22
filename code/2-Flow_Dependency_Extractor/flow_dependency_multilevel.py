# ===========================
# Multi-Layer Dependencies
# ===========================

import pandas as pd
import math
import os

# --- Paths (داینامیک) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RESULTS_PATH = os.path.join(BASE_DIR, "results")

input_csv = os.path.join(RESULTS_PATH, "twolevel_dependencies.csv")

# --- Multi-Layer Function ---
def build_multilayer_mini(input_csv, output_prefix,
                          S_dep_th_start=0.3, 
                          max_layers=3, 
                          chunksize=5000,      # فقط ۵۰۰۰ رکورد در هر chunk
                          sample_frac=0.05,    # فقط ۵٪ داده‌ها
                          host_limit=20,       # فقط ۲۰ تا host اول
                          stop_limit=2000):    # به محض رسیدن به ۲۰۰۰ رکورد stop

    current_input = input_csv
    S_dep_th = S_dep_th_start

    for layer in range(3, max_layers+1):
        print(f"\n[+] Building Layer {layer} with threshold {S_dep_th}")

        candidates = {}
        chunk_counter = 0

        for chunk in pd.read_csv(current_input, sep=",", chunksize=chunksize):
            chunk_counter += 1
            print(f"    Processing chunk {chunk_counter} ...")

            # --- Sampling ---
            if sample_frac < 1.0:
                chunk = chunk.sample(frac=sample_frac, random_state=42)

            for host, host_flows in chunk.groupby("src_fi"):
                host_flows = host_flows.sort_values("Ni").reset_index(drop=True)
                for i, fi in host_flows.iterrows():
                    Ni = fi["Ni"]
                    for j in range(i+1, len(host_flows)):
                        fj = host_flows.iloc[j]
                        Nj = fj["Nj"]
                        if abs(Ni - Nj) > 5:
                            break
                        key = (
                            fi["src_fi"], fi["dst_fi"], fi["src_port_fi"], fi["dst_port_fi"], fi["protocol_fi"],
                            fj["src_fj"], fj["dst_fj"], fj["src_port_fj"], fj["dst_port_fj"], fj["protocol_fj"]
                        )
                        if key not in candidates:
                            candidates[key] = {"Ni": Ni, "Nj": Nj, "Tij": 0}
                        candidates[key]["Tij"] += 1

            if len(candidates) > stop_limit:
                print(f"[!] Stop early: already {len(candidates)} records (limit {stop_limit}).")
                break

        # --- Filtering ---
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

        df_out = pd.DataFrame(rows)
        out_csv = f"{output_prefix}.csv"
        df_out.to_csv(out_csv, sep=",", index=False)

        print(f"[*] Layer {layer} done -> {len(df_out)} records saved at {out_csv}")

        if len(df_out) <= stop_limit:
            print(f"[!] Stop condition reached at Layer {layer} (records={len(df_out)})")
            break

        current_input = out_csv

    print("\n[+] Mini multi-layer dependency building finished.")

# --- Run Mini Version ---
output_prefix = os.path.join(RESULTS_PATH, "multilevel_dependencies")

build_multilayer_mini(
    input_csv=input_csv,
    output_prefix=output_prefix,
    S_dep_th_start=0.3,
    max_layers=3,
    chunksize=5000,
    sample_frac=0.1,
    host_limit=20,
    stop_limit=2000
)

print("\n Mini-run finished! Outputs are in:", RESULTS_PATH)
