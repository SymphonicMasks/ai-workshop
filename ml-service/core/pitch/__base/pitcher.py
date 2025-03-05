from abc import ABC, abstractmethod

import pretty_midi


class BasePitcher(ABC):
    pitcher_name: str
    default_path: str

    @classmethod
    @abstractmethod
    def invoke(cls, audio_file_path: str) -> pretty_midi.PrettyMIDI:
        pass

    @classmethod
    def save_midi(cls, audio_file_path: str, output_path: str | None) -> str:
        if output_path is None:
            output_path = cls.default_path
        midi_data = cls.invoke(audio_file_path)
        midi_data.write(output_path)
        return output_path
