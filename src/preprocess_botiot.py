import pandas as pd
import numpy as np

print("Loading Bot-IoT dataset...")

df = pd.read_csv("data/botiot.csv", low_memory=False)

print("Original shape:", df.shape)

# =========================
# 1. Drop unnecessary columns
# =========================
drop_cols = [
    "pkSeqID",
    "saddr",
    "daddr",
    "category",
    "subcategory"
]

df = df.drop(columns=[col for col in drop_cols if col in df.columns])

# =========================
# 2. Encode categorical columns
# =========================
df["proto"] = df["proto"].astype("category").cat.codes

# =========================
# 3. Label already exists
# =========================
df.rename(columns={"attack": "Label"}, inplace=True)

# =========================
# 4. Remove NaN / inf
# =========================
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

print("\nAfter cleaning:", df.shape)

print("\nLabel counts:")
print(df["Label"].value_counts())

# =========================
# 5. Save cleaned dataset
# =========================
df.to_csv("data/cleaned_botiot.csv", index=False)

print("\n✅ Saved cleaned_botiot.csv")