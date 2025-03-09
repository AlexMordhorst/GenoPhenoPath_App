# CLAUDE.md - GenoPhenoPath App Documentation

## Build/Run Commands
- Run app: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt`
- Create conda environment: `conda env create -f environment.yml`
- Activate conda env: `conda activate GenoPhenoPath`

## Code Style Guidelines
- **Formatting**: Follow PEP 8 for Python code
- **Imports**: Group in order: standard library, third-party, local imports
- **Variable naming**: Use snake_case for variables and functions
- **UI components**: Follow existing dark space theme
- **Type hints**: Add where possible for function parameters and returns
- **Error handling**: Use try/except blocks with specific exceptions
- **Documentation**: Add docstrings to functions using triple quotes
- **3D visualization**: Use plotly.graph_objects for interactive plots

## Architecture Notes
- `app.py`: Main Streamlit UI and user interaction logic
- `prototype.py`: Core knowledge graph generation logic
- Data files in `Data/` directory should follow tab-separated format