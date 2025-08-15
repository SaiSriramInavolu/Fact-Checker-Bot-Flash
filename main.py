import subprocess
import sys
import logging
from src.database import init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_streamlit_app():
    """Runs the Streamlit application."""
    app_path = "src/ui/streamlit_app.py"
    logging.info(f"Starting Streamlit app from {app_path}...")
    
    init_db() 

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except FileNotFoundError:
        logging.error("Streamlit is not installed or not found in your PATH.")
        logging.error("Please ensure you have activated your virtual environment and installed Streamlit.")
    except Exception as e:
        logging.error(f"An error occurred while running Streamlit: {e}")

if __name__ == "__main__":
    run_streamlit_app()
