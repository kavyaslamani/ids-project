import pandas as pd

print("Loading datasets...")

# =========================
# 1. Load datasets
# =========================
ddos = pd.read_csv("data/cleaned_ddos.csv", low_memory=False)
cic = pd.read_csv("data/cleaned_02-14-2018.csv")

# =========================
# 2. Clean column names
# =========================
ddos.columns = ddos.columns.str.strip()
cic.columns = cic.columns.str.strip()

# =========================
# 3. Find common columns
# =========================
common_cols = list(set(ddos.columns) & set(cic.columns))

print("Common columns:", len(common_cols))

# Keep only common features
ddos = ddos[common_cols]
cic = cic[common_cols]

# =========================
# 4. Separate NORMAL traffic
# =========================
normal = cic[cic["Label"] == 0]

# Sample NORMAL data
normal_sample = normal.sample(n=200000, random_state=42)

print("Normal sample:", normal_sample.shape)

# =========================
# 5. Sample DDoS (IMPORTANT)
# =========================
ddos_sample = ddos.sample(n=200000, random_state=42)

print("DDoS sample:", ddos_sample.shape)

# =========================
# 6. Combine datasets
# =========================
combined = pd.concat([ddos_sample, normal_sample])

# Shuffle dataset
combined = combined.sample(frac=1, random_state=42)

print("Balanced dataset shape:", combined.shape)

# =========================
# 7. Save final dataset
# =========================
combined.to_csv("data/ddos_combined.csv", index=False)

print("\n✅ Saved: data/ddos_combined.csv")