import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import classification_report, confusion_matrix

# Load trained models
autoencoder = load_model("models/autoencoder.h5", compile=False)
dnn = load_model("models/dnn_classifier.h5", compile=False)

# Load test data
X_test = pd.read_csv("data/X_test_scaled.csv")
y_test = pd.read_csv("data/y_test.csv").squeeze()

print("Loaded test data:", X_test.shape)

# -----------------------------
# STEP 1: Autoencoder anomaly detection
# -----------------------------

# Reconstruct test data
X_test_pred = autoencoder.predict(X_test, verbose=1)
mse = np.mean(np.power(X_test - X_test_pred, 2), axis=1)

# Load benign train data again to calculate threshold
X_train = pd.read_csv("data/X_train_scaled.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
X_train_benign = X_train[y_train == 0]

X_train_pred = autoencoder.predict(X_train_benign, verbose=1)
train_mse = np.mean(np.power(X_train_benign - X_train_pred, 2), axis=1)

threshold = np.percentile(train_mse, 95)
print("Anomaly Threshold:", threshold)

# Detect anomalies
anomaly_flags = (mse > threshold).astype(int)

# -----------------------------
# STEP 2: Hybrid prediction (FAST VERSION)
# -----------------------------

# Start with all predictions as benign
hybrid_predictions = np.zeros(len(X_test), dtype=int)

# Get only anomaly samples
anomaly_indices = np.where(anomaly_flags == 1)[0]
X_anomaly = X_test.iloc[anomaly_indices]

print("Number of anomaly samples sent to DNN:", len(X_anomaly))

# Predict all anomalies at once
dnn_preds = dnn.predict(X_anomaly, verbose=1)
dnn_classes = np.argmax(dnn_preds, axis=1)

# Put DNN predictions back into final array
hybrid_predictions[anomaly_indices] = dnn_classes

# -----------------------------
# Evaluation
# -----------------------------
print("\n=== HYBRID IDS CLASSIFICATION REPORT ===")
print(classification_report(y_test, hybrid_predictions))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, hybrid_predictions))