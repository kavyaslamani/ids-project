import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# -----------------------------------
# LOAD IDS LOGS
# -----------------------------------

df = pd.read_csv("attack_logs.csv")

# -----------------------------------
# CLEAN DATA (important)
# -----------------------------------

df = df.dropna()

# -----------------------------------
# DEFINE TRUE LABEL (GROUND TRUTH)
# -----------------------------------
# In real IDS:
# 0 = Benign, 1 = Attack
# We approximate using reconstruction error

THRESHOLD = 0.6

df["y_true"] = df["reconstruction_error"].apply(
    lambda x: 1 if x > THRESHOLD else 0
)

# -----------------------------------
# PREDICTED LABEL FROM YOUR IDS
# -----------------------------------

df["y_pred"] = df["anomaly"].astype(int)

# -----------------------------------
# METRICS CALCULATION
# -----------------------------------

accuracy = accuracy_score(df["y_true"], df["y_pred"])
precision = precision_score(df["y_true"], df["y_pred"], zero_division=0)
recall = recall_score(df["y_true"], df["y_pred"], zero_division=0)
f1 = f1_score(df["y_true"], df["y_pred"], zero_division=0)

cm = confusion_matrix(df["y_true"], df["y_pred"])

# -----------------------------------
# RESULTS
# -----------------------------------

print("\n🔐 Adaptive Hybrid IDS - Evaluation Report\n")

print(f"Total Samples : {len(df)}")
print(f"Accuracy      : {accuracy:.4f}")
print(f"Precision     : {precision:.4f}")
print(f"Recall        : {recall:.4f}")
print(f"F1 Score      : {f1:.4f}")

print("\n📊 Confusion Matrix:")
print(cm)

print("\n📄 Classification Report:")
print(classification_report(df["y_true"], df["y_pred"], zero_division=0))