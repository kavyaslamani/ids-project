from fastapi import FastAPI
from pydantic import BaseModel
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import os
from datetime import datetime

# -----------------------------------
# LOAD MODEL
# -----------------------------------

autoencoder = load_model("autoencoder_model.h5", compile=False)

app = FastAPI(title="Adaptive Hybrid IDS")

# -----------------------------------
# INPUT FORMAT
# -----------------------------------

class TrafficData(BaseModel):
    features: list
    src_ip: str = "Unknown"
    dst_ip: str = "Unknown"

# -----------------------------------
# LOG FILE SETUP
# -----------------------------------

log_file = "attack_logs.csv"

if not os.path.exists(log_file):
    pd.DataFrame(columns=[
        "timestamp",
        "src_ip",
        "dst_ip",
        "anomaly",
        "attack_name",
        "severity",
        "reconstruction_error"
    ]).to_csv(log_file, index=False)

# -----------------------------------
# ADAPTIVE MEMORY BUFFER
# -----------------------------------

error_history = []

# -----------------------------------
# MAIN PREDICT ENDPOINT
# -----------------------------------

@app.post("/predict")
def predict(data: TrafficData):

    # ---------------------------
    # PREPROCESS INPUT
    # ---------------------------

    features = np.array(data.features).reshape(1, -1)

    # ---------------------------
    # MODEL INFERENCE
    # ---------------------------

    reconstructed = autoencoder.predict(features, verbose=0)

    reconstruction_error = float(np.mean(np.square(features - reconstructed)))

    # ---------------------------
    # ADAPTIVE THRESHOLD
    # ---------------------------

    error_history.append(reconstruction_error)

    if len(error_history) > 50:
        error_history.pop(0)

    threshold = np.mean(error_history) + (np.std(error_history) * 0.9)

    anomaly = 1 if reconstruction_error > threshold else 0

    # ---------------------------
    # FINAL BALANCED SEVERITY ENGINE
    # ---------------------------

    if reconstruction_error > 0.85:
        severity = "CRITICAL"
        attack_name = "DDoS"

    elif reconstruction_error > 0.65:
        severity = "HIGH"
        attack_name = "Botnet"

    elif reconstruction_error > 0.40:
        severity = "MEDIUM"
        attack_name = "PortScan"

    elif reconstruction_error > threshold:
        severity = "LOW"
        attack_name = "Suspicious"

    else:
        severity = "LOW"
        attack_name = "Benign"

    # ---------------------------
    # TIMESTAMP
    # ---------------------------

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------------------
    # LOGGING
    # ---------------------------

    pd.DataFrame([{
        "timestamp": timestamp,
        "src_ip": data.src_ip,
        "dst_ip": data.dst_ip,
        "anomaly": anomaly,
        "attack_name": attack_name,
        "severity": severity,
        "reconstruction_error": reconstruction_error
    }]).to_csv(log_file, mode="a", header=False, index=False)

    # ---------------------------
    # RESPONSE
    # ---------------------------

    return {
        "timestamp": timestamp,
        "anomaly": anomaly,
        "attack_name": attack_name,
        "severity": severity,
        "reconstruction_error": reconstruction_error
    }

# -----------------------------------
# EVALUATION ENDPOINT
# -----------------------------------

@app.post("/evaluate")
def evaluate(data: TrafficData):

    features = np.array(data.features).reshape(1, -1)

    reconstructed = autoencoder.predict(features, verbose=0)

    error = float(np.mean(np.square(features - reconstructed)))

    return {
        "reconstruction_error": error,
        "anomaly": int(error > 0.15)
    }