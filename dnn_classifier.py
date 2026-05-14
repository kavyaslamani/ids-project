import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical

# ======================================
# LOAD DATASET
# ======================================

print("\nLoading Dataset...")

df = pd.read_csv("data/cleaned_combined.csv")

print("\nDataset Loaded:", df.shape)

# ======================================
# PREPROCESSING
# ======================================

# Remove Timestamp if exists
if "Timestamp" in df.columns:
    df = df.drop("Timestamp", axis=1)

# Remove missing values
df = df.dropna()

# Separate features and labels
X = df.drop("Label", axis=1)
y = df["Label"]

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

print("\nTraining Shape:", X_train.shape)
print("Testing Shape:", X_test.shape)

# ======================================
# CLASS WEIGHTS
# ======================================

print("\nCalculating Class Weights...")

class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)

class_weights = dict(enumerate(class_weights))

print("\nClass Weights:")
print(class_weights)

# ======================================
# ONE HOT ENCODING
# ======================================

y_train_cat = to_categorical(y_train)
y_test_cat = to_categorical(y_test)

# ======================================
# BUILD DNN MODEL
# ======================================

print("\nBuilding DNN Model...")

model = Sequential()

model.add(Dense(128, activation='relu', input_shape=(X_train.shape[1],)))
model.add(Dropout(0.3))

model.add(Dense(64, activation='relu'))
model.add(Dropout(0.3))

model.add(Dense(32, activation='relu'))

model.add(Dense(len(np.unique(y_train)), activation='softmax'))

# ======================================
# COMPILE MODEL
# ======================================

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ======================================
# TRAIN MODEL
# ======================================

print("\nTraining DNN Model...")

history = model.fit(
    X_train,
    y_train_cat,
    epochs=10,
    batch_size=256,
    validation_data=(X_test, y_test_cat),
    class_weight=class_weights
)

# ======================================
# SAVE MODEL
# ======================================

model.save("dnn_classifier.h5")

print("\nDNN Attack Classifier Trained Successfully!")