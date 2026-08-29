import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Model

# -------------------------
# LOAD DATASET
# -------------------------

print("Loading Dataset...")


df = pd.read_csv("data/cleaned_02-14-2018.csv")

# Use a subset for faster training
df = df.sample(n=200000, random_state=42)

print(df.shape)

print(df.shape)

# -------------------------
# LABELS
# -------------------------

X = df.drop("Label", axis=1)

y = df["Label"]

# -------------------------
# ENCODE LABELS
# -------------------------

encoder = LabelEncoder()

y = encoder.fit_transform(y)

# -------------------------
# SCALE FEATURES
# -------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(encoder, "models/label_encoder.pkl")

# -------------------------
# TRAIN TEST
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42
)

print("Training Samples :", len(X_train))
print("Testing Samples  :", len(X_test))

# -------------------------
# AUTOENCODER
# -------------------------

input_dim = X_train.shape[1]

autoencoder = Sequential([
    Dense(64, activation="relu", input_shape=(input_dim,)),
    Dense(32, activation="relu"),
    Dense(16, activation="relu"),
    Dense(32, activation="relu"),
    Dense(64, activation="relu"),
    Dense(input_dim)
])

autoencoder.compile(
    optimizer="adam",
    loss="mse"
)

print("Training Autoencoder...")

autoencoder.fit(
    X_train,
    X_train,
    epochs=15,
    batch_size=512,
    validation_split=0.2
)

autoencoder.save("models/autoencoder.h5")

# -------------------------
# DNN
# -------------------------

classifier = Sequential([
    Dense(128, activation="relu", input_shape=(input_dim,)),
    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense(len(np.unique(y)), activation="softmax")
])

classifier.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

print("Training Classifier...")

classifier.fit(
    X_train,
    y_train,
    epochs=15,
    batch_size=512,
    validation_split=0.2
)

classifier.save("models/dnn_classifier.h5")

print("\nTRAINING COMPLETED")