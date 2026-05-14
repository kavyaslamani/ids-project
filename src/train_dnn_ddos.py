import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

print("Loading data...")

X_train = pd.read_csv("data/X_train_ddos.csv").values
X_test = pd.read_csv("data/X_test_ddos.csv").values

y_train = pd.read_csv("data/y_train_ddos.csv").values.flatten()
y_test = pd.read_csv("data/y_test_ddos.csv").values.flatten()

print("Train shape:", X_train.shape)

# =========================
# Convert labels to categorical
# =========================
y_train_cat = to_categorical(y_train)
y_test_cat = to_categorical(y_test)

# =========================
# Build model
# =========================
model = Sequential()

model.add(Dense(64, activation="relu", input_shape=(X_train.shape[1],)))
model.add(Dense(32, activation="relu"))
model.add(Dense(y_train_cat.shape[1], activation="softmax"))

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("\nTraining DNN...")

model.fit(
    X_train,
    y_train_cat,
    epochs=10,
    batch_size=256,
    validation_split=0.2,
    verbose=1
)

# =========================
# Evaluate
# =========================
loss, acc = model.evaluate(X_test, y_test_cat)

print("\nTest Accuracy:", acc)

# =========================
# Save model
# =========================
model.save("models/dnn_ddos.h5")

print("\n✅ DNN model saved!")