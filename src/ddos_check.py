import pandas as pd
import numpy as np

print("Loading DDoS dataset...")

df = pd.read_csv("data/DrDoS_DNS.csv", low_memory=False)

print("Original shape:", df.shape)

# =========================
# 1. Fix column names
# =========================
df.columns = df.columns.str.strip()

# =========================
# 2. Drop useless columns
# =========================
drop_cols = [
    "Flow ID",
    "Source IP",
    "Destination IP",
    "Timestamp"
]

df = df.drop(columns=[col for col in drop_cols if col in df.columns])

# =========================
# 3. Convert label
# =========================
df["Label"] = df["Label"].apply(lambda x: 1 if x != "BENIGN" else 0)

print("\nLabel counts:")
print(df["Label"].value_counts())

# =========================
# 4. Remove inf / NaN
# =========================
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

print("\nAfter cleaning:", df.shape)

# =========================
# 5. Save cleaned dataset
# =========================
df.to_csv("data/cleaned_ddos.csv", index=False)

print("\nSaved cleaned_ddos.csv")