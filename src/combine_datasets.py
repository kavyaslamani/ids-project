import pandas as pd

print("Loading datasets...")

df1 = pd.read_csv("data/02-14-2018.csv")
df2 = pd.read_csv("data/02-15-2018.csv")

print("02-14 shape:", df1.shape)
print("02-15 shape:", df2.shape)

# Combine
df = pd.concat([df1, df2], ignore_index=True)

print("Combined shape:", df.shape)

# Save combined file
df.to_csv("data/combined_cicids.csv", index=False)

print("✅ Combined dataset saved as data/combined_cicids.csv")