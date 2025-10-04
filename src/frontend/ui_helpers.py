import streamlit as st
from datetime import datetime, timedelta

def location_input():
    """
    Creates input widgets for location (latitude and longitude).

    Returns:
        Dictionary with 'lat' and 'lon' keys
    """
    st.sidebar.subheader("Location")

    lat = st.sidebar.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=40.7128,
        step=0.0001,
        format="%.4f",
        help="Enter latitude (-90 to 90)"
    )

    lon = st.sidebar.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=-74.0060,
        step=0.0001,
        format="%.4f",
        help="Enter longitude (-180 to 180)"
    )

    return {'lat': lat, 'lon': lon}

def date_input():
    """
    Creates a date input widget.

    Returns:
        String date in 'YYYY-MM-DD' format
    """
    st.sidebar.subheader("Analysis Date")

    selected_date = st.sidebar.date_input(
        "Select Date",
        value=datetime.now().date(),
        min_value=datetime(2020, 1, 1).date(),
        max_value=datetime.now().date(),
        help="Select the end date for historical analysis"
    )

    return selected_date.strftime('%Y-%m-%d')

def variable_selector():
    """
    Creates a multi-select widget for environmental variables.

    Returns:
        List of selected variable names
    """
    st.sidebar.subheader("Environmental Variables")

    variables = [
        'Temperature',
        'Precipitation',
        'Wind Speed',
        'Humidity',
        'Air Quality Index',
        'Sea Level',
        'CO2 Levels'
    ]

    selected_variables = st.sidebar.multiselect(
        "Select Variables to Analyze",
        options=variables,
        default=['Temperature', 'Precipitation'],
        help="Choose one or more environmental variables"
    )

    return selected_variables

def threshold_input(variable_name, default_value):
    """
    Creates a threshold input widget for a specific variable.

    Args:
        variable_name: Name of the variable
        default_value: Default threshold value

    Returns:
        Float threshold value
    """
    threshold = st.number_input(
        f"Threshold for {variable_name}",
        value=float(default_value),
        step=1.0,
        help=f"Set the threshold value for {variable_name}"
    )

    return threshold
