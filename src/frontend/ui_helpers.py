import streamlit as st
from datetime import datetime
from streamlit_folium import st_folium
import folium


def location_input():
    """
    Allows the user to select a location by clicking on a map or entering coordinates.
    Returns:
        Dictionary with 'lat' and 'lon' keys
    """
    st.sidebar.subheader("Location")
    st.sidebar.markdown("Enter latitude and longitude, or search by place name, and see the location on the map.")

    # Place name search
    place_name = st.sidebar.text_input("Search for a place (city, address, etc.)", "")
    search = st.sidebar.button("Search")

    # Session state for lat/lon
    if 'lat' not in st.session_state:
        st.session_state.lat = 40.7128
    if 'lon' not in st.session_state:
        st.session_state.lon = -74.0060

    # If search is clicked, use Google Geocoding API
    if search and place_name:
        import requests
        api_key = st.secrets["GOOGLE_GEOCODE_API_KEY"]
        if api_key:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place_name}&key={api_key}"
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data['status'] == 'OK':
                    loc = data['results'][0]['geometry']['location']
                    st.session_state.lat = loc['lat']
                    st.session_state.lon = loc['lng']
                else:
                    st.sidebar.error(f"No results found for '{place_name}'.")
            else:
                st.sidebar.error("Failed to contact Google Geocoding API.")

    # Manual lat/lon entry
    lat = st.sidebar.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=float(st.session_state.lat),
        step=0.0001,
        format="%.4f",
        help="Enter latitude (-90 to 90)"
    )
    lon = st.sidebar.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=float(st.session_state.lon),
        step=0.0001,
        format="%.4f",
        help="Enter longitude (-180 to 180)"
    )
    st.session_state.lat = lat
    st.session_state.lon = lon

    # Show the selected location on a map with a marker using pydeck
    import pydeck as pdk
    st.write("### 🌍 Selected Location")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"lat": lat, "lon": lon}],
        get_position='[lon, lat]',
        get_fill_color='[200, 30, 0, 160]',
        get_radius=10000,
    )
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=3, pitch=0)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
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
