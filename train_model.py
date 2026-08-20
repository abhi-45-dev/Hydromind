import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

np.random.seed(42)
num_samples = 3000

# 1. Generate realistic sensor values
turbidity_v = np.random.uniform(0.5, 3.0, num_samples)
temperature_c = np.random.uniform(15.0, 35.0, num_samples)

ntu = (3.0 - turbidity_v) * (1000.0 / 2.5)

# Visual features
hue = np.random.uniform(0, 180, num_samples)
sat = np.random.uniform(0, 255, num_samples)
val = np.random.uniform(0, 255, num_samples)
clarity = np.random.uniform(10, 500, num_samples)

# Synthetic DO calculation based on temperature
base_do = 14.6 - (0.33 * temperature_c) + (0.004 * (temperature_c ** 2))
do_est = np.maximum(1.0, base_do - (ntu / 1000.0) * 2.5)

# Calculate target pollution score (0-100)
score = (
    (ntu / 1000.0) * 50.0 +
    ((12.0 - do_est) / 11.0) * 30.0 +
    (sat / 255.0) * 20.0
)
score = np.clip(score, 0, 100)

# Build 7D feature matrix (NTU, Temperature, DO_est, Hue, Sat, Val, Clarity)
X = np.column_stack([ntu, temperature_c, do_est, hue, sat, val, clarity])
y = score

# Train Random Forest Regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model file
joblib.dump(model, "hydromind_model.pkl")
print("Successfully retrained and saved model as hydromind_model.pkl!")