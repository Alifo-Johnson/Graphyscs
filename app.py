import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import io # Required for the download button

# --- Configuration and Initialization ---

# Set the page title and description
st.set_page_config(page_title="Custom Data Graph Plotter", layout="wide")

# Image path check (using a simpler path for robustness, assuming assets folder exists)
try:
    st.image("assets/GraPhycs.png", width=1000)
except Exception:
    # Fallback in case image is missing
    st.image("GraPhycs.png", width=1000)

st.title("Graphycs 📊")
st.subheader("Physics Experiment Data Graph Plotter")
st.markdown("Enter your data, axis labels, and units using the **sidebar**.")

# Define common physics units for the dropdown
PHYSICS_UNITS = [
    "None",
    "Time (s)",
    "Length (m)",
    "Mass (kg)",
    "Force (N)",
    "Velocity (m/s)",
    "Acceleration (m/s²)",
    "Voltage (V)",
    "Current (A)",
    "Resistance (Ω)",
    "Energy (J)",
    "Power (W)"
]

# Initialize session state (no changes here)
if 'fig' not in st.session_state:
    st.session_state['fig'] = None
if 'x_values' not in st.session_state:
    st.session_state['x_values'] = []
if 'y_values' not in st.session_state:
    st.session_state['y_values'] = []
if 'plotted' not in st.session_state:
    st.session_state['plotted'] = False
if 'show_gradient' not in st.session_state:
    st.session_state['show_gradient'] = False # New state variable for gradient persistence

# --- Helper Function for Clearing Inputs ---
def clear_inputs():
    """Clears the plot state and resets gradient state."""
    st.session_state['fig'] = None
    st.session_state['x_values'] = []
    st.session_state['y_values'] = []
    st.session_state['plotted'] = False
    st.session_state['show_gradient'] = False # Reset gradient state
    st.toast("Plot state cleared!")

def set_gradient_state():
    """Sets the session state to show the gradient."""
    st.session_state['show_gradient'] = True

# --- Data Input in Sidebar (IMPROVED: Added custom label inputs) ---

with st.sidebar:
    st.header("Data Input & Customization")
    st.markdown("Enter comma-separated numbers.")
    
    # --- X-axis Customization ---
    st.subheader("X-Axis")
    x_label = st.text_input("X-axis Label (e.g., Time)", value="Time", key="x_label")
    x_unit = st.selectbox(
        "X-axis Unit",
        options=PHYSICS_UNITS,
        index=1,
        key="x_unit_select"
    )
    x_input = st.text_input(
        "Enter X values",
        value="1, 2, 3, 4, 5",
        key="x_input"
    )
    
    st.markdown("---")

    # --- Y-axis Customization ---
    st.subheader("Y-Axis")
    y_label = st.text_input("Y-axis Label (e.g., Position)", value="Position", key="y_label")
    y_unit = st.selectbox(
        "Y-axis Unit",
        options=PHYSICS_UNITS,
        index=2, # Default to Length (m)
        key="y_unit_select"
    )
    y_input = st.text_input(
        "Enter Y values",
        value="1, 4, 9, 16, 25",
        key="y_input"
    )

    st.markdown("---")
    # Added: Buttons side-by-side for primary action and reset
    col_p, col_c = st.columns(2)
    with col_p:
        # Note: We don't need to call a function on click for 'Plot Data' if we check its state below
        plot_button = st.button("Plot Data", type="primary")
    with col_c:
        st.button("Clear Plot/State", on_click=clear_inputs, type="secondary")

# --- Core Plotting Function (IMPROVED: Better unit handling and label use) ---

