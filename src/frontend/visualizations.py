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

    exceeding_indices = [i for i, v in enumerate(values) if v > threshold]
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
    fig, ax = plt.subplots(figsize=(8, 5))

    values = historical_data['values']
    variable = historical_data['variable']
    unit = historical_data['unit']

    ax.hist(values, bins=10, color='skyblue', edgecolor='black', alpha=0.7)
    ax.axvline(x=threshold, color='r', linestyle='--', linewidth=2, label=f'Threshold ({threshold} {unit})')

    ax.set_xlabel(f'{variable} ({unit})', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title(f'{variable} Distribution', fontsize=14, fontweight='bold')
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
    df = pd.DataFrame([location])
    st.map(df, zoom=5)
