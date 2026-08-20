import joblib
import numpy as np
from feature_extractor import (
    convert_voltages_to_physics,
    estimate_dissolved_oxygen,
    extract_visual_features
)

class HydromindEngine:
    def __init__(self, model_path="hydromind_model.pkl"):
        """Loads the pre-trained Pickle model into memory upon initialization."""
        try:
            self.model = joblib.load(model_path)
            print(f"Successfully loaded model from '{model_path}'!")
        except Exception as e:
            raise RuntimeError(f"Failed to load model binary '{model_path}': {str(e)}")

    def predict_pollution_score(self, image_bytes, turbidity_v, conductivity_v):
        """
        Main interface function.
        Inputs:
            - image_bytes: Raw JPEG bytes from camera
            - turbidity_v: Analog voltage float from Turbidity probe
            - conductivity_v: Analog voltage float from TDS probe
        Returns:
            - pollution_score: Integer from 0 (Pristine) to 100 (Hazardous)
        """
        # 1. Physics conversions
        ntu_est, tds_est = convert_voltages_to_physics(turbidity_v, conductivity_v)

        # 2. Extract optical features
        visual_feats = extract_visual_features(image_bytes)
        hue_mean, sat_mean = visual_feats[0], visual_feats[1]

        # 3. Calculate Method 2 Synthetic Dissolved Oxygen
        do_est = estimate_dissolved_oxygen(tds_est, ntu_est, hue_mean, sat_mean)

        # 4. Construct 7D Feature Vector
        feature_vector = np.array([[ntu_est, tds_est, do_est] + visual_feats])

        # 5. ML Model Inference
        raw_score = self.model.predict(feature_vector)[0]

        # Clamp output strictly between 0 and 100
        pollution_score = int(np.clip(round(raw_score), 0, 100))
        return pollution_score


# Quick local test block
if __name__ == "__main__":
    import cv2

    print("\n--- Testing Hydromind Master Engine ---")
    engine = HydromindEngine()

    # Generate a dummy black JPEG frame for testing
    dummy_img = np.zeros((200, 200, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', dummy_img)
    test_image_bytes = encoded.tobytes()

    # Test Case 1: Clean Water Inputs
    score_clean = engine.predict_pollution_score(
        image_bytes=test_image_bytes,
        turbidity_v=2.8,       # High voltage = Clear water
        conductivity_v=0.4     # Low voltage = Low dissolved solids
    )
    print(f"Clean Water Simulation -> Pollution Score: {score_clean} / 100")

    # Test Case 2: Dirty / Salty Water Inputs
    score_dirty = engine.predict_pollution_score(
        image_bytes=test_image_bytes,
        turbidity_v=0.8,       # Low voltage = Murky water
        conductivity_v=2.5     # High voltage = High dissolved solids
    )
    print(f"Contaminated Water Simulation -> Pollution Score: {score_dirty} / 100")