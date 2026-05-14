import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

print("Loading models...")

# =============================
# 1. Load models (SAFE MODE)
# =============================
autoencoder = keras.models.load_model(
    "models/autoencoder_toniot.h5",
    compile=False
)

dnn = keras.models.load_model(
    "models/dnn_toniot.h5",
    compile=False
)

# Recompile safely
autoencoder.compile(optimizer="adam", loss="mse")
dnn.compile(optimizer="adam", loss="sparse_categorical_crossentropy")

# =============================
# 2. Load test data
# =============================
X_test = pd.read_csv("data/X_test_toniot.csv").values

print("\nData loaded:", X_test.shape)

# =============================
# 3. Autoencoder anomaly detection
# =============================
reconstructed = autoencoder.predict(X_test)

mse = np.mean(np.power(X_test - reconstructed, 2), axis=1)

threshold = np.percentile(mse, 95)

anomalies = mse > threshold

print("\nAnomaly Threshold:", threshold)
print("Total anomalies detected:", np.sum(anomalies))

# =============================
# 4. DNN classification
# =============================
pred = np.argmax(dnn.predict(X_test), axis=1)

# =============================
# 5. Hybrid logic
# =============================
final_output = []

for i in range(len(X_test)):
    if anomalies[i]:
        final_output.append(-1)   # anomaly
    else:
        final_output.append(pred[i])

final_output = np.array(final_output)

# =============================
# 6. Results
# =============================
print("\n========== HYBRID IDS RESULT ==========")
print("Normal classified samples:", np.sum(final_output != -1))
print("Anomalies detected:", np.sum(final_output == -1))

print("\nSample outputs:")
print(final_output[:20])