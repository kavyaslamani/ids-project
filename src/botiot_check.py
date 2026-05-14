import pandas as pd

print("Loading Bot-IoT dataset...")

df = pd.read_csv("data/botiot.csv", low_memory=False)

print("\nShape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

# Detect label column
if "attack" in df.columns:
    print("\nLabel counts:")
    print(df["attack"].value_counts())
elif "label" in df.columns:
    print("\nLabel counts:")
    print(df["label"].value_counts())
else:
    print("\n❌ Label column not found")

print("\nFirst 5 rows:")
print(df.head())