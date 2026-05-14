import pandas as pd

print("Loading TON-IoT dataset...")

df = pd.read_csv("data/toniot.csv")

print("\n✅ Loaded successfully!")

print("\nSHAPE:")
print(df.shape)

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\nFIRST 5 ROWS:")
print(df.head())

print("\nDATA TYPES:")
print(df.dtypes)

# Detect label column
print("\nLABEL INFO:")

if "label" in df.columns:
    print(df["label"].value_counts())

elif "Attack" in df.columns:
    print(df["Attack"].value_counts())

elif "type" in df.columns:
    print(df["type"].value_counts())

else:
    print("⚠️ No label column found")