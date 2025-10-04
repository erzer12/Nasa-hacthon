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

    for variable in selected_variables:
        st.markdown(f"## 📊 {variable} Analysis")

        col1, col2 = st.columns([2, 1])

        with st.spinner(f'Processing {variable} data...'):
            historical_data = get_processed_data(selected_date, variable, location)

        with col1:
            st.subheader("Set Threshold")
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

        with col2:
            st.subheader("Risk Metrics")
            st.metric("Exceedance Probability", f"{analysis_result['probability']}%")
            st.metric("Risk Index", f"{analysis_result['risk_index']:.3f}")
            st.metric("Mean Value", f"{analysis_result['mean']} {historical_data['unit']}")
            st.metric("Std Deviation", f"{analysis_result['std']} {historical_data['unit']}")

        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            st.subheader("Historical Trend")
            visualizations.plot_probability_trend(historical_data, threshold, analysis_result)

        with viz_col2:
            st.subheader("Data Distribution")
            visualizations.plot_histogram(historical_data, threshold)

        result_record = {
            'Variable': variable,
            'Location_Lat': location['lat'],
            'Location_Lon': location['lon'],
            'Analysis_Date': selected_date,
            'Threshold': threshold,
            'Unit': historical_data['unit'],
            'Probability_%': analysis_result['probability'],
            'Risk_Index': analysis_result['risk_index'],
            'Mean': analysis_result['mean'],
            'Std_Dev': analysis_result['std'],
            'Min': analysis_result['min'],
            'Max': analysis_result['max']
        }
        all_results.append(result_record)

        st.markdown("---")

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
