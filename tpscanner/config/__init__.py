# __init__.py

import os

from .config import Config

# Load the configuration file
config = Config("tpscanner/config/config.ini")

# Ensure the output directory exists
os.makedirs(config.output_dir, exist_ok=True)
