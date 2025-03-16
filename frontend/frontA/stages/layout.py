"""
Streamlit layout configuration for the GenoPhenoPath application.

This module handles the basic UI layout configuration including page settings,
CSS styling, and layout containers.

Functions in this module are used in:
- frontend.frontB.app.main: For initializing the application layout
"""

import streamlit as st

def configure_page_settings():
    """
    Configure the Streamlit page settings.
    
    This function sets up the page title, icon, layout, and sidebar state.
    
    Used in:
    - frontend.frontB.app.main.run_app
    """
    # Set page config to make the app wider with dark mode
    st.set_page_config(
        page_title="GenoPhenoPath 3D Knowledge Graph",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="collapsed"  # Hide sidebar by default
    )

def apply_custom_css():
    """
    Apply custom CSS styling to the application.
    
    This function adds dark space-themed styling to create a visually appealing interface.
    
    Used in:
    - frontend.frontB.app.main.run_app
    """
    # Add custom CSS for dark spacey theme
    st.markdown("""
    <style>
        /* Pure black background */
        .stApp {
            background: #000000;
        }
        
        /* Hide and remove the top header bar completely */
        header {
            display: none !important;
        }
        
        /* Target the main elements that create margins/padding */
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            margin-top: -39px !important;  /* 30% more negative margin to further reduce space */
        }
        
        /* Remove extra padding from the root container */
        .css-k1vhr4, .css-18e3th9, .css-1d391kg, 
        [data-testid="stVerticalBlock"] {
            padding-top: 0 !important;
            margin-top: -20px !important;  /* 30% more negative margin */
        }
        
        /* Target the top toolbar area */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Title styling */
        h1 {
            color: #8be9fd !important;
            font-family: 'Courier New', monospace !important;
            text-shadow: 0 0 10px rgba(139, 233, 253, 0.7);
        }
        
        /* Make text and labels more visible on dark background */
        p, .stMarkdown, .css-10trblm, .css-1yeedl6 {
            color: #f8f8f2 !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid rgba(139, 233, 253, 0.2);
        }
        
        /* Make sidebar headers stand out */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: #8be9fd !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Style sidebar checkboxes */
        [data-testid="stSidebar"] [data-testid="stCheckbox"] {
            margin-bottom: 0.5rem !important;
        }
        
        /* Style sidebar sliders */
        [data-testid="stSidebar"] [data-testid="stSlider"] {
            margin-bottom: 1.2rem !important;
        }
        
        /* Improve spacing between sections */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            margin-bottom: 0.5rem !important;
        }
        
        /* Hide the sidebar toggle completely */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Position our custom dropdown bar at the very top */
        div[data-testid="stExpander"] {
            position: fixed !important;
            top: 0px !important;
            left: 10% !important;
            right: 0 !important;
            z-index: 9999 !important;
            width: 80% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Style the dropdown header itself */
        .streamlit-expanderHeader {
            background-color: rgba(30, 41, 59, 0.8) !important;
            border: none !important;
            border-radius: 0 !important; /* Remove border radius for a menu bar look */
            color: #8be9fd !important;
            font-weight: 500 !important;
            margin: 0 !important;
            width: 100% !important;
            padding: 5px 10px !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        /* Style the dropdown content */
        .streamlit-expanderContent {
            background-color: rgba(15, 20, 30, 0.8) !important;
            border-radius: 0 0 4px 4px !important;
            border: none !important;
            padding: 10px !important;
            margin: 0 !important;
            width: 100% !important;
            box-shadow: none !important;
        }
        
        /* Remove additional outlines and borders that might appear */
        .streamlit-expanderHeader:focus, .streamlit-expanderHeader:hover,
        .streamlit-expanderContent:focus, .streamlit-expanderContent:hover {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Style the expander arrow */
        .streamlit-expanderHeader svg {
            color: #8be9fd !important;
            fill: #8be9fd !important;
        }
        
        /* Remove the white outline around the icon */
        .st-emotion-cache-1w5q6cr, .css-1w5q6cr {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Remove padding from the main content to eliminate space at the top */
        .main .block-container {
            padding-top: 0px !important;
            margin-top: -52px !important;  /* 30% more negative margin (from -40px to -52px) */
        }
        
        /* Button styling */
        .stButton button {
            background-color: #483d8b !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #272733 !important;
            color: #8be9fd !important;
            border-radius: 4px !important;
        }
        
        /* Slider styling */
        .stSlider div[data-baseweb="slider"] div {
            background-color: #483d8b !important;
        }
        
        /* Make metric labels more visible */
        [data-testid="stMetricLabel"] {
            color: #f8f8f2 !important;
        }
        
        /* Make metric values more visible and colorful */
        [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: bold !important;
        }
        
        /* Colorize different metric types */
        /* First row - node counts */
        [data-testid="column"]:nth-child(1) [data-testid="stMetricValue"] {
            color: #8be9fd !important; /* Blue for genes */
        }
        [data-testid="column"]:nth-child(2) [data-testid="stMetricValue"] {
            color: #ffb86c !important; /* Orange for phenotypes */
        }
        [data-testid="column"]:nth-child(3) [data-testid="stMetricValue"] {
            color: #ff79c6 !important; /* Magenta for diagnostics */
        }
        
        /* Info box styling */
        .stAlert {
            background-color: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(139, 233, 253, 0.2) !important;
        }
        
        /* Make plotly background match app background */
        .js-plotly-plot, .plotly, .plot-container {
            background: #000000 !important;
        }
        
        /* Additional styling for plotly chart spacing */
        [data-testid="element-container"] {
            margin-top: -50px !important;
            padding-top: 0 !important;
        }
        iframe {
            margin-top: -30px !important;
        }
    </style>
    """, unsafe_allow_html=True)

def create_layout_containers():
    """
    Create the main layout containers for the application.
    
    This function creates containers for the:
    - Stats dropdown
    - Animation placeholder
    
    Returns:
        Tuple of containers:
        - dropdown_container: Container for statistics dropdown
        - animation_placeholder: Placeholder for loading animation
        
    Used in:
    - frontend.frontB.app.main.run_app
    """
    # Create a container for the dropdown
    dropdown_container = st.container()
    
    # Create a placeholder for the DNA animation
    animation_placeholder = st.empty()
    
    return dropdown_container, animation_placeholder