import requests
import random
import time

URL = "http://127.0.0.1:8000/predict"

print("Starting Attack Simulation...")

while True:

    features = [random.uniform(50, 500) for _ in range(78)]

    response = requests.post(
        URL,
        json={"features": features}
    )

    print(response.json())

    time.sleep(0.2)