def plot_data(x_str, y_str, x_label, y_label, x_unit_label, y_unit_label, show_gradient=False):
    """Parses input, plots the data, and optionally adds the best-fit line/gradient."""
    
    # 1. Input Parsing and Validation
    try:
        x_values = [float(val.strip()) for val in x_str.split(',') if val.strip()]
        y_values = [float(val.strip()) for val in y_str.split(',') if val.strip()]

        if not (x_values and y_values):
            st.error("Please enter data for both the X and Y axes.")
            return None, [], []
        if len(x_values) != len(y_values):
            st.error("The number of X values must match the number of Y values.")
            return None, [], []
    except ValueError:
        st.error("Invalid input. Please ensure all values are numbers and separated by commas.")
        return None, [], []

    # 2. Plot Creation
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_values, y_values, marker='o', linestyle='', color='b', label='Data Points')

    # Construct axis labels
    x_axis_label_full = f"{x_label} ({x_unit_label.split(' ')[-1].replace('(','').replace(')','')})" if x_unit_label != "None" else x_label
    y_axis_label_full = f"{y_label} ({y_unit_label.split(' ')[-1].replace('(','').replace(')','')})" if y_unit_label != "None" else y_label

    ax.set_xlabel(x_axis_label_full)
    ax.set_ylabel(y_axis_label_full)
    ax.set_title(f"Plot of {y_label} vs {x_label}")
    ax.legend()
    ax.grid(True, linestyle='--')

    # 3. Gradient Calculation and Line
    if show_gradient:
        if len(x_values) < 2:
            st.error("Need at least two data points to calculate a meaningful linear gradient.")
        else:
            slope, intercept, r_value, p_value, std_err = linregress(x_values, y_values)
            gradient = slope
            
            # IMPROVED: Determine gradient unit label
            y_unit_simple = y_unit_label.split(' ')[-1].strip('()')
            x_unit_simple = x_unit_label.split(' ')[-1].strip('()')
            
            if y_unit_label == "None" and x_unit_label == "None":
                 grad_unit_display = ""
            elif y_unit_label == "None":
                 grad_unit_display = f"$\\frac{{1}}{{{x_unit_simple}}}$"
            elif x_unit_label == "None":
                 grad_unit_display = f"({y_unit_simple})"
            else:
                # Use LaTeX for fraction notation in the Streamlit output for better formatting
                grad_unit_display = f"$\\frac{{{y_unit_simple}}}{{{x_unit_simple}}}$"

            # Create the best-fit line
            x_fit = np.array(x_values)
            y_fit = intercept + slope * x_fit

            # Plot the best-fit line
            ax.plot(x_fit, y_fit, color='r', linestyle='--',
                    label=f'Best-Fit Line (m: {gradient:.4f})')
            ax.legend()
            
            # Display calculated gradient with units
            st.info(f"**Calculated Gradient (Slope of Best-Fit Line):** $m = {gradient:.4f}$ {grad_unit_display}")
            st.markdown(f"**Y-Intercept:** $c = {intercept:.4f}$")
            st.markdown(f"**R-Squared ($R^2$) Value:** ${r_value**2:.4f}$ (Measure of linearity)")

    return fig, x_values, y_values


# --- Main Logic Flow ---

# If the Plot button is clicked, or if the gradient state is true (to redraw the plot)
if plot_button or st.session_state['show_gradient']:
    # Only reset fig state if the plot button was explicitly pressed (to prevent endless loop on gradient click)
    if plot_button:
        st.session_state['fig'] = None
        st.session_state['show_gradient'] = False # Reset gradient state if new data is plotted

    # Generate the plot
    st.session_state['fig'], st.session_state['x_values'], st.session_state['y_values'] = plot_data(
        x_input, y_input, x_label, y_label, x_unit, y_unit, st.session_state['show_gradient']
    )
    st.session_state['plotted'] = st.session_state['fig'] is not None

# Display the plot
if st.session_state['fig']:
    st.pyplot(st.session_state['fig'])

    # --- Conditional Display of Buttons and Info ---
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # Button to calculate and show the gradient
        # Use on_click to immediately set the state and trigger a rerun
        st.button(
            "Calculate Gradient (Best-Fit)", 
            on_click=set_gradient_state, 
            help="Calculates and plots the linear best-fit line and its gradient."
        )

    with col2:
        # Button to download the plot as a PNG
        # Save the figure to a bytes buffer
        buf = io.BytesIO()
        st.session_state['fig'].savefig(buf, format="png", bbox_inches='tight') 
        buf.seek(0) # Reset buffer pointer

        st.download_button(
            label="Download Plot as PNG", 
            data=buf,
            file_name="custom_data_plot.png",
            mime="image/png",
            help="Downloads the current plot image as a high-quality PNG file."
        )

# Initial/Empty state message
elif not st.session_state['plotted']:
    st.info("Enter your data in the sidebar and click 'Plot Data' to begin. Use the axis label and unit dropdowns to customize your graph for professional presentation.")