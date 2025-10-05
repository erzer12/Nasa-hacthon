import streamlit as st
import requests
from datetime import datetime

def location_input():
    """
    Allows the user to select a location using Google Maps.
    Returns:
        Dictionary with 'lat' and 'lon' keys
    """
    st.sidebar.subheader("Location")
    st.sidebar.markdown(
        "Enter latitude and longitude manually, or search for a place name."
    )

    # Initialize session state
    if "lat" not in st.session_state:
        st.session_state.lat = 40.7128
    if "lon" not in st.session_state:
        st.session_state.lon = -74.0060

    # Place search
    place_name = st.sidebar.text_input("Search for a place (city, address, etc.)", "")
    if st.sidebar.button("Search") and place_name:
        import os
        api_key = st.secrets["google"].get("maps_api_key") if "google" in st.secrets and "maps_api_key" in st.secrets["google"] else os.environ.get("GOOGLE_MAPS_API_KEY")
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place_name}&key={api_key}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] == "OK":
                loc = data["results"][0]["geometry"]["location"]
                st.session_state.lat = loc["lat"]
                st.session_state.lon = loc["lng"]
            else:
                st.sidebar.error(f"No results found for '{place_name}'")
        else:
            st.sidebar.error("Failed to contact Google Geocoding API")

    # Manual lat/lon entry
    lat = st.sidebar.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=float(st.session_state.lat),
        step=0.0001,
        format="%.6f",
    )
    lon = st.sidebar.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=float(st.session_state.lon),
        step=0.0001,
        format="%.6f",
    )
    st.session_state.lat = lat
    st.session_state.lon = lon


    # Google Maps embed with marker at the selected location and zoomed in
    st.write("### 🌍 Selected Location")
    api_key = st.secrets["google"].get("maps_api_key") if "google" in st.secrets and "maps_api_key" in st.secrets["google"] else os.environ.get("GOOGLE_MAPS_API_KEY")
    map_url = (
        f"https://www.google.com/maps/embed/v1/place?key={api_key}"
        f"&q={lat},{lon}"
        f"&zoom=12"
        f"&maptype=roadmap"
    )
    st.components.v1.html(
        f'<iframe width="700" height="400" style="border:0" src="{map_url}" allowfullscreen></iframe>',
        height=400,
        width=700,
    )

    return {"lat": lat, "lon": lon}


def date_input():
    st.sidebar.subheader("Analysis Date")
    selected_date = st.sidebar.date_input(
        "Select Date",
        value=datetime.now().date(),
        min_value=datetime(2020, 1, 1).date(),
        # Allow any future date selection by omitting max_value
    )
    return selected_date.strftime("%Y-%m-%d")


def variable_selector():
    st.sidebar.subheader("Environmental Variables")
    variables = [
        "Temperature",
        "Precipitation",
        "Wind Speed",
        "Humidity",
    ]
    selected = st.sidebar.multiselect(
        "Select Variables to Analyze", options=variables, default=["Temperature", "Precipitation"]
    )
    return selected


def threshold_input(variable_name, default_value):
    threshold = st.number_input(
        f"Threshold for {variable_name}",
        value=float(default_value),
        step=1.0,
    )
    return threshold
