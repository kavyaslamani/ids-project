import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder

# Load the original combined dataset
df = pd.read_csv("data/combined_cicids.csv")

# Fit encoder on text labels
le = LabelEncoder()
le.fit(df["Label"])

print("Classes:")
print(le.classes_)

# Save encoder
joblib.dump(le, "models/label_encoder_combined.pkl")

print("\nSaved successfully.")