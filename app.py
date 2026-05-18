
from fastapi import FastAPI
import numpy as np
import tensorflow as tf
import joblib

app = FastAPI()

# ---------------------------------
# LOAD AI MODELS
# ---------------------------------

autoencoder = tf.keras.models.load_model(
    "autoencoder.h5",
    compile=False
)

dnn_model = tf.keras.models.load_model(
    "dnn_model.h5",
    compile=False
)

scaler = joblib.load(
    "scaler.pkl"
)

label_encoder = joblib.load(
    "label_encoder.pkl"
)

# ---------------------------------
# HOME ROUTE
# ---------------------------------

@app.get("/")
def home():

    return {
        "message": "Adaptive Hybrid IDS AI Server Running"
    }

# ---------------------------------
# PREDICT ROUTE
# ---------------------------------

@app.post("/predict")
def predict(data: dict):

    try:

        # -----------------------------
        # FEATURE PROCESSING
        # -----------------------------

        features = np.array(
            data["features"]
        ).reshape(1, -1)

        scaled = scaler.transform(features)

        # -----------------------------
        # AUTOENCODER
        # -----------------------------

        reconstructed = autoencoder.predict(
            scaled,
            verbose=0
        )

        mse = np.mean(
            np.square(scaled - reconstructed)
        )

        # -----------------------------
        # NORMALIZED SCORE
        # -----------------------------

        anomaly_score = float(mse / 300)

        # -----------------------------
        # ATTACK DETECTION
        # -----------------------------

        if anomaly_score > 4:

            attack = "Unknown Attack"

            risk = "Critical"

        elif anomaly_score > 2:

            prediction = dnn_model.predict(
                scaled,
                verbose=0
            )

            predicted_class = np.argmax(
                prediction
            )

            attack = label_encoder.inverse_transform(
                [predicted_class]
            )[0]

            risk = "High"

        elif anomaly_score > 0.8:

            attack = "Suspicious Traffic"

            risk = "Medium"

        else:

            attack = "Normal Traffic"

            risk = "Low"

        # -----------------------------
        # RESPONSE
        # -----------------------------

        return {

            "prediction": attack,

            "anomaly_score": round(
                anomaly_score,
                6
            ),

            "risk_level": risk

        }

    except Exception as e:

        return {

            "prediction": "System Error",

            "anomaly_score": 0,

            "risk_level": "Unknown",

            "error": str(e)

        }