from fastapi import FastAPI
import numpy as np

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Adaptive Hybrid IDS Live Server Running"
    }

@app.post("/predict")
def predict(data: dict):

    features = np.array(data["features"])

    score = float(np.mean(features))

    if score > 0.7:
        attack = "Unknown Attack"
    elif score > 0.4:
        attack = "Known Attack"
    else:
        attack = "Normal Traffic"

    return {
        "prediction": attack,
        "anomaly_score": score
    }