import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# =========================
# LOAD DATASET
# =========================

df = pd.read_csv("data/02-14-2018.csv")

print("\nOriginal Shape:")
print(df.shape)

# =========================
# REMOVE UNWANTED COLUMNS
# =========================

# Remove Timestamp
df = df.drop(columns=["Timestamp"])

print("\nAfter Removing Timestamp:")
print(df.shape)

# =========================
# HANDLE MISSING VALUES
# =========================

df.replace([np.inf, -np.inf], np.nan, inplace=True)

df.dropna(inplace=True)

print("\nAfter Removing Missing Values:")
print(df.shape)

# =========================
# ENCODE LABELS
# =========================

label_encoder = LabelEncoder()

df["Label"] = label_encoder.fit_transform(df["Label"])

print("\nEncoded Labels:")
print(df["Label"].unique())

# =========================
# SPLIT FEATURES & LABELS
# =========================

X = df.drop(columns=["Label"])

y = df["Label"]

print("\nFeature Shape:")
print(X.shape)

print("\nLabel Shape:")
print(y.shape)

# =========================
# NORMALIZE FEATURES
# =========================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

print("\nFeatures Normalized")

# =========================
# TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining Shape:")
print(X_train.shape)

print("\nTesting Shape:")
print(X_test.shape)

# =========================
# SAVE FILES
# =========================

pd.DataFrame(X_train).to_csv("data/X_train.csv", index=False)
pd.DataFrame(X_test).to_csv("data/X_test.csv", index=False)

pd.DataFrame(y_train).to_csv("data/y_train.csv", index=False)
pd.DataFrame(y_test).to_csv("data/y_test.csv", index=False)

print("\nPreprocessing Completed Successfully!")