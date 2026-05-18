
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib

# ---------------------------------
# GENERATE SAMPLE DATA
# ---------------------------------

rows = 5000

X = np.random.rand(rows, 10) * 100

labels = np.random.choice(

    [
        "Normal Traffic",
        "DDoS Attack",
        "Botnet Attack",
        "Reconnaissance",
        "Brute Force"
    ],

    rows

)

# ---------------------------------
# LABEL ENCODER
# ---------------------------------

label_encoder = LabelEncoder()

y = label_encoder.fit_transform(labels)

# ---------------------------------
# SCALER
# ---------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# ---------------------------------
# SPLIT
# ---------------------------------

X_train, X_test, y_train, y_test = train_test_split(

    X_scaled,
    y,

    test_size=0.2,

    random_state=42

)

# ---------------------------------
# AUTOENCODER
# ---------------------------------

autoencoder = Sequential([

    Dense(8, activation='relu', input_shape=(10,)),

    Dense(4, activation='relu'),

    Dense(8, activation='relu'),

    Dense(10, activation='linear')

])

autoencoder.compile(

    optimizer='adam',

    loss='mse'

)

autoencoder.fit(

    X_train,
    X_train,

    epochs=10,

    batch_size=32,

    validation_split=0.2,

    verbose=1

)

# ---------------------------------
# DNN CLASSIFIER
# ---------------------------------

dnn_model = Sequential([

    Dense(32, activation='relu', input_shape=(10,)),

    Dense(16, activation='relu'),

    Dense(len(label_encoder.classes_), activation='softmax')

])

dnn_model.compile(

    optimizer='adam',

    loss='sparse_categorical_crossentropy',

    metrics=['accuracy']

)

dnn_model.fit(

    X_train,
    y_train,

    epochs=10,

    batch_size=32,

    validation_split=0.2,

    verbose=1

)

# ---------------------------------
# SAVE EVERYTHING
# ---------------------------------

autoencoder.save("autoencoder.h5")

dnn_model.save("dnn_model.h5")

joblib.dump(

    scaler,

    "scaler.pkl"

)

joblib.dump(

    label_encoder,

    "label_encoder.pkl"

)

print("\n✅ TRAINING COMPLETE")
print("✅ MODELS SAVED")

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

# ---------------------------------
# PREDICTIONS
# ---------------------------------

predictions = dnn_model.predict(X_test)

y_pred = np.argmax(predictions, axis=1)

# ---------------------------------
# METRICS
# ---------------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    average='weighted'
)

recall = recall_score(
    y_test,
    y_pred,
    average='weighted'
)

f1 = f1_score(
    y_test,
    y_pred,
    average='weighted'
)

# ---------------------------------
# PRINT RESULTS
# ---------------------------------

print("\n📊 MODEL EVALUATION")

print(f"Accuracy  : {accuracy:.4f}")

print(f"Precision : {precision:.4f}")

print(f"Recall    : {recall:.4f}")

print(f"F1-Score  : {f1:.4f}")
