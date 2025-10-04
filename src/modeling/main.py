# --- Real Statistical Modeling ---
import numpy as np
from scipy.stats import genextreme

def analyze_variable(historical_data, threshold):
    """
    Fits a General Extreme Value (GEV) distribution to the data and calculates exceedance probability and risk index.
    Args:
        historical_data: Dictionary containing 'values' key with list of data points
        threshold: The threshold value to compare against
    Returns:
        Dictionary containing:
            - probability: Float (0-100) representing probability of exceeding threshold
            - risk_index: Float (0-1) normalized risk score
            - mean: Mean of historical data
            - std: Standard deviation of historical data
            - max: Maximum value in historical data
            - min: Minimum value in historical data
    """
    values = np.array(historical_data['values'], dtype=float)
    values = values[~np.isnan(values)]  # Remove NaNs
    if len(values) == 0:
        return {
            'probability': 0.0,
            'risk_index': 0.0,
            'mean': float('nan'),
            'std': float('nan'),
            'max': float('nan'),
            'min': float('nan')
        }

    # Fit GEV distribution
    c, loc, scale = genextreme.fit(values)
    gev_dist = genextreme(c, loc=loc, scale=scale)
    prob = 1 - gev_dist.cdf(threshold)
    probability = float(np.clip(prob * 100, 0, 100))

    # Risk index: normalized location parameter (loc)
    # For simplicity, use a hardcoded min/max for normalization
    loc_min, loc_max = np.percentile(values, [5, 95])
    if loc_max > loc_min:
        risk_index = float(np.clip((loc - loc_min) / (loc_max - loc_min), 0, 1))
    else:
        risk_index = float(probability / 100)

    return {
        'probability': round(probability, 2),
        'risk_index': round(risk_index, 3),
        'mean': round(np.mean(values), 2),
        'std': round(np.std(values), 2),
        'max': round(np.max(values), 2),
        'min': round(np.min(values), 2)
    }
