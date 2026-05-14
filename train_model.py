from sklearn.linear_model import LogisticRegression
import numpy as np
import joblib

# Simple training data
X = np.array([
    [1, 2],
    [2, 3],
    [3, 4],
    [10, 11],
    [11, 12],
    [12, 13]
])

# Labels
# 0 = Normal
# 1 = Attack
y = np.array([0, 0, 0, 1, 1, 1])

# Train model
model = LogisticRegression()
model.fit(X, y)

# Save model
joblib.dump(model, "ids_model.pkl")

print("Model trained and saved!")