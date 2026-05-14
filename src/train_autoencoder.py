import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report, confusion_matrix

# Load processed data
X_train = pd.read_csv("data/X_train_scaled.csv")
X_test = pd.read_csv("data/X_test_scaled.csv")
y_train = pd.read_csv("data/y_train.csv").squeeze()
y_test = pd.read_csv("data/y_test.csv").squeeze()

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)

# Keep only benign traffic for training
X_train_benign = X_train[y_train == 0]

print("Benign training samples:", X_train_benign.shape)

# Input dimension
input_dim = X_train.shape[1]

# Build Autoencoder
input_layer = Input(shape=(input_dim,))

encoded = Dense(64, activation="relu")(input_layer)
encoded = Dense(32, activation="relu")(encoded)
encoded = Dense(16, activation="relu")(encoded)

decoded = Dense(32, activation="relu")(encoded)
decoded = Dense(64, activation="relu")(decoded)
decoded = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)

# Compile model
autoencoder.compile(optimizer="adam", loss="mse")

# Train model
early_stop = EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)

history = autoencoder.fit(
    X_train_benign,
    X_train_benign,
    epochs=20,
    batch_size=256,
    shuffle=True,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# Save model
autoencoder.save("models/autoencoder.h5")
print("\nAutoencoder model saved as models/autoencoder.h5")

# Reconstruction error on test set
X_test_pred = autoencoder.predict(X_test)
mse = np.mean(np.power(X_test - X_test_pred, 2), axis=1)

# Threshold from benign training reconstruction error
X_train_pred = autoencoder.predict(X_train_benign)
train_mse = np.mean(np.power(X_train_benign - X_train_pred, 2), axis=1)

threshold = np.percentile(train_mse, 95)
print("\nAnomaly Threshold:", threshold)

# Predict anomalies
y_pred_anomaly = (mse > threshold).astype(int)

# Convert true labels to anomaly labels
# 0 = normal, 1 = attack
y_test_anomaly = (y_test != 0).astype(int)

print("\n=== AUTOENCODER ANOMALY DETECTION REPORT ===")
print(classification_report(y_test_anomaly, y_pred_anomaly))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test_anomaly, y_pred_anomaly))