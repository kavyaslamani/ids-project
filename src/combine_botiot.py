import pandas as pd

print("Loading datasets...")

botiot = pd.read_csv("data/cleaned_botiot.csv")
cic = pd.read_csv("data/cleaned_02-14-2018.csv")

# Clean column names
botiot.columns = botiot.columns.str.strip()
cic.columns = cic.columns.str.strip()

# Find common columns
common_cols = list(set(botiot.columns) & set(cic.columns))

print("Common columns:", len(common_cols))

# Keep only common columns
botiot = botiot[common_cols]
cic = cic[common_cols]

# Get normal samples
normal = cic[cic["Label"] == 0]

# Sample data
normal_sample = normal.sample(n=200000, random_state=42)
botiot_sample = botiot.sample(n=200000, random_state=42)

print("Normal:", normal_sample.shape)
print("BotIoT:", botiot_sample.shape)

# Combine
combined = pd.concat([normal_sample, botiot_sample])
combined = combined.sample(frac=1, random_state=42)

print("Final shape:", combined.shape)

# Save
combined.to_csv("data/botiot_combined.csv", index=False)

print("\n✅ Saved botiot_combined.csv")