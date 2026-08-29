import joblib

scaler = joblib.load("models/scaler_combined.pkl")

print("=" * 60)
print("MODEL FEATURE CONFIGURATION")
print("=" * 60)

print("Number of features:", len(scaler.feature_names_in_))

for i, feature in enumerate(scaler.feature_names_in_):
    print(f"{i:02d} : {feature}")

print("=" * 60)