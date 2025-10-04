

import os
import asyncio
import httpx
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression

load_dotenv()

"""
NASA Hackathon Data Engine
Hybrid backend for async weather/climate data fetching from NASA POWER, GES DISC OPeNDAP, and Meteomatics (fallback).
Caches all results in /data/cache/.
"""
import os
import asyncio
import httpx
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
from dotenv import load_dotenv

load_dotenv()

# --- Variable mapping (UI name -> (NASA var, unit, Meteomatics var, GES DISC var)) ---
VARIABLE_MAP = {
    'Temperature':      ('T2M', '°C', 't_2m:C', None),
    'Precipitation':    ('PRECTOTCORR', 'mm', 'precip_24h:mm', None),
    'Wind Speed':       ('WS2M', 'm/s', 'wind_speed_10m:ms', None),
    'Humidity':         ('RH2M', '%', 'relative_humidity_2m:p', None),
}

# --- Caching helpers ---
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def cache_path(lat, lon, variable, date, source):
    safe_var = variable.replace(" ", "_")
    return CACHE_DIR / f"{safe_var}_{lat:.4f}_{lon:.4f}_{date}_{source}.parquet"

def cache_save(lat, lon, variable, date, data, source):
    path = cache_path(lat, lon, variable, date, source)
    df = pd.DataFrame({"dates": data["dates"], "values": data["values"]})
    df.to_parquet(path, index=False)

def cache_load(lat, lon, variable, date, source):
    path = cache_path(lat, lon, variable, date, source)
    if path.exists():
        df = pd.read_parquet(path)
        return {
            "dates": df["dates"].tolist(),
            "values": df["values"].tolist(),
        }
    return None





# --- Meteomatics API ---
async def fetch_meteomatics_data(lat, lon, date, variable):
    """Fetch daily data from Meteomatics API for the last 30 years for a variable."""
    _, unit, meteomatics_var, _ = VARIABLE_MAP.get(variable, (None, None, None, None))
    if not meteomatics_var:
        return None
    user = os.environ.get("METEOMATICS_USERNAME")
    pw = os.environ.get("METEOMATICS_PASSWORD")
    end_date = datetime.strptime(date, '%Y-%m-%d')
    years = [end_date.year - i for i in range(29, -1, -1)]
    dates = [end_date.replace(year=year).strftime('%Y-%m-%d') for year in years]
    start = dates[0] + "T00:00:00Z"
    end = dates[-1] + "T00:00:00Z"
    url = (
        f"https://api.meteomatics.com/{start}--{end}:P1Y/{meteomatics_var}/{lat},{lon}/json"
    )
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, auth=(user, pw), timeout=15)
            resp.raise_for_status()
            data = resp.json()
            timeseries = data['data'][0]['coordinates'][0]['dates']
            values = [d['value'] for d in timeseries]
            dates = [d['date'][:10] for d in timeseries]
            return {
                "dates": dates,
                "values": [None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v) for v in values],
                "variable": variable,
                "unit": unit,
                "source": "Meteomatics"
            }
        except Exception as e:
            print(f"Meteomatics API error for {variable}: {e}")
            return None




# --- Main async data fetch (Meteomatics only) ---
async def get_processed_data_async(selected_date, variable_name, location):
    """Fetch data for a variable at a location and date using Meteomatics only."""
    lat, lon = float(location['lat']), float(location['lon'])
    # If variable is not mapped to Meteomatics, return empty result with message
    if variable_name not in VARIABLE_MAP or VARIABLE_MAP[variable_name][2] is None:
        print(f"Variable '{variable_name}' not available from Meteomatics.")
        return {
            "dates": [],
            "values": [],
            "variable": variable_name,
            "unit": None,
            "source": "Unavailable",
            "message": f"Variable '{variable_name}' is not available from Meteomatics API."
        }
    # 1. Try cache for Meteomatics
    meteo_cache = cache_load(lat, lon, variable_name, selected_date, "meteomatics")
    if meteo_cache:
        print(f"Loaded {variable_name} from Meteomatics cache.")
        return {
            **meteo_cache,
            "variable": variable_name,
            "unit": VARIABLE_MAP[variable_name][1],
            "source": "Meteomatics (cache)"
        }
    # 2. Fetch Meteomatics
    data_meteo = await fetch_meteomatics_data(lat, lon, selected_date, variable_name)
    if data_meteo and any(v is not None for v in data_meteo["values"]):
        cache_save(lat, lon, variable_name, selected_date, data_meteo, "meteomatics")
        print(f"Fetched {variable_name} from Meteomatics API.")
        return data_meteo
    # 3. If all fail, return empty
    print(f"No data available for {variable_name} from Meteomatics.")
    return {
        "dates": [],
        "values": [],
        "variable": variable_name,
        "unit": VARIABLE_MAP[variable_name][1],
        "source": "Unavailable"
    }

async def get_multiple_variables(selected_date, variable_names, location):
    """Fetch multiple variables in parallel."""
    tasks = [get_processed_data_async(selected_date, var, location) for var in variable_names]
    return await asyncio.gather(*tasks)
