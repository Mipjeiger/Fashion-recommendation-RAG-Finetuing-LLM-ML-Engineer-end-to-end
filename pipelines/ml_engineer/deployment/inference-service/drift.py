import numpy as np

# Replace with real training baseline later
BASELINE_MEAN = 0.0
BASELINE_STD = 1.0

def compute_drift(input_data: np.ndarray) -> float:
    """
    Compute the drift score using KL divergence between the input data distribution and the baseline distribution.
    
    Args:
        input_data (np.ndarray): The input data for which to compute the drift score."""
    
    current_mean = np.mean(input_data)
    current_std = np.std(input_data)

    baseline_dist = np.random.normal(loc=BASELINE_MEAN, scale=BASELINE_STD, size=1000)
    current_dist = np.random.normal(loc=current_mean, scale=current_std, size=1000)

    hist_base, _ = np.histogram(baseline_dist, bins=50, density=True)
    hist_curr, _ = np.histogram(current_dist, bins=50, density=True)

    hist_base += 1e-8  # Avoid zero probabilities
    hist_curr += 1e-8

    return float(np.sum(hist_base * np.log(hist_base / hist_curr)))