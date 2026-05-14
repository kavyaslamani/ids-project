import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import save_model

print("Loading training data...")

X_train = pd.read_csv("data/X_train_ddos.csv").values

print("Data shape:", X_train.shape)

# =========================
# Autoencoder Architecture
# =========================
input_dim = X_train.shape[1]

input_layer = Input(shape=(input_dim,))
encoded = Dense(16, activation="relu")(input_layer)
encoded = Dense(8, activation="relu")(encoded)

decoded = Dense(16, activation="relu")(encoded)
decoded = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)

autoencoder.compile(optimizer="adam", loss="mse")

print("\nTraining autoencoder...")

autoencoder.fit(
    X_train,
    X_train,
    epochs=10,
    batch_size=256,
    validation_split=0.2,
    verbose=1
)

# =========================
# Save model
# =========================
autoencoder.save("models/autoencoder_ddos.h5")

print("\n✅ Autoencoder saved!")