import numpy as np
import pandas as pd
import joblib

from tensorflow.keras.models import load_model

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


print("=" * 70)
print("ADAPTIVE HYBRID IDS - MODEL EVALUATION")
print("=" * 70)


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test data...")

X_test = pd.read_csv(
    "data/X_test_combined.csv"
)

y_test = pd.read_csv(
    "data/y_test_combined.csv"
)


print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)


# ============================================================
# CONVERT TO NUMPY
# ============================================================

X = X_test.values.astype(float)

y = y_test.iloc[:, 0].values.astype(int)


# ============================================================
# LOAD MODEL + LABEL ENCODER
# ============================================================

print("\nLoading DNN model...")

model = load_model(
    "models/dnn_combined.h5"
)

label_encoder = joblib.load(
    "models/label_encoder_combined.pkl"
)


print(
    "Classes:",
    label_encoder.classes_.tolist()
)


# ============================================================
# IMPORTANT
# ============================================================
# X_test_combined.csv is already standardized.
#
# Therefore DO NOT apply scaler_combined.pkl again.
#
# ============================================================


print("\nRunning predictions...")

prediction = model.predict(
    X,
    verbose=1
)


y_pred = np.argmax(
    prediction,
    axis=1
)


# ============================================================
# OVERALL METRICS
# ============================================================

accuracy = accuracy_score(
    y,
    y_pred
)

precision = precision_score(
    y,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y,
    y_pred,
    average="weighted",
    zero_division=0
)

weighted_f1 = f1_score(
    y,
    y_pred,
    average="weighted",
    zero_division=0
)

macro_f1 = f1_score(
    y,
    y_pred,
    average="macro",
    zero_division=0
)


# ============================================================
# DISPLAY OVERALL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("OVERALL MODEL PERFORMANCE")
print("=" * 70)

print(
    f"Test Samples       : {len(y):,}"
)

print(
    f"Accuracy           : {accuracy * 100:.2f}%"
)

print(
    f"Weighted Precision : {precision * 100:.2f}%"
)

print(
    f"Weighted Recall    : {recall * 100:.2f}%"
)

print(
    f"Weighted F1 Score  : {weighted_f1 * 100:.2f}%"
)

print(
    f"Macro F1 Score     : {macro_f1 * 100:.2f}%"
)


# ============================================================
# PER CLASS PERFORMANCE
# ============================================================

print("\n")
print("=" * 70)
print("PER-CLASS PERFORMANCE")
print("=" * 70)

report = classification_report(
    y,
    y_pred,
    target_names=label_encoder.classes_,
    digits=4,
    zero_division=0
)

print(report)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n")
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

cm = confusion_matrix(
    y,
    y_pred
)

print(cm)


# ============================================================
# ACTUAL VS PREDICTED DISTRIBUTION
# ============================================================

print("\n")
print("=" * 70)
print("ACTUAL CLASS DISTRIBUTION")
print("=" * 70)

for i, count in enumerate(np.bincount(y)):
    if i < len(label_encoder.classes_):
        print(
            f"{label_encoder.classes_[i]:30s}: {count:,}"
        )


print("\n")
print("=" * 70)
print("PREDICTED CLASS DISTRIBUTION")
print("=" * 70)

pred_counts = np.bincount(
    y_pred,
    minlength=len(label_encoder.classes_)
)

for i, count in enumerate(pred_counts):

    print(
        f"{label_encoder.classes_[i]:30s}: {count:,}"
    )


print("\n")
print("=" * 70)
print("EVALUATION COMPLETE")
print("=" * 70)