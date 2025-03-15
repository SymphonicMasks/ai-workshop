from abc import ABC
from typing import Optional

import pretty_midi
from basic_pitch.inference import predict

from config import DEFAULT_TEMP_MIDI_PATH
from core.pitch.__base.pitcher import BasePitcher

from preprocessor_dynamicnr import PianoPreprocessor

class BasicPitcher(ABC, BasePitcher):
    pitcher_name = 'basic_pitcher'
    default_path = DEFAULT_TEMP_MIDI_PATH

    @classmethod
    def invoke(cls, audio_file_path: str) -> pretty_midi.PrettyMIDI:
        processor = PianoPreprocessor(audio_file_path)
        processed_audio, sr = processor.process_pipeline()
        processor.save_output("temp_processed.wav")
        model_output, midi_data, note_events = predict("temp_processed.wav",
                                                       onset_threshold=0.6,
                                                       minimum_frequency=16.35,
                                                       maximum_frequency=7902.13)
        return midi_data

    @classmethod
    def save_midi(cls, audio_file_path: str, output_path: Optional[str] = None) -> str:
        if output_path is None:
            output_path = cls.default_path
        midi_data = cls.invoke(audio_file_path)
        midi_data.write(output_path)
        return output_path
