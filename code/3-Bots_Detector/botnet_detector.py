# ===========================
# Step 3: Bot Detector (Clustering)
# ===========================

import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib.pyplot as plt
import os

# --- Paths (داینامیک) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RESULTS_PATH = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_PATH, exist_ok=True)

# --- Step 1: Load multilayer dependencies ---
input_csv = os.path.join(RESULTS_PATH, "multilevel_dependencies.csv")
df = pd.read_csv(input_csv)

print("[*] Loaded dependencies:", len(df))

# --- Step 2: Build host-level graph ---
edges = df[["src_fi", "src_fj", "S_dep"]]
hosts = list(set(edges["src_fi"]).union(set(edges["src_fj"])))
print("[*] Unique hosts:", len(hosts))

# --- Step 3: Create distance matrix ---
host_index = {h: i for i, h in enumerate(hosts)}
n = len(hosts)
dist_matrix = np.zeros((n, n))

for _, row in edges.iterrows():
    i, j = host_index[row["src_fi"]], host_index[row["src_fj"]]
    weight = row["S_dep"]
    dist = 1 - weight   # وابستگی بیشتر → فاصله کمتر
    dist_matrix[i, j] = dist
    dist_matrix[j, i] = dist

df_dist = pd.DataFrame(dist_matrix, index=hosts, columns=hosts)
out_dist = os.path.join(RESULTS_PATH, "distance_matrix.csv")
df_dist.to_csv(out_dist)
print(f"[*] Distance matrix saved -> {out_dist}")

# --- Step 4: Hierarchical Clustering ---
Z = linkage(dist_matrix, method="average")

plt.figure(figsize=(12, 6))
dendrogram(Z, labels=hosts, leaf_rotation=90)
plt.title("Hierarchical Clustering of Hosts")
plt.xlabel("Hosts")
plt.ylabel("Distance")
plt.tight_layout()

# ذخیره نمودار
out_fig = os.path.join(RESULTS_PATH, "clusters_dendrogram.png")
plt.savefig(out_fig, dpi=300)

# نمایش نمودار روی صفحه
plt.show()

print(f"[*] Dendrogram saved -> {out_fig}")

# --- Step 5: Assign clusters ---
clusters = fcluster(Z, t=0.7, criterion="distance")  # threshold قابل تغییر
df_clusters = pd.DataFrame({"host": hosts, "cluster": clusters})
out_clusters = os.path.join(RESULTS_PATH, "clusters.csv")
df_clusters.to_csv(out_clusters, index=False)

print(f"[*] Clustering result saved -> {out_clusters}")
print(df_clusters.head(10))
