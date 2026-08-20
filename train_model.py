import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from feature_extractor import convert_voltages_to_physics, estimate_dissolved_oxygen


def generate_synthetic_dataset(n_samples=3000):
    np.random.seed(42)

    # 1. Generate realistic physical features
    ntu = np.random.uniform(0, 1000, n_samples)          # Turbidity (NTU)
    tds = np.random.uniform(0, 2000, n_samples)          # Total Dissolved Solids (PPM)
    hue = np.random.uniform(0, 180, n_samples)           # HSV Hue (Color shift)
    sat = np.random.uniform(0, 255, n_samples)           # HSV Saturation (Color depth)
    val = np.random.uniform(0, 255, n_samples)           # HSV Value (Brightness)
    clarity = np.random.uniform(5, 500, n_samples)       # Laplacian Variance (Clarity)

    # 2. Compute synthetic Dissolved Oxygen (Method 2)
    do_list = []
    for i in range(n_samples):
        do_val = estimate_dissolved_oxygen(tds[i], ntu[i], hue[i], sat[i])
        do_list.append(do_val)
    do_est = np.array(do_list)

    # 3. Ground-Truth Target Formula (Pollution Score 0 to 100)
    score_ntu = (ntu / 1000.0) * 35.0                    
    score_tds = (tds / 2000.0) * 30.0                    
    score_do_penalty = np.clip((7.0 - do_est) / 6.5, 0, 1) * 25.0 
    score_visual = (sat / 255.0) * 10.0                  

    # Combine and bound target between 0 and 100
    y_pollution = np.clip(score_ntu + score_tds + score_do_penalty + score_visual, 0, 100)

    # 7D Feature Matrix
    X = np.column_stack((ntu, tds, do_est, hue, sat, val, clarity))

    return X, y_pollution


def train_and_save_model():
    print("Generating synthetic dataset based on WHO/EPA parameters...")
    X, y = generate_synthetic_dataset(n_samples=3000)

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)

    print("Training Random Forest Regression Engine...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate Model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n--- Model Evaluation ---")
    print(f"Mean Absolute Error (MAE): {mae:.2f} score points")
    print(f"R² Performance Score: {r2:.4f}")

    # Save model binary file
    output_filename = "hydromind_model.pkl"
    joblib.dump(model, output_filename)
    print(f"\nSuccessfully saved model to '{output_filename}'!")


if __name__ == "__main__":
    train_and_save_model()