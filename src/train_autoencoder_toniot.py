import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras

print("Loading TON-IoT data...")

X_train = pd.read_csv("data/X_train_toniot.csv").values
X_test = pd.read_csv("data/X_test_toniot.csv").values

print("Shape:", X_train.shape)

# -----------------------------
# Autoencoder Model
# -----------------------------
input_dim = X_train.shape[1]

model = keras.Sequential([
    keras.layers.Input(shape=(input_dim,)),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(input_dim, activation="linear")
])

model.compile(optimizer="adam", loss="mse")

# -----------------------------
# Train
# -----------------------------
history = model.fit(
    X_train, X_train,
    epochs=5,
    batch_size=256,
    validation_data=(X_test, X_test)
)

# -----------------------------
# Save model
# -----------------------------
model.save("models/autoencoder_toniot.h5")

print("\n✅ TON-IoT Autoencoder trained & saved!")