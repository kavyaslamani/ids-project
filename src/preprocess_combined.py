import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

print("Loading combined dataset...")

df = pd.read_csv("data/combined_cicids.csv")

print("Original shape:", df.shape)

# Drop Timestamp (not useful for model)
if "Timestamp" in df.columns:
    df.drop(columns=["Timestamp"], inplace=True)

# Replace inf values
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Drop missing rows
before = df.shape[0]
df.dropna(inplace=True)
after = df.shape[0]

print("Rows removed:", before - after)
print("After cleaning shape:", df.shape)

# Encode labels
le = LabelEncoder()
df["Label"] = le.fit_transform(df["Label"])

print("\nEncoded label mapping:")
for i, label in enumerate(le.classes_):
    print(f"{i} → {label}")

# Save cleaned dataset
df.to_csv("data/cleaned_combined.csv", index=False)

print("\n✅ Cleaned combined dataset saved!")