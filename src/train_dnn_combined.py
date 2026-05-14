import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

print("Loading training data...")

X_train = pd.read_csv("data/X_train_combined.csv").values
y_train = pd.read_csv("data/y_train_combined.csv").values.flatten()

# Convert labels to one-hot
y_train_cat = to_categorical(y_train, num_classes=5)

# Build model
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(32, activation='relu'),
    Dense(5, activation='softmax')   # IMPORTANT: 5 classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("Training DNN...")

model.fit(X_train, y_train_cat, epochs=10, batch_size=256, validation_split=0.1)

# Save model
model.save("models/dnn_combined.h5")

print("✅ DNN trained and saved")