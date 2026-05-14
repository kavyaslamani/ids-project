import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

print("Loading cleaned TON-IoT dataset...")

df = pd.read_csv("data/cleaned_toniot.csv")

print("Dataset shape:", df.shape)

# -----------------------------
# 1. Split features & labels
# -----------------------------
X = df.drop(columns=["Label"])
y = df["Label"]

print("Features shape:", X.shape)
print("Labels shape:", y.shape)

# -----------------------------
# 2. Train-Test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# -----------------------------
# 3. Scaling
# -----------------------------
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nScaling complete!")

# -----------------------------
# 4. Save everything
# -----------------------------
pd.DataFrame(X_train_scaled).to_csv("data/X_train_toniot.csv", index=False)
pd.DataFrame(X_test_scaled).to_csv("data/X_test_toniot.csv", index=False)

y_train.to_csv("data/y_train_toniot.csv", index=False)
y_test.to_csv("data/y_test_toniot.csv", index=False)

joblib.dump(scaler, "models/scaler_toniot.pkl")

print("\n✅ TON-IoT prepared successfully!")