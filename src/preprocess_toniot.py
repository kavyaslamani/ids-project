import pandas as pd
import numpy as np

print("Loading TON-IoT dataset...")

df = pd.read_csv("data/toniot.csv")

print("Original Shape:", df.shape)

# -----------------------------
# 1. Remove useless columns
# -----------------------------
drop_cols = []

for col in df.columns:
    if "ip" in col.lower() or "ts" in col.lower():
        drop_cols.append(col)

df.drop(columns=drop_cols, inplace=True, errors='ignore')

print("\nRemoved columns:", drop_cols)

# -----------------------------
# 2. Handle missing / infinite values
# -----------------------------
df.replace([np.inf, -np.inf], np.nan, inplace=True)
before = df.shape[0]
df.dropna(inplace=True)
after = df.shape[0]

print("Rows removed:", before - after)

# -----------------------------
# 3. Encode categorical columns
# -----------------------------
categorical_cols = df.select_dtypes(include=['object']).columns

print("\nCategorical columns:", categorical_cols.tolist())

for col in categorical_cols:
    df[col] = df[col].astype("category").cat.codes

# -----------------------------
# 4. Handle label column
# -----------------------------
if "label" in df.columns:
    label_col = "label"
elif "Attack" in df.columns:
    label_col = "Attack"
elif "type" in df.columns:
    label_col = "type"
else:
    raise Exception("No label column found!")

print("\nUsing label column:", label_col)

# Ensure label is numeric
df[label_col] = df[label_col].astype(int)

# -----------------------------
# 5. Save cleaned dataset
# -----------------------------
df.rename(columns={label_col: "Label"}, inplace=True)

df.to_csv("data/cleaned_toniot.csv", index=False)

print("\n✅ Cleaned TON-IoT saved!")
print("Final Shape:", df.shape)