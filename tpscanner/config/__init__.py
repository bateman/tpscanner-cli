# __init__.py

import os

from .config import Config

config = Config("tpscanner/config/config.json")

os.makedirs(config.output_dir, exist_ok=True)
