# Historical Risk Explorer

A Streamlit-based tool developed for the NASA Earth Observation Challenge, enabling users to analyze historical environmental data and assess risk probabilities through interactive visualizations.

## Overview

Historical Risk Explorer is a modular application that allows users to:
- Select any geographic location and date for analysis
- Explore multiple environmental variables
- Visualize trends and distributions
- Calculate risk indices and exceedance probabilities
## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Nasa-hacthon.git
    cd Nasa-hacthon
    ```

2. **(Optional) Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```


3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure credentials:**
    
    Create a file at `.streamlit/secrets.toml` in the project root with the following structure:
    ```toml
    [meteomatics]
    username = "your_meteomatics_username"
    password = "your_meteomatics_password"
    ```
    This file is used by Streamlit to securely provide credentials to the app. Do **not** use a `.env` file.

## Directory Structure

```
src/
├── frontend/
│   ├── app.py              # Main Streamlit app entry point
│   ├── ui_helpers.py       # UI components and input widgets
│   └── visualizations.py   # Plotting and visualization utilities
├── data_engine/
│   └── main.py             # Mock data generation logic
└── modeling/
    └── main.py             # Statistical analysis and modeling
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Launching the App

Start the Streamlit application with:

```bash
streamlit run src/frontend/app.py
```

The app will be accessible at [http://localhost:8501](http://localhost:8501) in your browser.

## Supported Environmental Variables

- Temperature (°C)
- Precipitation (mm)
- Wind Speed (km/h)
- Humidity (%)
- Air Quality Index (AQI)
- Sea Level (m)
- CO₂ Levels (ppm)

## Data Source

Some data is mock-generated using NumPy for demonstration. For Meteomatics, you must provide credentials in `.streamlit/secrets.toml` as described above.

## Key Features

- **Flexible Location & Date Selection**
- **Multi-variable Environmental Analysis**
- **Interactive Charts & Maps**
- **Risk Probability Calculations**
- **CSV Export of Results**

---

*Developed for the NASA Earth Observation Challenge.*
