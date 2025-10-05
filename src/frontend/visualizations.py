import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_probability_trend(historical_data, threshold, analysis_result):
    """
    Plots the historical data trend with threshold line.

    Args:
        historical_data: Dictionary with 'dates', 'values', 'variable', 'unit'
        threshold: Threshold value
        analysis_result: Dictionary with analysis results
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    dates = historical_data['dates']
    values = historical_data['values']
    variable = historical_data['variable']
    unit = historical_data['unit']

    ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=4, label='Historical Data')
    ax.axhline(y=threshold, color='r', linestyle='--', linewidth=2, label=f'Threshold ({threshold} {unit})')

    exceeding_indices = [i for i, v in enumerate(values) if v is not None and v > threshold]
    if exceeding_indices:
        exceeding_dates = [dates[i] for i in exceeding_indices]
        exceeding_values = [values[i] for i in exceeding_indices]
        ax.scatter(exceeding_dates, exceeding_values, color='red', s=50, zorder=5, label='Exceeds Threshold')

    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{variable} ({unit})', fontsize=12, fontweight='bold')
    ax.set_title(f'{variable} Historical Trend', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45, ha='right')

    date_step = max(1, len(dates) // 6)
    ax.set_xticks(range(0, len(dates), date_step))
    ax.set_xticklabels([dates[i] for i in range(0, len(dates), date_step)])

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

def plot_histogram(historical_data, threshold):
    """
    Plots a histogram of the historical data with threshold line.

    Args:
        historical_data: Dictionary with 'values', 'variable', 'unit'
        threshold: Threshold value
    """
    import datetime
    values = historical_data['values']
    variable = historical_data['variable']
    unit = historical_data['unit']
    dates = historical_data.get('dates', [])

    # Determine if this is a future date (prediction)
    is_future = False
    if dates:
        try:
            last_date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d")
            is_future = last_date > datetime.datetime.now()
        except Exception:
            pass

    # For future dates, use only the last 10 years of data
    if is_future:
        values_to_plot = [v for v in values[-10:] if v is not None and not np.isnan(v)]
        hist_label = "(last 10 years used for prediction)"
    else:
        values_to_plot = [v for v in values if v is not None and not np.isnan(v)]
        hist_label = ""

    if not values_to_plot:
        st.warning(f"No data available to plot histogram for {variable}.")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(values_to_plot, bins=10, color='skyblue', edgecolor='black', alpha=0.7)
    ax.axvline(x=threshold, color='r', linestyle='--', linewidth=2, label=f'Threshold ({threshold} {unit})')
    ax.set_xlabel(f'{variable} ({unit})', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title(f'{variable} Distribution {hist_label}', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

def plot_map(location):
    """
    Displays a map with the selected location.

    Args:
        location: Dictionary with 'lat' and 'lon' keys
    """
    import os
    api_key = st.secrets["google"].get("maps_api_key") if "google" in st.secrets and "maps_api_key" in st.secrets["google"] else os.environ.get("GOOGLE_MAPS_API_KEY")
    lat = location.get('lat', 0)
    lon = location.get('lon', 0)
    # Use Google Maps embed with marker at the selected location
    map_url = (
        f"https://www.google.com/maps/embed/v1/place?key={api_key}"
        f"&q={lat},{lon}"
        f"&zoom=12"
        f"&maptype=roadmap"
    )
    st.write("### 🌍 Selected Location")
    st.components.v1.html(
        f'<iframe width="700" height="400" style="border:0" src="{map_url}" allowfullscreen></iframe>',
        height=400,
        width=700,
    )
