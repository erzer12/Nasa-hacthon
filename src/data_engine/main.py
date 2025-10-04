import numpy as np
from datetime import datetime, timedelta

def get_processed_data(selected_date, variable_name, location):
    """
    Generates mock historical data for the given variable and location.
    Returns 30 historical data points simulated using normal distribution.

    Args:
        selected_date: The date selected by the user
        variable_name: The environmental variable (e.g., 'Temperature', 'Precipitation')
        location: Dictionary with 'lat' and 'lon' keys

    Returns:
        Dictionary containing:
            - dates: List of 30 dates leading up to selected_date
            - values: List of 30 simulated data points
            - variable: The variable name
            - location: The location dictionary
    """
    np.random.seed(hash(f"{variable_name}{location['lat']}{location['lon']}") % (2**32))

    variable_configs = {
        'Temperature': {'mean': 20, 'std': 5, 'unit': '°C'},
        'Precipitation': {'mean': 50, 'std': 20, 'unit': 'mm'},
        'Wind Speed': {'mean': 15, 'std': 5, 'unit': 'km/h'},
        'Humidity': {'mean': 60, 'std': 15, 'unit': '%'},
        'Air Quality Index': {'mean': 75, 'std': 25, 'unit': 'AQI'},
        'Sea Level': {'mean': 0, 'std': 0.5, 'unit': 'm'},
        'CO2 Levels': {'mean': 410, 'std': 10, 'unit': 'ppm'},
    }

    config = variable_configs.get(variable_name, {'mean': 50, 'std': 15, 'unit': 'units'})

    values = np.random.normal(config['mean'], config['std'], 30)
    values = np.maximum(values, 0)

    end_date = datetime.strptime(selected_date, '%Y-%m-%d')
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]

    return {
        'dates': dates,
        'values': values.tolist(),
        'variable': variable_name,
        'location': location,
        'unit': config['unit']
    }
