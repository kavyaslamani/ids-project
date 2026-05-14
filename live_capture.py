import requests
import numpy as np
import time
import random

URL = "http://127.0.0.1:8000/predict"

print("Starting Live IDS Traffic Capture...")

while True:

    try:

        # -----------------------------
        # NORMAL TRAFFIC (80%)
        # -----------------------------
        if random.random() < 0.8:

            features = np.random.normal(
                loc=0,
                scale=0.5,
                size=78
            ).tolist()

        # -----------------------------
        # ATTACK TRAFFIC (20%)
        # -----------------------------
        else:

            features = np.random.normal(
                loc=8,
                scale=3,
                size=78
            ).tolist()

        # -----------------------------
        # SEND TO API
        # -----------------------------
        response = requests.post(
            URL,
            json={"features": features}
        )

        print(response.json())

        time.sleep(1)

    except Exception as e:

        print("Error:", e)

        time.sleep(2)