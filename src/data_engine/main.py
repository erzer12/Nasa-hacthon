# main.py

import os
import asyncio
import httpx
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression

load_dotenv()

# --- NASA POWER API variable mapping (UI name -> API variable, unit) ---
VARIABLE_MAP = {
    'Temperature': ('T2M', '°C'),
    'Precipitation': ('PRECTOTCORR', 'mm'),
    'Wind Speed': ('WS2M', 'm/s'),
    'Humidity': ('RH2M', '%'),
    'Temperature (Max)': ('T2M_MAX', '°C'),
    'Temperature (Min)': ('T2M_MIN', '°C'),
    'Precipitation (Daily)': ('PRECTOTCORR', 'mm'),
    'Wind Speed (Max)': ('WS2M_MAX', 'm/s'),
}


async def get_processed_data_async(selected_date, variable_name, location, nasa_api_key=None):
    """
    Fetch historical data for a given variable and location from NASA POWER API.
    Returns 30 historical data points (same day/month over last 30 years).
    Handles future prediction using linear regression if needed.
    """
    if nasa_api_key is None:
        nasa_api_key = os.environ.get('NASA_API_KEY')
    if not nasa_api_key:
        raise RuntimeError("NASA API key not set in environment variables or .env file.")

    var_id, unit = VARIABLE_MAP.get(variable_name, (None, 'units'))
    if var_id is None:
        # Return a placeholder for unmapped variables
        return {
            'dates': [],
            'values': [],
            'variable': variable_name,
            'location': location,
            'unit': unit,
            'message': f"Variable '{variable_name}' is not available from NASA POWER API."
        }

    # Parse date and location
    end_date = datetime.strptime(selected_date, '%Y-%m-%d')
    lat, lon = location['lat'], location['lon']

    # Prepare dates for the last 30 years
    today = datetime.today()
    is_future = end_date > today
    years = [end_date.year - i for i in range(29, -1, -1)]
    dates = [end_date.replace(year=year).strftime('%Y-%m-%d') for year in years]

    start_yyyymmdd = dates[0].replace('-', '')
    end_yyyymmdd = dates[-1].replace('-', '')

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={var_id}"
        f"&start={start_yyyymmdd}&end={end_yyyymmdd}"
        f"&latitude={lat}&longitude={lon}"
        f"&community=RE&format=JSON&user=demo&api_key={nasa_api_key}"
    )

    values = []
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            param_data = data['properties']['parameter'].get(var_id, {})

            for date_str in dates:
                val = param_data.get(date_str, np.nan)
                # Replace NASA fill value -999.0 with np.nan
                if val == -999.0:
                    val = np.nan
                values.append(val)
        except Exception as e:
            print(f"[NASA API ERROR] URL: {url}")
            print(f"[NASA API ERROR] Exception: {e}")
            values = [np.nan] * len(dates)

    # Future prediction using linear regression
    predicted_value = None
    if is_future:
        last_10_years = [(int(dates[-10 + i][:4]), v) for i, v in enumerate(values[-10:]) if not np.isnan(v)]
        if len(last_10_years) >= 2:
            years_arr = np.array([y for y, v in last_10_years]).reshape(-1, 1)
            vals_arr = np.array([v for y, v in last_10_years])
            model = LinearRegression().fit(years_arr, vals_arr)
            future_year = int(selected_date[:4])
            predicted_value = float(model.predict(np.array([[future_year]]))[0])
        elif last_10_years:
            predicted_value = float(np.mean([v for y, v in last_10_years]))

        # Optionally replace last value with prediction
        values[-1] = predicted_value if predicted_value is not None else np.nan

    # Convert NaNs to None for JSON serialization
    values = [None if np.isnan(v) else float(v) for v in values]

    result = {
        'dates': dates,
        'values': values,
        'variable': variable_name,
        'location': location,
        'unit': unit
    }
    if is_future:
        result['predicted_value'] = predicted_value

    return result


async def get_multiple_variables(selected_date, variable_names, location):
    """
    Fetch multiple environmental variables asynchronously.
    Returns a list of results dictionaries.
    """
    nasa_api_key = os.environ.get('NASA_API_KEY')
    tasks = [get_processed_data_async(selected_date, var, location, nasa_api_key) for var in variable_names]
    return await asyncio.gather(*tasks)
