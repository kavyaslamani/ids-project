import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

print("Loading TON-IoT data...")

X_train = pd.read_csv("data/X_train_toniot.csv").values
X_test = pd.read_csv("data/X_test_toniot.csv").values
y_train = pd.read_csv("data/y_train_toniot.csv").values.ravel()
y_test = pd.read_csv("data/y_test_toniot.csv").values.ravel()

print("Shapes loaded:", X_train.shape, X_test.shape)

# -----------------------------
# Label Encoding (important)
# -----------------------------
le = LabelEncoder()
y_train_enc = le.fit_transform(y_train)
y_test_enc = le.transform(y_test)

num_classes = len(np.unique(y_train_enc))

# -----------------------------
# DNN Model
# -----------------------------
model = keras.Sequential([
    keras.layers.Input(shape=(X_train.shape[1],)),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dense(64, activation="relu"),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(num_classes, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# -----------------------------
# Train
# -----------------------------
model.fit(
    X_train, y_train_enc,
    epochs=5,
    batch_size=256,
    validation_data=(X_test, y_test_enc)
)

# -----------------------------
# Predictions
# -----------------------------
y_pred = np.argmax(model.predict(X_test), axis=1)

print("\n=== TON-IoT DNN REPORT ===")
print(classification_report(y_test_enc, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test_enc, y_pred))

# -----------------------------
# Save model
# -----------------------------
model.save("models/dnn_toniot.h5")

print("\n✅ TON-IoT DNN trained & saved!")