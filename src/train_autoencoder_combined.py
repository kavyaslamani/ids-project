import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping

print("Loading scaled train data...")
X_train = pd.read_csv("data/X_train_combined.csv").values

input_dim = X_train.shape[1]

# Build autoencoder
input_layer = Input(shape=(input_dim,))
encoded = Dense(32, activation="relu")(input_layer)
encoded = Dense(16, activation="relu")(encoded)

decoded = Dense(32, activation="relu")(encoded)
decoded = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)

autoencoder.compile(optimizer="adam", loss="mse")

print("Training autoencoder...")

early_stop = EarlyStopping(monitor="val_loss", patience=3)

autoencoder.fit(
    X_train, X_train,
    epochs=20,
    batch_size=256,
    validation_split=0.1,
    callbacks=[early_stop],
    verbose=1
)

# Save model
autoencoder.save("models/autoencoder_combined.h5")

print("✅ Autoencoder trained and saved")