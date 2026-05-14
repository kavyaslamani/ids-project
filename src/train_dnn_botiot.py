import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

print("Loading data...")

X_train = pd.read_csv("data/X_train_botiot.csv").values
X_test = pd.read_csv("data/X_test_botiot.csv").values

y_train = pd.read_csv("data/y_train_botiot.csv").values.flatten()
y_test = pd.read_csv("data/y_test_botiot.csv").values.flatten()

# Convert labels
y_train_cat = to_categorical(y_train)
y_test_cat = to_categorical(y_test)

print("Train shape:", X_train.shape)

# =========================
# Model
# =========================
model = Sequential()

model.add(Dense(32, activation="relu", input_shape=(X_train.shape[1],)))
model.add(Dense(16, activation="relu"))
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
    batch_size=128,
    validation_split=0.2,
    verbose=1
)

# Evaluate
loss, acc = model.evaluate(X_test, y_test_cat)

print("\nTest Accuracy:", acc)

# Save
model.save("models/dnn_botiot.h5")

print("\n✅ DNN saved!")