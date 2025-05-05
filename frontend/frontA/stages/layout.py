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
        initial_sidebar_state="collapsed",  # Ensure sidebar is hidden
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "GenoPhenoPath: 3D Knowledge Graph for Genome-Phenotype-Diagnostic Visualization"
        }
    )

def apply_custom_css():
    """
    Apply custom CSS styling to the application.
    
    This function adds dark space-themed styling to create a visually appealing interface
    with enhanced tab navigation, and makes the app fill the entire browser window.
    
    Used in:
    - frontend.frontB.app.main.run_app
    """
    # Add custom CSS for dark spacey theme
    st.markdown("""
    <style>
        /* MORE AGGRESSIVE FULLSCREEN APPROACH */
        /* Target ALL containers and elements to fill screen */
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }

        /* The root app container itself - absolutely no margins */
        .stApp {
            background: #000000;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        
        /* Target first child of stApp to remove top margins */
        .stApp > div {
            margin-top: -20px !important;
            padding-top: 0 !important;
        }
        
        /* Target streamlit app view container */
        [data-testid="stAppViewContainer"] {
            margin-top: -20px !important;
            padding-top: 0 !important;
        }
        
        /* Main content container - no padding */
        [data-testid="stAppViewBlockContainer"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100vw !important;
            max-width: 100vw !important;
            height: 100vh !important;
            max-height: 100vh !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: auto !important;
        }
        
        /* Target the actual content wrappers */
        .main, .main-content, section, 
        .block-container, [data-testid="stVerticalBlock"] {
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Ensure content doesn't have scrollbars unless needed */
        .main .block-container {
            padding: 0 !important;
        }
        
        /* Remove Streamlit branding and header completely */
        #MainMenu, header, footer, [data-testid="stToolbar"], div[data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
        }
        
        /* Hide ALL hidden overflow that might create borders */
        .withScreencast, .css-ffhzg2, 
        .css-1db87p3, .css-1vq4p4l {
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
            max-width: 100vw !important;
        }
        
        /* Hide scrollbar but allow scrolling */
        /* For Chrome, Safari and Opera */
        .main::-webkit-scrollbar {
            display: none;
        }
        /* For Firefox */
        .main {
            scrollbar-width: none;
        }
        /* For IE and Edge */
        .main {
            -ms-overflow-style: none;
        }
        
        /* Force any viewport units to be calculated correctly */
        .stApp [style*="vh"], .stApp [style*="vw"],
        .stApp [style*="height"], .stApp [style*="width"] {
            box-sizing: border-box !important;
        }
        
        /* Title styling - minimal margin */
        h1 {
            color: #8be9fd !important;
            font-family: 'Courier New', monospace !important;
            text-shadow: 0 0 10px rgba(139, 233, 253, 0.7);
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Make text and labels more visible on dark background */
        p, .stMarkdown, .css-10trblm, .css-1yeedl6 {
            color: #f8f8f2 !important;
        }
        
        /* Sidebar styling - hide completely, we're not using it */
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Hide the sidebar toggle completely */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Button styling */
        .stButton button {
            background-color: #483d8b !important;
            color: white !important;
            border: none !important;
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
        
        /* PLOTLY CHART FULLSCREEN BEHAVIOR */
        /* Make plotly background match app background */
        .js-plotly-plot, .plotly, .plot-container {
            background: #000000 !important;
        }
        
        /* Ensure each container holding charts has maximum height */
        [data-testid="element-container"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
            width: 100% !important;
        }
        
        /* Make Plotly charts take maximum available space */
        .plot-container, iframe {
            width: 100% !important;
            height: 85vh !important; /* Take most of the viewport height */
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        
        /* Tab styling - pulled up with more tabs */
        [data-testid="stTabs"] {
            background-color: transparent !important;
            border-radius: 5px !important;
            padding: 5px 5px 2px 5px !important;
            padding-top: 0 !important;
            margin-bottom: 0 !important;
            margin-top: -20px !important; /* Negative margin to pull up */
            width: 100% !important;
            border: none !important;
            position: relative !important;
            top: -20px !important; /* Additional positioning to pull up */
        }
        
        /* Active tab button styling */
        [data-testid="stTabs"] button[aria-selected="true"] {
            background-color: #483d8b !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 3px !important;
            box-shadow: 0 0 5px rgba(72, 61, 139, 0.5) !important;
        }
        
        /* Inactive tab button styling */
        [data-testid="stTabs"] button[aria-selected="false"] {
            color: #8be9fd !important;
            background-color: rgba(15, 20, 30, 0.8) !important;
            opacity: 0.8 !important;
            border: none !important;
            border-radius: 3px !important;
        }
        
        /* For disabled tab effect - this will apply to non-clickable tabs */
        [data-testid="stTabs"] button[aria-disabled="true"],
        [data-testid="stTabs"] button[disabled] {
            opacity: 0.5 !important;
            cursor: not-allowed !important;
            color: #6c757d !important;
        }
        
        /* Tab panel container - the content under each tab */
        [data-testid="stTabs"] [data-testid="stTabContent"] {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin-top: 0 !important;
            width: 100% !important;
        }
        
        /* Make dataframes go full width */
        [data-testid="stDataFrame"] {
            width: 100% !important;
        }
        
        /* Ensure all containers expand to full width */
        div.stTabs > div {
            width: 100% !important;
        }

        /* Fix iframe heights to match parent */
        iframe {
            display: block !important;
        }
        
        /* Force elements to take full width - using !important as Streamlit uses inline styles */
        div, section, main {
            max-width: 100% !important;
        }
        
        /* Fix any containing blocks that might limit width */
        .element-container, .stDataFrame > div,
        div[data-testid="stDecoration"] {
            max-width: 100% !important;
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add JavaScript to help resize the iframe and remove border effects
    st.markdown("""
    <script>
        // Function to resize all iframes to fit full window
        function resizeIFrames() {
            const iframes = document.querySelectorAll('iframe');
            const height = window.innerHeight;
            const width = window.innerWidth;
            
            iframes.forEach(iframe => {
                iframe.style.height = height + 'px';
                iframe.style.width = width + 'px';
                iframe.style.border = 'none';
                iframe.style.margin = '0';
                iframe.style.padding = '0';
            });
        }
        
        // Run on page load and window resize
        window.addEventListener('load', resizeIFrames);
        window.addEventListener('resize', resizeIFrames);
    </script>
    """, unsafe_allow_html=True)

def create_layout_containers():
    """
    Create the main layout containers for the application.
    
    Note: This function is kept for backward compatibility.
    The dropdown container is no longer used, as statistics are now in their own tab.
    
    Returns:
        Animation placeholder: Placeholder for loading animation
        
    Used in:
    - frontend.frontB.app.main.run_app (legacy)
    """
    # Create a placeholder for the DNA animation
    animation_placeholder = st.empty()
    
    return animation_placeholder