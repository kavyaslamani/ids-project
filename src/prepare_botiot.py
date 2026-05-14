import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

print("Loading cleaned Bot-IoT dataset...")

df = pd.read_csv("data/cleaned_botiot.csv")

print("Original shape:", df.shape)

# =========================
# 1. Separate normal & attack
# =========================
normal = df[df["Label"] == 0]
attack = df[df["Label"] == 1]

print("Normal samples:", normal.shape)
print("Attack samples:", attack.shape)

# =========================
# 2. Balance dataset
# =========================
attack_sample = attack.sample(n=50000, random_state=42)

balanced = pd.concat([normal, attack_sample])

# Shuffle
balanced = balanced.sample(frac=1, random_state=42)

print("Balanced shape:", balanced.shape)

# =========================
# 3. Split features & label
# =========================
X = balanced.drop("Label", axis=1)
y = balanced["Label"]

# =========================
# 🔥 FIX: Convert all to numeric
# =========================
X = X.apply(pd.to_numeric, errors='coerce')

# Remove invalid rows
X = X.dropna()
y = y[X.index]

print("\nAfter numeric conversion:")
print("Features:", X.shape)
print("Labels:", y.shape)

# =========================
# 4. Train-test split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# =========================
# 5. Scaling
# =========================
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nScaling complete!")

# =========================
# 6. Save processed data
# =========================
pd.DataFrame(X_train_scaled).to_csv("data/X_train_botiot.csv", index=False)
pd.DataFrame(X_test_scaled).to_csv("data/X_test_botiot.csv", index=False)

y_train.to_csv("data/y_train_botiot.csv", index=False)
y_test.to_csv("data/y_test_botiot.csv", index=False)

joblib.dump(scaler, "models/scaler_botiot.pkl")

print("\n✅ Saved Bot-IoT processed data")