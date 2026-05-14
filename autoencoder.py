import pandas as pd
import numpy as np

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

# =========================
# LOAD TRAINING DATA
# =========================

X_train = pd.read_csv("data/X_train.csv")

print("\nTraining Data Shape:")
print(X_train.shape)

# =========================
# USE ONLY NORMAL TRAFFIC
# =========================

# Since:
# 0 = Benign

y_train = pd.read_csv("data/y_train.csv")

normal_index = y_train.iloc[:, 0] == 0

X_train_normal = X_train[normal_index]

print("\nNormal Traffic Shape:")
print(X_train_normal.shape)

# =========================
# AUTOENCODER ARCHITECTURE
# =========================

input_dim = X_train_normal.shape[1]

input_layer = Input(shape=(input_dim,))

# Encoder
encoder = Dense(32, activation="relu")(input_layer)
encoder = Dense(16, activation="relu")(encoder)

# Decoder
decoder = Dense(32, activation="relu")(encoder)
decoder = Dense(input_dim, activation="linear")(decoder)

# Build model
autoencoder = Model(inputs=input_layer, outputs=decoder)

# Compile
autoencoder.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="mse"
)

# =========================
# TRAIN MODEL
# =========================

history = autoencoder.fit(
    X_train_normal,
    X_train_normal,
    epochs=10,
    batch_size=256,
    validation_split=0.2,
    shuffle=True
)

# =========================
# SAVE MODEL
# =========================

autoencoder.save("autoencoder_model.h5")

print("\nAutoencoder Trained Successfully!")