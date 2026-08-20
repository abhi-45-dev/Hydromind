import joblib
import numpy as np
from feature_extractor import (
    convert_voltages_to_physics,
    estimate_dissolved_oxygen,
    extract_image_features
)

class HydromindEngine:
    def __init__(self, model_path="hydromind_model.pkl"):
        self.model = joblib.load(model_path)

    def predict_pollution_score(self, image_bytes, turbidity_v, temperature_c=25.0):
        # 1. Physical conversions
        ntu = convert_voltages_to_physics(turbidity_v)

        # 2. Visual feature extraction
        hue, sat, val, clarity = extract_image_features(image_bytes)

        # 3. Estimate Dissolved Oxygen
        do_est = estimate_dissolved_oxygen(temperature_c, ntu, hue, sat)

        # 4. Construct 7D feature vector
        features = np.array([[ntu, temperature_c, do_est, hue, sat, val, clarity]])

        # 5. Model prediction
        score = self.model.predict(features)[0]
        return int(np.clip(score, 0, 100))