from scapy.all import sniff
import numpy as np
from tensorflow.keras.models import load_model
import joblib

print("Loading models...")

autoencoder = load_model("models/autoencoder_botiot.h5", compile=False)
dnn = load_model("models/dnn_botiot.h5", compile=False)
scaler = joblib.load("models/scaler_botiot.pkl")

# Simple feature extractor
def extract_features(packet):
    try:
        return [len(packet)]
    except:
        return None

def process_packet(packet):
    features = extract_features(packet)

    if features is None:
        return

    # Pad to 13 features (your model input)
    while len(features) < 13:
        features.append(0)

    X = np.array(features).reshape(1, -1)

    try:
        X = scaler.transform(X)
    except:
        return

    # Autoencoder
    recon = autoencoder.predict(X, verbose=0)
    mse = np.mean((X - recon) ** 2)

    threshold = 0.4

    if mse > threshold:
        print("🚨 Anomaly Detected!")

        pred = np.argmax(dnn.predict(X, verbose=0), axis=1)[0]

        if pred == 1:
            print("🔥 ATTACK DETECTED")
        else:
            print("⚠ Suspicious")

print("Starting live capture...")

sniff(prn=process_packet, count=50)