import pandas as pd
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

print("Loading training data...")

X_train = pd.read_csv("data/X_train_botiot.csv").values

print("Shape:", X_train.shape)

# =========================
# Model
# =========================
input_dim = X_train.shape[1]

input_layer = Input(shape=(input_dim,))
encoded = Dense(8, activation="relu")(input_layer)
encoded = Dense(4, activation="relu")(encoded)

decoded = Dense(8, activation="relu")(encoded)
decoded = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(input_layer, decoded)

autoencoder.compile(optimizer="adam", loss="mse")

print("\nTraining autoencoder...")

autoencoder.fit(
    X_train,
    X_train,
    epochs=10,
    batch_size=128,
    validation_split=0.2,
    verbose=1
)

autoencoder.save("models/autoencoder_botiot.h5")

print("\n✅ Autoencoder saved!")