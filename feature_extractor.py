import cv2
import numpy as np

def convert_voltages_to_physics(turb_v, cond_v):
    """
    Converts raw analog voltages from ESP32 ADC pins to standard physical units.
    - Turbidity: High voltage (~3.0V) = Clear Water (~0 NTU). Low voltage (~0.5V) = Murky (~1000 NTU).
    - Conductivity/TDS: Low voltage (~0.2V) = Low TDS (~0 PPM). High voltage (~3.0V) = High TDS (~2000 PPM).
    """
    turb_v_clamped = np.clip(turb_v, 0.5, 3.0)
    cond_v_clamped = np.clip(cond_v, 0.1, 3.0)

    # 1. Corrected Turbidity Transfer Curve (Inversely proportional to Voltage)
    # Voltage 3.0V -> 0 NTU | Voltage 0.5V -> 1000 NTU
    ntu_est = max(0.0, (3.0 - turb_v_clamped) * (1000.0 / 2.5))

    # 2. Corrected TDS Transfer Curve (Directly proportional to Voltage)
    # Voltage 0.1V -> 0 PPM | Voltage 3.0V -> 2000 PPM
    tds_est = max(0.0, (cond_v_clamped - 0.1) * (2000.0 / 2.9))

    return round(ntu_est, 2), round(tds_est, 2)


def estimate_dissolved_oxygen(tds_est, ntu_est, hue_mean, sat_mean, assumed_temp_c=25.0):
    """
    METHOD 2: Synthetic DO Estimator
    Combines thermodynamic solubility with optical & physical surrogate penalties.
    Returns: Estimated Dissolved Oxygen in mg/L.
    """
    # 1. Base Thermodynamic Saturation Limit at 25°C (Benson-Krause simplification)
    do_sat = 14.652 - (0.41022 * assumed_temp_c) + (0.0079910 * (assumed_temp_c ** 2)) - (0.000077774 * (assumed_temp_c ** 3))

    # 2. TDS Penalty (Salts reduce oxygen solubility)
    do_salinity_adjusted = do_sat * (1.0 - (0.000006 * tds_est))

    # 3. Turbidity / Particulate Depletion (Microbial decay consumes oxygen)
    turbidity_depletion = (ntu_est / 1000.0) * 2.5

    # 4. Optical Algae/Organic Penalty
    # Green/Yellow Hue in HSV space falls roughly between 35 and 85
    is_algae_hue = 1.0 if (35 <= hue_mean <= 85) else 0.0
    algae_depletion = is_algae_hue * (sat_mean / 255.0) * 2.0

    # Clamp DO output between 0.5 mg/L (hypoxic) and maximum thermodynamic limit
    estimated_do = max(0.5, do_salinity_adjusted - turbidity_depletion - algae_depletion)
    return round(estimated_do, 2)


def extract_visual_features(image_bytes):
    """
    Decodes JPEG image bytes and extracts HSV color metrics and Laplacian clarity.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Fallback default features if image is missing or corrupted
    if img is None:
        return [0.0, 0.0, 128.0, 50.0]

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue_mean = np.mean(hsv[:, :, 0])
    sat_mean = np.mean(hsv[:, :, 1])
    val_mean = np.mean(hsv[:, :, 2])

    # Measure image clarity / particulate blur using Laplacian Variance
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clarity_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    return [hue_mean, sat_mean, val_mean, clarity_var]