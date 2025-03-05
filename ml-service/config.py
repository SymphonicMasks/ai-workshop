import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_TEMP_MIDI_PATH = os.environ.get("DEFAULT_TEMP_MIDI_PATH", "test.mid")
