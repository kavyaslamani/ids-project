import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.metrics import classification_report, confusion_matrix

print("Loading models...")

autoencoder = load_model("models/autoencoder_combined.h5", compile=False)
dnn = load_model("models/dnn_combined.h5")

print("Loading test data...")

X_test = pd.read_csv("data/X_test_combined.csv").values
y_test = pd.read_csv("data/y_test_combined.csv").values.flatten()

# Step 1: Anomaly detection
reconstructions = autoencoder.predict(X_test)
mse = np.mean(np.power(X_test - reconstructions, 2), axis=1)

threshold = np.percentile(mse, 95)
print("Anomaly Threshold:", threshold)

anomalies = mse > threshold

# Step 2: Classification
y_pred = dnn.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)

print("\n=== HYBRID IDS REPORT ===")
print(classification_report(y_test, y_pred_classes))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_classes))