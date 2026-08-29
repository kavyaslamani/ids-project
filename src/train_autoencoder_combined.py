import pandas as pd
import numpy as np
import joblib

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping

print("Loading scaled train data...")

X_train = pd.read_csv(
    "data/X_train_combined.csv"
).values

input_dim = X_train.shape[1]

print("Training data shape:", X_train.shape)
print("Input dimension:", input_dim)

# ==========================================
# BUILD AUTOENCODER
# ==========================================

input_layer = Input(shape=(input_dim,))

encoded = Dense(32, activation="relu")(input_layer)
encoded = Dense(16, activation="relu")(encoded)

decoded = Dense(32, activation="relu")(encoded)
decoded = Dense(
    input_dim,
    activation="linear"
)(decoded)

autoencoder = Model(
    inputs=input_layer,
    outputs=decoded
)

autoencoder.compile(
    optimizer="adam",
    loss="mse"
)

# ==========================================
# TRAIN
# ==========================================

print("Training autoencoder...")

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True
)

autoencoder.fit(
    X_train,
    X_train,
    epochs=20,
    batch_size=256,
    validation_split=0.1,
    callbacks=[early_stop],
    verbose=1
)

# ==========================================
# CALCULATE TRAINING RECONSTRUCTION ERROR
# ==========================================

print("Calculating reconstruction errors...")

reconstructed = autoencoder.predict(
    X_train,
    verbose=1
)

mse = np.mean(
    np.square(
        X_train - reconstructed
    ),
    axis=1
)

print()
print("==========================================")
print("RECONSTRUCTION ERROR STATISTICS")
print("==========================================")
print("Min:", np.min(mse))
print("Mean:", np.mean(mse))
print("Median:", np.median(mse))
print("95th percentile:", np.percentile(mse, 95))
print("99th percentile:", np.percentile(mse, 99))
print("Max:", np.max(mse))

# ==========================================
# ANOMALY THRESHOLD
# ==========================================

threshold = float(
    np.percentile(mse, 95)
)

print()
print("==========================================")
print("ANOMALY THRESHOLD")
print("==========================================")
print("Threshold:", threshold)

# Save threshold
joblib.dump(
    threshold,
    "models/autoencoder_threshold_combined.pkl"
)

# ==========================================
# SAVE MODEL
# ==========================================

autoencoder.save(
    "models/autoencoder_combined.h5"
)

print()
print("✅ Autoencoder trained and saved")
print("✅ Threshold saved")