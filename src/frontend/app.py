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
    # Removed unsupported variables: Sea Level, Air Quality Index, CO2 Levels
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
    return "Unknown"
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

from . import ui_helpers, visualizations
import asyncio
from data_engine.main import get_processed_data_async, get_multiple_variables
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
    # Fetch all variables asynchronously
    async def fetch_all():
        return await get_multiple_variables(selected_date, selected_variables, location)

    with st.spinner('Processing all selected variables...'):
        results = asyncio.run(fetch_all())

    for idx, variable in enumerate(selected_variables):
        historical_data = results[idx]
        values = historical_data['values']
        # Filter out None values for mean calculation
        valid_vals = [v for v in values if v is not None]
        mean_val = sum(valid_vals) / len(valid_vals) if valid_vals else 0
        label = get_condition_label(variable, mean_val)
        cache_key = f"{selected_date}_{location['lat']}_{location['lon']}_{variable}"
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


    # Show selected variables in summary, with icons and color for eye-catching effect
    ICONS = {
        'Temperature': '🌡️',
        'Precipitation': '🌧️',
        'Wind Speed': '💨',
        'Humidity': '💧',
    }
    selected_vars_str = ', '.join([f"{ICONS.get(var, '')} {var}" for var in selected_variables])

    # Build a natural language summary
    friendly_phrases = []
    for var, lbl in summary_labels:
        if var == 'Temperature' and lbl in ['Very Hot', 'Hot']:
            friendly_phrases.append('it will feel <span style="color:#e25822;font-weight:bold">very hot</span>')
        elif var == 'Temperature' and lbl in ['Freezing', 'Cold']:
            friendly_phrases.append('it will feel <span style="color:#1e90ff;font-weight:bold">cold</span>')
        elif var == 'Precipitation' and lbl in ['Stormy', 'Heavy']:
            friendly_phrases.append('expect <span style="color:#0077b6;font-weight:bold">heavy rain</span>')
        elif var == 'Precipitation' and lbl == 'Dry':
            friendly_phrases.append('it will be <span style="color:#f4a261;font-weight:bold">dry</span>')
        elif var == 'Wind Speed' and lbl in ['Very Windy', 'Storm-level']:
            friendly_phrases.append('it will be <span style="color:#b5179e;font-weight:bold">very windy</span>')
        elif var == 'Humidity' and lbl == 'Very Humid':
            friendly_phrases.append('the air will feel <span style="color:#43aa8b;font-weight:bold">very humid</span>')
        else:
            friendly_phrases.append(f"{lbl.lower()} {var.lower()}")

    summary_sentence = " and ".join(friendly_phrases)
    st.markdown(f"""
        <div style="background:#23272f;border:1.5px solid #343942;padding:1.2em 1em 1em 1em;border-radius:1em;margin-bottom:1em;box-shadow:0 2px 8px 0 rgba(0,0,0,0.18);">
            <span style="font-size:1.3em;font-weight:bold;color:#f8fafc;">📝 Personalized Weather Insight</span><br>
            <span style="font-size:1.1em;color:#f8fafc;">{summary_sentence.capitalize()}.</span><br>
            <span style="font-size:1em;color:#b0b8c1;">Variables analyzed: {selected_vars_str}</span>
        </div>
    """, unsafe_allow_html=True)

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
