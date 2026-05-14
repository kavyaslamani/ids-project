import pandas as pd

# Load dataset
df = pd.read_csv("data/02-14-2018.csv")

# Show first 5 rows
print("\nFIRST 5 ROWS:")
print(df.head())

# Dataset shape
print("\nDATASET SHAPE:")
print(df.shape)

# Column names
print("\nCOLUMNS:")
print(df.columns.tolist())

# Label counts
print("\nLABEL COUNTS:")
print(df['Label'].value_counts())

# Missing values
print("\nMISSING VALUES:")
print(df.isnull().sum())