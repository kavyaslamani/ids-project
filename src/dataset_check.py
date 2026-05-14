import pandas as pd

# Load dataset
df = pd.read_csv("data/02-14-2018.csv")

# 1. Show first 5 rows
print("========== FIRST 5 ROWS ==========")
print(df.head())

# 2. Show column names
print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

# 3. Show dataset shape
print("\n========== DATASET SHAPE ==========")
print("Rows, Columns:", df.shape)

# 4. Show label counts
print("\n========== LABEL COUNTS ==========")
print(df["Label"].value_counts())

# 5. Show missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# 6. Show data types
print("\n========== DATA TYPES ==========")
print(df.dtypes)