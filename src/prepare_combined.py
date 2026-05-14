import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

print("Loading cleaned combined dataset...")

df = pd.read_csv("data/cleaned_combined.csv")

print("Dataset shape:", df.shape)

# Split features and labels
X = df.drop("Label", axis=1)
y = df["Label"]

print("Features:", X.shape)
print("Labels:", y.shape)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# Scaling
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nScaling complete!")

# Save scaler
joblib.dump(scaler, "models/scaler_combined.pkl")

# Save processed data
pd.DataFrame(X_train_scaled).to_csv("data/X_train_combined.csv", index=False)
pd.DataFrame(X_test_scaled).to_csv("data/X_test_combined.csv", index=False)

y_train.to_csv("data/y_train_combined.csv", index=False)
y_test.to_csv("data/y_test_combined.csv", index=False)

print("\n✅ Combined data prepared and saved!")