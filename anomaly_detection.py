import pandas as pd
import numpy as np

from tensorflow.keras.models import load_model

# =========================
# LOAD AUTOENCODER MODEL
# =========================

autoencoder = load_model("autoencoder_model.h5", compile=False)

print("\nAutoencoder Loaded Successfully!")

# =========================
# LOAD TEST DATA
# =========================

X_test = pd.read_csv("data/X_test.csv")

y_test = pd.read_csv("data/y_test.csv")

print("\nTest Data Shape:")
print(X_test.shape)

# =========================
# RECONSTRUCT TEST DATA
# =========================

reconstructed = autoencoder.predict(X_test)

print("\nReconstruction Completed!")

# =========================
# CALCULATE RECONSTRUCTION ERROR
# =========================

mse = np.mean(np.power(X_test - reconstructed, 2), axis=1)

print("\nFirst 10 Reconstruction Errors:")
print(mse[:10])

# =========================
# SET THRESHOLD
# =========================

threshold = np.percentile(mse, 95)

print("\nThreshold:")
print(threshold)

# =========================
# PREDICT ANOMALIES
# =========================

predictions = (mse > threshold).astype(int)

print("\nFirst 20 Predictions:")
print(predictions[:20])

# =========================
# COUNT RESULTS
# =========================

anomaly_count = np.sum(predictions)

normal_count = len(predictions) - anomaly_count

print("\nNormal Traffic Count:")
print(normal_count)

print("\nAnomaly Count:")
print(anomaly_count)

# =========================
# SAVE PREDICTIONS
# =========================

np.save("data/anomaly_predictions.npy", predictions)

print("\nAnomaly Detection Completed Successfully!")