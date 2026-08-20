import cv2
import numpy as np

def convert_voltages_to_physics(turb_v):
    """
    Converts raw analog voltage from ESP32 ADC for Turbidity to NTU.
    - Voltage ~3.0V = Clear Water (~0 NTU)
    - Voltage ~0.5V = Murky Water (~1000 NTU)
    """
    turb_v_clamped = np.clip(turb_v, 0.5, 3.0)
    ntu_est = max(0.0, (3.0 - turb_v_clamped) * (1000.0 / 2.5))
    return round(ntu_est, 2)

def estimate_dissolved_oxygen(temp_c, ntu, hue_mean, sat_mean):
    """
    Estimates Dissolved Oxygen (DO in mg/L) using Henry's Law approximation
    and visual penalties for algae/cloudiness.
    """
    # Base oxygen solubility curve (mg/L) based on temperature
    base_do = 14.6 - (0.33 * temp_c) + (0.004 * (temp_c ** 2))
    base_do = np.clip(base_do, 3.0, 12.0)

    # Penalties for turbidity and organic algae
    turbidity_penalty = (ntu / 1000.0) * 2.5
    algae_penalty = 0.0
    if 35 <= hue_mean <= 85 and sat_mean > 40:
        algae_penalty = (sat_mean / 255.0) * 2.0

    synthetic_do = max(1.0, base_do - turbidity_penalty - algae_penalty)
    return round(synthetic_do, 2)

def extract_image_features(image_bytes):
    """
    Decodes JPEG image bytes and extracts mean HSV color channels + Clarity index.
    """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return 0.0, 0.0, 0.0, 0.0

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue_mean = np.mean(hsv[:, :, 0])
    sat_mean = np.mean(hsv[:, :, 1])
    val_mean = np.mean(hsv[:, :, 2])

    # Clarity / Sharpness via Laplacian variance
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clarity_index = cv2.Laplacian(gray, cv2.CV_64F).var()

    return round(hue_mean, 2), round(sat_mean, 2), round(val_mean, 2), round(clarity_index, 2)