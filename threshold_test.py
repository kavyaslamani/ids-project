import numpy as np
import pandas as pd
import joblib
import tensorflow as tf


# ============================================================
# LOAD TEST DATA
# ============================================================

X = pd.read_csv(
    "data/X_test_combined.csv"
)

print()
print("==============================================")
print("AUTOENCODER THRESHOLD CALIBRATION")
print("==============================================")
print(
    f"Test samples: {len(X):,}"
)
print(
    f"Test features: {X.shape[1]}"
)


# ============================================================
# LOAD SCALER
# ============================================================

scaler = joblib.load(
    "models/scaler_combined.pkl"
)


# ============================================================
# FIX FEATURE NAMES
# ============================================================

if hasattr(scaler, "feature_names_in_"):

    expected_features = list(
        scaler.feature_names_in_
    )

    print(
        f"Scaler expects: {len(expected_features)} features"
    )

    if X.shape[1] != len(expected_features):

        raise ValueError(
            f"Feature mismatch. "
            f"CSV has {X.shape[1]} features, "
            f"but scaler expects "
            f"{len(expected_features)} features."
        )

    X_for_scaler = pd.DataFrame(
        X.values,
        columns=expected_features
    )

else:

    X_for_scaler = X.values


# ============================================================
# LOAD AUTOENCODER
# ============================================================

print()
print("Loading Autoencoder...")

autoencoder = tf.keras.models.load_model(
    "models/autoencoder_combined.h5",
    compile=False
)


# ============================================================
# SCALE DATA
# ============================================================

print(
    "Scaling test data..."
)

X_scaled = scaler.transform(
    X_for_scaler
)


# ============================================================
# AUTOENCODER PREDICTION
# ============================================================

print(
    "Running Autoencoder..."
)

reconstructed = autoencoder.predict(
    X_scaled,
    verbose=1
)


# ============================================================
# RECONSTRUCTION ERROR
# ============================================================

errors = np.mean(
    np.square(
        X_scaled - reconstructed
    ),
    axis=1
)


# ============================================================
# ERROR STATISTICS
# ============================================================

print()
print("==============================================")
print("RECONSTRUCTION ERROR ANALYSIS")
print("==============================================")

print(
    f"Minimum : {np.min(errors):.6f}"
)

print(
    f"Maximum : {np.max(errors):.6f}"
)

print(
    f"Mean    : {np.mean(errors):.6f}"
)

print(
    f"Median  : {np.median(errors):.6f}"
)

print(
    f"90th %  : {np.percentile(errors, 90):.6f}"
)

print(
    f"95th %  : {np.percentile(errors, 95):.6f}"
)

print(
    f"97.5 %  : {np.percentile(errors, 97.5):.6f}"
)

print(
    f"99th %  : {np.percentile(errors, 99):.6f}"
)

print(
    f"99.5 %  : {np.percentile(errors, 99.5):.6f}"
)

print(
    f"99.9 %  : {np.percentile(errors, 99.9):.6f}"
)


# ============================================================
# TEST DIFFERENT THRESHOLDS
# ============================================================

thresholds = [
    0.5,
    0.75,
    1.0,
    1.25,
    1.5,
    2.0,
    2.5,
    3.0,
    4.0,
    5.0
]


print()
print("==============================================")
print("THRESHOLD COMPARISON")
print("==============================================")

for threshold in thresholds:

    anomaly_count = int(
        np.sum(
            errors > threshold
        )
    )

    anomaly_rate = (
        anomaly_count /
        len(errors)
    ) * 100

    print(
        f"Threshold {threshold:<5} | "
        f"Anomalies: {anomaly_count:>8,} | "
        f"Rate: {anomaly_rate:>6.2f}%"
    )


# ============================================================
# SAVE RECONSTRUCTION ERRORS
# ============================================================

result = pd.DataFrame(
    {
        "reconstruction_error": errors
    }
)

result.to_csv(
    "data/reconstruction_errors.csv",
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("==============================================")
print("CALIBRATION COMPLETED")
print("==============================================")

print(
    "Saved: data/reconstruction_errors.csv"
)