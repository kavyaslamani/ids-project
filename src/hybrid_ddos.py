import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

print("Loading data...")

X_test = pd.read_csv("data/X_test_ddos.csv").values
y_test = pd.read_csv("data/y_test_ddos.csv").values.flatten()

# =========================
# Load models
# =========================
autoencoder = load_model("models/autoencoder_ddos.h5", compile=False)
dnn = load_model("models/dnn_ddos.h5", compile=False)

# =========================
# Autoencoder → anomaly
# =========================
print("Running autoencoder...")

recon = autoencoder.predict(X_test)
mse = np.mean(np.power(X_test - recon, 2), axis=1)

threshold = np.percentile(mse, 95)
anomaly_pred = (mse > threshold).astype(int)

# =========================
# DNN → classification
# =========================
print("Running DNN...")

dnn_pred = np.argmax(dnn.predict(X_test), axis=1)

# =========================
# Hybrid logic
# =========================
final_pred = []

for i in range(len(X_test)):
    if anomaly_pred[i] == 1:
        final_pred.append(1)  # attack
    else:
        final_pred.append(dnn_pred[i])

final_pred = np.array(final_pred)

# =========================
# Evaluation
# =========================
from sklearn.metrics import classification_report, confusion_matrix

print("\n=== HYBRID IDS REPORT ===")
print(classification_report(y_test, final_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, final_pred))