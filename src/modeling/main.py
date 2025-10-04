import numpy as np

def analyze_variable(historical_data, threshold):
    """
    Analyzes historical data against a threshold using simple statistical logic.
    Calculates the probability of exceeding the threshold and a normalized risk index.

    Args:
        historical_data: Dictionary containing 'values' key with list of data points
        threshold: The threshold value to compare against

    Returns:
        Dictionary containing:
            - probability: Float (0-100) representing percentage of points exceeding threshold
            - risk_index: Float (0-1) normalized risk score
            - mean: Mean of historical data
            - std: Standard deviation of historical data
            - max: Maximum value in historical data
            - min: Minimum value in historical data
    """
    values = np.array(historical_data['values'])

    points_exceeding = np.sum(values > threshold)
    total_points = len(values)
    probability = (points_exceeding / total_points) * 100

    mean_val = np.mean(values)
    std_val = np.std(values)
    max_val = np.max(values)
    min_val = np.min(values)

    if std_val > 0:
        z_score = abs((threshold - mean_val) / std_val)
        risk_index = min(probability / 100, 1.0)
    else:
        risk_index = 1.0 if mean_val > threshold else 0.0

    variability_factor = std_val / (mean_val + 1e-10)
    risk_index = min(risk_index * (1 + variability_factor * 0.5), 1.0)

    return {
        'probability': round(probability, 2),
        'risk_index': round(risk_index, 3),
        'mean': round(mean_val, 2),
        'std': round(std_val, 2),
        'max': round(max_val, 2),
        'min': round(min_val, 2)
    }
