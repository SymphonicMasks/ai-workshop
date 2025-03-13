import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DEFAULT_TEMP_MIDI_PATH = os.environ.get("DEFAULT_TEMP_MIDI_PATH", "test.mid")
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SCORES_DIR = DATA_DIR / "scores"
VISUALIZATIONS_DIR = DATA_DIR / "visuals"