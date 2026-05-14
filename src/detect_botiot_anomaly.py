import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

print("Loading test data...")

X_test = pd.read_csv("data/X_test_botiot.csv").values
y_test = pd.read_csv("data/y_test_botiot.csv").values

# Load model
autoencoder = load_model("models/autoencoder_botiot.h5", compile=False)

print("Running reconstruction...")

recon = autoencoder.predict(X_test)

# Error
mse = np.mean(np.power(X_test - recon, 2), axis=1)

# Threshold
threshold = np.percentile(mse, 95)

print("\nThreshold:", threshold)

# Predictions
y_pred = (mse > threshold).astype(int)

print("Anomalies detected:", np.sum(y_pred))

np.save("data/botiot_anomaly.npy", y_pred)

print("\n✅ Saved anomaly predictions")