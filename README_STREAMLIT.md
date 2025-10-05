# Historical Risk Explorer

A multi-file Streamlit application for the NASA Earth Observation Challenge that analyzes historical environmental data and calculates risk probabilities.

## Project Structure

```
src/
├── frontend/
│   ├── app.py              # Main Streamlit application (orchestrator)
│   ├── ui_helpers.py       # User input widgets
│   └── visualizations.py   # Plotting functions
├── data_engine/
│   └── main.py            # Mock data generation
└── modeling/
    └── main.py            # Statistical analysis
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure credentials:
   
    Create a file at `.streamlit/secrets.toml` in the project root with the following structure:
    ```toml
    [meteomatics]
    username = "your_meteomatics_username"
    password = "your_meteomatics_password"
    ```
    This file is used by Streamlit to securely provide credentials to the app. Do **not** use a `.env` file.

## Running the Application

To run the Streamlit application:

```bash
streamlit run src/frontend/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Features

- **Location Selection**: Choose any location by latitude and longitude
- **Date Selection**: Select analysis date for historical data
- **Multi-Variable Analysis**: Analyze multiple environmental variables simultaneously
- **Interactive Visualizations**: View trends, distributions, and maps
- **Risk Calculation**: Calculate exceedance probability and risk indices
- **CSV Export**: Download combined analysis results

## Environmental Variables

The application supports analysis of the following variables:
- Temperature (°C)
- Precipitation (mm)
- Wind Speed (km/h)
- Humidity (%)
- Air Quality Index (AQI)
- Sea Level (m)
- CO2 Levels (ppm)

## Mock Data

The application uses mock data generated with NumPy for demonstration purposes. For Meteomatics, you must provide credentials in `.streamlit/secrets.toml` as described above.
