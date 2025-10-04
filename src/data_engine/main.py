
# --- Real API Integration ---
import requests
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Meteomatics variable mapping (UI name -> API variable, unit)
VARIABLE_MAP = {
    'Temperature': ('t_2m:C', '°C'),
    'Precipitation': ('precip_24h:mm', 'mm'),
    'Wind Speed': ('wind_speed_10m:ms', 'm/s'),
    'Humidity': ('relative_humidity_2m:p', '%'),
    'Air Quality Index': ('air_quality_index:idx', 'AQI'),
    'Sea Level': ('msl_pressure:hpa', 'hPa'),
    'CO2 Levels': ('co2:ppm', 'ppm'),
    # Also support the more specific names if needed
    'Temperature (Max)': ('t_max_2m:C', '°C'),
    'Temperature (Min)': ('t_min_2m:C', '°C'),
    'Precipitation (Daily)': ('precip_24h:mm', 'mm'),
    'Wind Speed (Max)': ('wind_speed_max_10m:ms', 'm/s'),
}

def get_processed_data(selected_date, variable_name, location):
    """
    Fetches historical data for the given variable and location from Meteomatics API.
    Returns 30 historical data points for the same day/month over 30 years.
    Args:
        selected_date: The date selected by the user (YYYY-MM-DD)
        variable_name: The environmental variable (user-friendly name)
        location: Dictionary with 'lat' and 'lon' keys
    Returns:
        Dictionary containing:
            - dates: List of 30 dates (one per year)
            - values: List of 30 data points
            - variable: The variable name
            - location: The location dictionary
            - unit: The unit string
    """

    api_username = os.environ.get('METEOMATICS_USERNAME')
    api_key = os.environ.get('METEOMATICS_PASSWORD')
    if not api_username or not api_key:
        raise RuntimeError("Meteomatics credentials not set in environment variables or .env file.")

    # Map variable name
    var_id, unit = VARIABLE_MAP.get(variable_name, (None, 'units'))
    if var_id is None:
        raise ValueError(f"Variable '{variable_name}' not mapped to Meteomatics API.")

    # Parse date and location
    end_date = datetime.strptime(selected_date, '%Y-%m-%d')
    lat = location['lat']
    lon = location['lon']

    # Build list of dates: same day/month for each of the last 30 years
    dates = [(end_date.replace(year=end_date.year - i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
    values = []
    for date_str in dates:
        url = f"https://api.meteomatics.com/{date_str}T00:00:00Z/{var_id}/{lat},{lon}/json"
        try:
            resp = requests.get(url, auth=(api_username, api_key), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Extract value from response
            val = data['data'][0]['coordinates'][0]['dates'][0]['value']
            values.append(val)
        except Exception as e:
            values.append(np.nan)  # Use NaN for missing data

    return {
        'dates': dates,
        'values': np.array(values, dtype=float).tolist(),
        'variable': variable_name,
        'location': location,
        'unit': unit
    }
