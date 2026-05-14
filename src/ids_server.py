from fastapi import FastAPI
import numpy as np
import joblib
import tensorflow as tf

app = FastAPI()

# Load models
print("Loading models...")
autoencoder = tf.keras.models.load_model("models/autoencoder.h5")
dnn_model = tf.keras.models.load_model("models/dnn_model.h5")
scaler = joblib.load("models/scaler.pkl")

@app.get("/")
def home():
    return {"message": "Adaptive IDS Server Running"}

@app.post("/predict")
def predict(data: dict):
    try:
        # Convert input to numpy
        X = np.array(data["features"]).reshape(1, -1)

        # Ensure 13 features
        if X.shape[1] < 13:
            X = np.pad(X, ((0, 0), (0, 13 - X.shape[1])), 'constant')

        # Scale
        X_scaled = scaler.transform(X)

        # Autoencoder (anomaly detection)
        recon = autoencoder.predict(X_scaled)
        error = np.mean(np.square(X_scaled - recon))

        threshold = 0.1
        anomaly = int(error > threshold)

        # DNN classification
        pred = dnn_model.predict(X_scaled)
        label = int(np.argmax(pred))

        return {
            "anomaly": anomaly,
            "class": label,
            "reconstruction_error": float(error)
        }

    except Exception as e:
        return {"error": str(e)}