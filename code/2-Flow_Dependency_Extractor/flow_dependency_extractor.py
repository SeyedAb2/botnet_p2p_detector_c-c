import os
import pandas as pd

# پیدا کردن ریشه پروژه به صورت داینامیک
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RESULTS_PATH = os.path.join(BASE_DIR, "results")

# خواندن ورودی
flows_file = os.path.join(RESULTS_PATH, "flows_filtered.csv")
df = pd.read_csv(flows_file, sep=",")

# محاسبه occurrence ها
counts = df.groupby(
    ["src", "src_port", "dst", "dst_port", "protocol"]
).size().reset_index(name="occurrences")

# ذخیره خروجی
out_file = os.path.join(RESULTS_PATH, "flow_occurrences.csv")
counts.to_csv(out_file, sep=",", index=False)

print("[*] Input flows:", len(df))
print("[*] Unique flows:", len(counts))
print("[*] Saved ->", out_file)
print(counts.tail(10))
