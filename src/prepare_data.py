import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Load cleaned dataset
df = pd.read_csv("data/cleaned_02-14-2018.csv")

print("Loaded cleaned dataset:", df.shape)

# Split features and labels
X = df.drop("Label", axis=1)
y = df["Label"]

print("Features shape:", X.shape)
print("Labels shape:", y.shape)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# Scale features
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nScaling complete!")
print("Scaled Train shape:", X_train_scaled.shape)
print("Scaled Test shape:", X_test_scaled.shape)

# Save scaler for future real-time traffic
joblib.dump(scaler, "models/scaler.pkl")

# Save processed train/test data
pd.DataFrame(X_train_scaled).to_csv("data/X_train_scaled.csv", index=False)
pd.DataFrame(X_test_scaled).to_csv("data/X_test_scaled.csv", index=False)
y_train.to_csv("data/y_train.csv", index=False)
y_test.to_csv("data/y_test.csv", index=False)

print("\nProcessed data saved successfully!")
print("Saved files:")
print("- models/scaler.pkl")
print("- data/X_train_scaled.csv")
print("- data/X_test_scaled.csv")
print("- data/y_train.csv")
print("- data/y_test.csv")