from abc import ABC
from typing import Optional

import pretty_midi
from basic_pitch.inference import predict

from config import DEFAULT_TEMP_MIDI_PATH
from core.pitch.__base.pitcher import BasePitcher


class BasicPitcher(ABC, BasePitcher):
    pitcher_name = 'basic_pitcher'
    default_path = DEFAULT_TEMP_MIDI_PATH

    @classmethod
    def invoke(cls, audio_file_path: str) -> pretty_midi.PrettyMIDI:
        model_output, midi_data, note_events = predict(audio_file_path,
                                                       onset_threshold=0.6,
                                                       minimum_frequency=130.813,
                                                       maximum_frequency=1278.75)
        return midi_data

    @classmethod
    def save_midi(cls, audio_file_path: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            output_path = cls.default_path
        midi_data = cls.invoke(audio_file_path)
        midi_data.write(output_path)
        return output_path
