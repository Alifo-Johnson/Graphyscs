import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import io # Required for the download button

# --- Configuration and Initialization --- Version 1

# Set the page title and description
# st.image("Graphycs.png", width=200) # NOTE: Uncomment if you have this image file


st.set_page_config(page_title="Custom Data Graph Plotter", layout="wide")

st.image("assets/Graphycs.png", width=1000) # Ensure you have this image in the correct path or comment out

st.title("Graphycs 📊")
st.subheader("Physics Experiment Data Graph Plotter")
st.markdown("Enter your data for the X and Y axes using the **sidebar**.")

# Define common physics units for the dropdown
PHYSICS_UNITS = [
    "None (Dimensionless)",
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

# Initialize session state to store the plot figure and calculated values
if 'fig' not in st.session_state:
    st.session_state['fig'] = None
if 'x_values' not in st.session_state:
    st.session_state['x_values'] = []
if 'y_values' not in st.session_state:
    st.session_state['y_values'] = []
if 'plotted' not in st.session_state:
    st.session_state['plotted'] = False

# --- Helper Function for Clearing Inputs ---
def clear_inputs():
    """Clears the data input fields and the plot state."""
    # st.session_state['x_input'] = "" # Kept out to allow default values to remain or user preference
    # st.session_state['y_input'] = "" # Kept out to allow default values to remain or user preference
    st.session_state['fig'] = None
    st.session_state['x_values'] = []
    st.session_state['y_values'] = []
    st.session_state['plotted'] = False
    st.toast("Input fields cleared!")

# --- Data Input in Sidebar ---

with st.sidebar:
    st.header("Data Input")
    st.markdown("Enter comma-separated numbers.")
    
    # 1. X-axis Data Input
    x_input = st.text_input(
        "Enter X values",
        value="1, 2, 3, 4, 5",
        key="x_input"
    )
    
    # 2. X-axis Unit Dropdown (NEW)
    x_unit = st.selectbox(
        "X-axis Unit",
        options=PHYSICS_UNITS,
        index=1, # Default to Time (s)
        key="x_unit_select"
    )

    # 3. Y-axis Data Input
    y_input = st.text_input(
        "Enter Y values",
        value="1, 4, 9, 16, 25",
        key="y_input"
    )
    
    # 4. Y-axis Unit Dropdown (NEW)
    y_unit = st.selectbox(
        "Y-axis Unit",
        options=PHYSICS_UNITS,
        index=4, # Default to Force (N)
        key="y_unit_select"
    )


    # Added: Buttons side-by-side for primary action and reset
    col_p, col_c = st.columns(2)
    with col_p:
        plot_button = st.button("Plot Data", type="primary")
    with col_c:
        st.button("Clear Plot/State", on_click=clear_inputs, type="secondary") # Updated label


# --- Core Plotting Function (MODIFIED) ---

def plot_data(x_str, y_str, x_unit_label, y_unit_label, show_gradient=False):
    """Parses input, plots the data, and optionally adds the best-fit line/gradient."""
    try:
        # Convert the comma-separated strings to lists of numbers
        x_values = [float(val.strip()) for val in x_str.split(',') if val.strip()]
        y_values = [float(val.strip()) for val in y_str.split(',') if val.strip()]

        if not (x_values and y_values):
            st.error("Please enter data for both the X and Y axes.")
            return None, [], []

        # Ensure the lists have the same number of elements
        if len(x_values) != len(y_values):
            st.error("The number of X values must match the number of Y values.")
            return None, [], []

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the user-provided data
        ax.plot(x_values, y_values, marker='o', linestyle='', color='b', label='Data Points')

        # Add labels and a title to the plot (MODIFIED: Use selected units)
        ax.set_xlabel(f"X-axis ({x_unit_label})")
        ax.set_ylabel(f"Y-axis ({y_unit_label})")
        ax.set_title(f"{y_unit_label} vs {x_unit_label} Plot") # Updated title
        ax.legend()
        ax.grid(True, linestyle='--')

        gradient = None
        if show_gradient:
            # Added: Check for minimum data points required for linear regression
            if len(x_values) < 2:
                 st.error("Need at least two data points to calculate a meaningful linear gradient.")
            else:
                # Calculate linear regression (best-fit straight line)
                slope, intercept, r_value, p_value, std_err = linregress(x_values, y_values)
                gradient = slope

                # Create the best-fit line
                x_fit = np.array(x_values)
                y_fit = intercept + slope * x_fit

                # Determine gradient unit label
                # If X-unit is 'Time (s)' and Y-unit is 'Length (m)', gradient unit is 'Velocity (m/s)'
                # This is a simplification but informative.
                y_unit_str = y_unit_label.split(' ')[0]
                x_unit_str = x_unit_label.split(' ')[0]
                
                # Handling 'None (Dimensionless)'
                if 'None' in x_unit_str and 'None' in y_unit_str:
                     grad_unit = ""
                elif 'None' in x_unit_str:
                     grad_unit = f"({y_unit_label})"
                elif 'None' in y_unit_str:
                     grad_unit = f"(1/{x_unit_label})"
                else:
                    grad_unit = f"({y_unit_str}/{x_unit_str})"


                # Plot the best-fit line
                ax.plot(x_fit, y_fit, color='r', linestyle='--',
                                label=f'Best-Fit Line\n(Gradient: {gradient:.4f})')
                ax.legend()
                
                # Display calculated gradient with units
                st.info(f"**Calculated Gradient (Slope of Best-Fit Line):** $m = {gradient:.4f}$ {grad_unit}")


        return fig, x_values, y_values

    except ValueError:
        st.error("Invalid input. Please ensure all values are numbers and separated by commas.")
        return None, [], []


# --- Button Logic and Display ---

# Only execute the plotting logic if the 'Plot Data' button is clicked
if plot_button:
    # Always reset the plot state when the main 'Plot Data' button is pressed
    st.session_state['fig'] = None
    # Pass the selected units to the plot function (MODIFIED)
    st.session_state['fig'], st.session_state['x_values'], st.session_state['y_values'] = plot_data(
        x_input, y_input, x_unit, y_unit 
    )
    st.session_state['plotted'] = st.session_state['fig'] is not None
    # Re-display the plot immediately after pressing "Plot Data"
    if st.session_state['fig']:
        st.pyplot(st.session_state['fig'])

# Display the plot if it has been generated and the plot button wasn't just pressed (to avoid double plotting)
elif st.session_state['fig']:
    st.pyplot(st.session_state['fig'])

# --- Conditional Display of Buttons and Info ---

if st.session_state['fig']:
    
    # --- Buttons under the plotted graph ---
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # Button to calculate and show the gradient
        if st.button("Calculate Gradient (Best-Fit)", help="Calculates and plots the linear best-fit line and its gradient."):
            # Re-plot the data, this time requesting the gradient calculation (MODIFIED: Pass units again)
            st.session_state['fig'], _, _ = plot_data(x_input, y_input, x_unit, y_unit, show_gradient=True)
            # Re-display the plot with the line
            st.pyplot(st.session_state['fig']) 
            

    with col2:
        # Button to download the plot as a PNG
        if st.session_state['fig']:
            # Save the figure to a bytes buffer
            buf = io.BytesIO()
            # Save to PNG
            st.session_state['fig'].savefig(buf, format="png", bbox_inches='tight') 
            buf.seek(0) # Reset buffer pointer

            # Streamlit download button
            st.download_button(
                label="Download Plot as PNG", 
                data=buf,
                file_name="custom_data_plot.png",
                mime="image/png",
                help="Downloads the current plot image as a high-quality PNG file."
            )

elif st.session_state['plotted'] and not st.session_state['fig']:
    # This covers the case where the user entered bad data and an error was shown
    pass
elif not plot_button and not st.session_state['plotted']:
    st.info("Enter your data in the sidebar and click 'Plot Data' to begin. For gradient calculation, ensure your data is appropriate for linear regression (i.e., not a single point).")