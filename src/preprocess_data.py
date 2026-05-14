import pandas as pd
import numpy as np

# Load raw dataset
df = pd.read_csv("data/02-14-2018.csv")

print("Original Shape:", df.shape)

# Remove Timestamp column
df = df.drop(columns=["Timestamp"], errors="ignore")

# Replace infinity values with NaN
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Remove rows with missing values
before_rows = df.shape[0]
df.dropna(inplace=True)
after_rows = df.shape[0]

print("Rows removed due to NaN/inf:", before_rows - after_rows)
print("After Cleaning Shape:", df.shape)

# Encode labels into numbers
label_mapping = {
    "Benign": 0,
    "FTP-BruteForce": 1,
    "SSH-Bruteforce": 2
}

df["Label"] = df["Label"].map(label_mapping)

print("\nEncoded Label Counts:")
print(df["Label"].value_counts())

# Save cleaned dataset
df.to_csv("data/cleaned_02-14-2018.csv", index=False)

print("\nCleaned dataset saved successfully!")
print("Saved file: data/cleaned_02-14-2018.csv")