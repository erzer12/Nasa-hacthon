def get_condition_label(variable, value):
    """
    Map a value for a variable to a human-friendly condition label.
    """
    if variable == 'Temperature':
        if value <= 0:
            return "Freezing"
        elif value <= 10:
            return "Cold"
        elif value <= 20:
            return "Mild"
        elif value <= 30:
            return "Warm"
        elif value <= 37:
            return "Hot"
        else:
            return "Very Hot"
    elif variable == 'Precipitation':
        if value < 1:
            return "Dry"
        elif value < 10:
            return "Light Rain"
        elif value < 30:
            return "Moderate"
        elif value < 60:
            return "Heavy"
        else:
            return "Stormy"
    elif variable == 'Sea Level':
        if value < 0.2:
            return "Normal"
        elif value < 0.5:
            return "Rising"
        elif value < 1.0:
            return "High Tide"
        else:
            return "Flood Risk"
    elif variable == 'Air Quality Index':
        if value <= 50:
            return "Good"
        elif value <= 100:
            return "Moderate"
        elif value <= 150:
            return "Poor"
        elif value <= 200:
            return "Very Poor"
        else:
            return "Hazardous"
    elif variable == 'Humidity':
        if value < 30:
            return "Dry"
        elif value < 50:
            return "Comfortable"
        elif value < 70:
            return "Humid"
        else:
            return "Very Humid"
    elif variable == 'Wind Speed':
        if value < 5:
            return "Calm"
        elif value < 15:
            return "Breezy"
        elif value < 30:
            return "Windy"
        elif value < 50:
            return "Very Windy"
        else:
            return "Storm-level"
    elif variable == 'CO2 Levels':
        if value < 400:
            return "Normal"
        elif value < 420:
            return "Elevated"
        elif value < 450:
            return "High"
        else:
            return "Very High"
    return "Unknown"
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from frontend import ui_helpers, visualizations
from data_engine.main import get_processed_data
from modeling.main import analyze_variable

st.set_page_config(
    page_title="Historical Risk Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Historical Risk Explorer")
st.markdown("""
### NASA Earth Observation Challenge
Explore historical environmental data and assess risk probabilities for various climate variables.
Select your location, date range, and variables to analyze patterns and potential risks.
""")

st.sidebar.title("Configuration")
st.sidebar.markdown("Adjust the parameters below to customize your analysis.")


location = ui_helpers.location_input()
selected_date = ui_helpers.date_input()
selected_variables = ui_helpers.variable_selector()

if not selected_variables:
    st.warning("Please select at least one environmental variable from the sidebar.")
    st.stop()

# Removed duplicate map preview

st.markdown("---")

if st.button("🚀 Analyze Variables", type="primary"):
    st.session_state.analysis_complete = True

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False


if st.session_state.analysis_complete:
    all_results = []
    summary_labels = []
    # Use session_state to cache per-variable data
    if 'weather_cache' not in st.session_state:
        st.session_state.weather_cache = {}
    weather_cache = st.session_state.weather_cache
    for variable in selected_variables:
        cache_key = f"{selected_date}_{location['lat']}_{location['lon']}_{variable}"
        if cache_key in weather_cache:
            historical_data, mean_val, label = weather_cache[cache_key]
        else:
            with st.spinner(f'Processing {variable} data...'):
                historical_data = get_processed_data(selected_date, variable, location)
            mean_val = historical_data['values']
            mean_val = sum(mean_val) / len(mean_val) if mean_val else 0
            label = get_condition_label(variable, mean_val)
            weather_cache[cache_key] = (historical_data, mean_val, label)
        summary_labels.append((variable, label))
        result_record = {
            'Variable': variable,
            'Location_Lat': location['lat'],
            'Location_Lon': location['lon'],
            'Analysis_Date': selected_date,
            'Condition': label,
            'Mean': mean_val,
            'Unit': historical_data['unit']
        }
        all_results.append(result_record)

    # Show selected variables in summary
    selected_vars_str = ', '.join(selected_variables)
    summary_sentence = "Likely " + ", ".join([f"{lbl.lower()} {var.lower()}" for var, lbl in summary_labels])
    st.markdown(f"### 📝 Personalized Weather Insight\n**Variables analyzed:** {selected_vars_str}.\n**{summary_sentence}.**")

    # Advanced Results toggleable
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False
    toggle_label = "Hide Advanced Results" if st.session_state.show_advanced else "Show Advanced Results"
    if st.button(toggle_label):
        st.session_state.show_advanced = not st.session_state.show_advanced

    if st.session_state.show_advanced:
        for idx, variable in enumerate(selected_variables):
            cache_key = f"{selected_date}_{location['lat']}_{location['lon']}_{variable}"
            historical_data, mean_val, label = weather_cache[cache_key]
            st.markdown(f"## 📊 {variable} (Advanced)")
            default_thresholds = {
                'Temperature': 25.0,
                'Precipitation': 60.0,
                'Wind Speed': 20.0,
                'Humidity': 70.0,
                'Air Quality Index': 100.0,
                'Sea Level': 0.5,
                'CO2 Levels': 415.0
            }
            threshold = ui_helpers.threshold_input(variable, default_thresholds.get(variable, 50.0))
            with st.spinner(f'Analyzing {variable}...'):
                analysis_result = analyze_variable(historical_data, threshold)
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Risk Metrics")
                st.metric("Exceedance Probability", f"{analysis_result['probability']}%")
                st.metric("Risk Index", f"{analysis_result['risk_index']:.3f}")
                st.metric("Mean Value", f"{analysis_result['mean']} {historical_data['unit']}")
                st.metric("Std Deviation", f"{analysis_result['std']} {historical_data['unit']}")
            with col2:
                st.subheader("Data Distribution")
                visualizations.plot_histogram(historical_data, threshold)
            st.subheader("Historical Trend")
            visualizations.plot_probability_trend(historical_data, threshold, analysis_result)
            st.markdown("---")
        # Export results
        st.markdown("## 💾 Export Results")
        st.markdown("Download the combined analysis results as a CSV file.")
        results_df = pd.DataFrame(all_results)
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"risk_analysis_{selected_date}.csv",
            mime="text/csv",
            type="primary"
        )
        st.success("✅ Analysis complete! You can now download the results.")
else:
    st.info("👆 Click the 'Analyze Variables' button above to start the analysis.")
