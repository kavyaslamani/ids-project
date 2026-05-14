import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

print("Loading test data...")

X_test = pd.read_csv("data/X_test_ddos.csv").values
y_test = pd.read_csv("data/y_test_ddos.csv").values

# =========================
# Load autoencoder
# =========================
autoencoder = load_model("models/autoencoder_ddos.h5", compile=False)

# =========================
# Reconstruction
# =========================
print("Running reconstruction...")

recon = autoencoder.predict(X_test)

# =========================
# Error calculation
# =========================
mse = np.mean(np.power(X_test - recon, 2), axis=1)

# =========================
# Threshold (95th percentile)
# =========================
threshold = np.percentile(mse, 95)

print("\nAnomaly Threshold:", threshold)

# =========================
# Predictions
# =========================
y_pred = (mse > threshold).astype(int)

print("\nTotal anomalies detected:", np.sum(y_pred))

# =========================
# Save results
# =========================
np.save("data/ddos_anomaly_preds.npy", y_pred)

print("\n✅ Saved anomaly predictions")