from fastapi import FastAPI
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
from datetime import datetime

from database import create_database, insert_attack

app = FastAPI()

# ==========================================
# CREATE DATABASE
# ==========================================

create_database()

# ==========================================
# LOAD AI MODELS
# ==========================================

autoencoder = tf.keras.models.load_model(
    "models/autoencoder_combined.h5",
    compile=False
)

dnn_model = tf.keras.models.load_model(
    "models/dnn_combined.h5",
    compile=False
)

scaler = joblib.load(
    "models/scaler_combined.pkl"
)

label_encoder = joblib.load(
    "models/label_encoder_combined.pkl"
)

threshold = joblib.load(
    "models/autoencoder_threshold_combined.pkl"
)

# ==========================================
# PREDICTION ROUTE
# ==========================================

@app.post("/predict")
def predict(data: dict):

    src_ip = data.get("src_ip", "Unknown")
    dst_ip = data.get("dst_ip", "Unknown")
    protocol = data.get("protocol", 0)

    try:

        # ==================================
        # FEATURE PROCESSING
        # ==================================

        features = np.asarray(
            data["features"],
            dtype=float
        )

        if features.size != 78:

            return {
                "attack": "System Error",
                "detection_type": "System Error",
                "anomaly": False,
                "reconstruction_error": 0,
                "risk": "Unknown",
                "confidence": 0,
                "error": (
                    f"Expected 78 features but received "
                    f"{features.size}"
                )
            }

        features = features.reshape(1, 78)

                # ==================================
        # SCALING
        # ==================================

        if hasattr(scaler, "feature_names_in_"):

            features_for_scaler = pd.DataFrame(
                features,
                columns=scaler.feature_names_in_
            )

        else:

            features_for_scaler = features

        scaled = scaler.transform(
            features_for_scaler
        )

        # ==================================
        # DEBUG LIVE SCALING
        # ==================================

        feature_names = (
            list(features_for_scaler.columns)
            if hasattr(features_for_scaler, "columns")
            else [str(i) for i in range(78)]
        )

        debug_df = pd.DataFrame({
            "Feature": feature_names,
            "Raw": features[0],
            "Mean": scaler.mean_,
            "Scale": scaler.scale_,
            "Scaled": scaled[0],
        })

        debug_df["AbsScaled"] = np.abs(
            debug_df["Scaled"]
        )

        print()
        print("==========================================")
        print("TOP 15 LIVE SCALED FEATURES")
        print("==========================================")

        print(
            debug_df
            .sort_values(
                "AbsScaled",
                ascending=False
            )
            .head(15)
            .to_string(index=False)
        )

        # ==================================
        # AUTOENCODER
        # ==================================

        reconstructed = autoencoder.predict(
            scaled,
            verbose=0
        )
        
                # ==================================
        # DEBUG LIVE SCALING
        # ==================================

        
        

        reconstruction_error = float(
            np.mean(
                np.square(
                    scaled - reconstructed
                )
            )
        )

        # ==================================
        # ANOMALY DETECTION
        # ==================================

        threshold = 0.04958238299974599

        anomaly = reconstruction_error > threshold

        # ==================================
        # DNN CLASSIFICATION
        # ==================================

        prediction = dnn_model.predict(
            scaled,
            verbose=0
        )

        confidence = float(
            np.max(prediction)
        )

        predicted_class = int(
            np.argmax(prediction)
        )

        predicted_attack = str(
            label_encoder.inverse_transform(
                [predicted_class]
            )[0]
        )

        # ==================================
        # HYBRID DECISION
        # ==================================

        if not anomaly:

            attack = "Benign"
            detection_type = "Benign Traffic"

        elif predicted_attack == "Benign":

            attack = "Unknown Attack"
            detection_type = "Unknown Anomaly"

        elif confidence < 0.90:

            attack = "Unknown Attack"
            detection_type = "Unknown Anomaly"

        else:

            attack = predicted_attack
            detection_type = "Known Attack"

        # ==================================
        # RISK LEVEL
        # ==================================

        if not anomaly:

            risk = "Low"

        elif reconstruction_error >= threshold * 2:

            risk = "High"

        else:

            risk = "Medium"

        # ==================================
        # SAVE TO SQLITE DATABASE
        # ==================================

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        insert_attack(
            timestamp,
            src_ip,
            dst_ip,
            protocol,
            attack,
            int(anomaly),
            reconstruction_error,
            risk,
            confidence
        )

        # ==================================
        # RETURN RESULT
        # ==================================

        return {
            "attack": attack,
            "detection_type": detection_type,
            "anomaly": bool(anomaly),
            "reconstruction_error": round(
                reconstruction_error,
                6
            ),
            "risk": risk,
            "confidence": round(
                confidence,
                4
            )
        }

    except Exception as e:

        return {
            "attack": "System Error",
            "detection_type": "System Error",
            "anomaly": False,
            "reconstruction_error": 0,
            "risk": "Unknown",
            "confidence": 0,
            "error": str(e)
        }