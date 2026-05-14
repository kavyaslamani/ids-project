import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib

print("Loading models...")

autoencoder = load_model("models/autoencoder_botiot.h5", compile=False)
dnn = load_model("models/dnn_botiot.h5", compile=False)
scaler = joblib.load("models/scaler_botiot.pkl")

print("Loading Wireshark data...")

df = pd.read_csv("data/traffic.csv")

print("Shape:", df.shape)

# =========================
# FEATURE EXTRACTION FIX
# =========================
features = df.select_dtypes(include=[np.number])

X = features.values

print("Raw feature shape:", X.shape)

# =========================
# FORCE 13 FEATURES (MODEL REQUIREMENT)
# =========================
if X.shape[1] < 13:
    pad = np.zeros((X.shape[0], 13 - X.shape[1]))
    X = np.hstack((X, pad))
else:
    X = X[:, :13]

print("Fixed feature shape:", X.shape)

# =========================
# SCALE DATA
# =========================
X = scaler.transform(X)

# =========================
# AUTOENCODER (ANOMALY DETECTION)
# =========================
recon = autoencoder.predict(X)
mse = np.mean(np.power(X - recon, 2), axis=1)

threshold = 0.4
anomalies = mse > threshold

print("\nTotal packets:", len(X))
print("Anomalies detected:", np.sum(anomalies))

# =========================
# DNN CLASSIFICATION
# =========================
pred = np.argmax(dnn.predict(X), axis=1)

print("\nSample predictions:")
print(pred[:20])