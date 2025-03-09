import os
from pathlib import Path
from typing import List, Union, Optional, Tuple

import pretty_midi

import music21.stream

from music21 import environment, stream, converter
from music21.note import Note


class SheetGenerator:
    def __init__(self, fractions: List[float], pause_fractions: List[float], default_path: Path):
        self.fractions = fractions
        self.pause_fractions = pause_fractions
        self.default_path = default_path
        self.env = environment.Environment

    def get_notes_from_midi(self, midi_data: pretty_midi.PrettyMIDI, tempo: float = None) -> Tuple[
        List[pretty_midi.Note], float]:
        notes = []
        try:
            if not tempo:
                tempo = midi_data.estimate_tempo()
        except ValueError:
            tempo = 0
            return notes, tempo

        beats_per_second = tempo / 60
        avg_note_time = 1 / beats_per_second

        for instrument in midi_data.instruments:
            for i, note in enumerate(instrument.notes):
                note_time = note.end - note.start
                notes.append(note)

                note_fraction = note_time / avg_note_time
                note_fraction = min(self.fractions, key=lambda x: abs(x - note_fraction))

        return notes, tempo

    def _preprocess_notes(self, notes: List[pretty_midi.Note], tempo: float,
                          time_signature: Tuple[int, int] = (4, 4), key: Tuple[str, str] = None) -> stream.Stream:

        m21_notes = []
        notes_in_one_sec = tempo / 60
        one_time = round(1 / notes_in_one_sec, 2)

        stream1 = stream.Stream()
        stream1.append(music21.meter.TimeSignature(f'{time_signature[0]}/{time_signature[1]}'))
        if key is not None:
            stream1.append(music21.key.Key(*key))

        for i, _note in enumerate(notes):
            options = self.fractions
            pause_options = self.pause_fractions

            if i == 0 and _note.start > pause_options[0] * one_time:
                rest = music21.note.Rest(quarterLength=pause_options[0])
                stream1.append(rest)

            name = _note.pitch
            rest = None
            if i + 1 < len(notes):
                next_note = notes[i + 1]

                if next_note.start < _note.end:
                    _note.end = next_note.start
                pause_fraction = (next_note.start - _note.end) / one_time
                if pause_fraction > 0.7:
                    rest_fraction = min(pause_options, key=lambda x: abs(x - pause_fraction))
                    rest = music21.note.Rest(quarterLength=rest_fraction)

            note_time = _note.end - _note.start
            note_fraction = note_time / one_time

            note_fraction = min(options, key=lambda x: abs(x - note_fraction))
            m21_note = Note(name, quarterLength=note_fraction)

            m21_notes.append(m21_note)
            stream1.append(m21_note)

            if rest is not None:
                stream1.append(rest)

        return stream1

    @staticmethod
    def read_xml(xml_path: Path) -> stream.Stream:
        xml_score = converter.parse(xml_path)
        xml_stream = stream.Stream(xml_score.parts[0].flatten().notesAndRests)

        return xml_stream

    def make_pdf(self, xml_path: Path, output_path: Path) -> Path:
        xml_score = converter.parse(xml_path)
        conv = converter.subConverters.ConverterLilypond()
        conv.write(xml_score, fmt='lilypond', fp=output_path, subformats=['pdf'])

        return output_path

    def invoke(self, midi_data: pretty_midi.PrettyMIDI, output_path: Optional[Union[Path, str]] = None,
                 time_signature: Tuple[int, int] = (4, 4), key: Tuple[str, str] = None, tempo: float = None) -> str:
        notes, tempo = self.get_notes_from_midi(midi_data, tempo)
        stream1 = self._preprocess_notes(notes, tempo, time_signature=time_signature, key=key)

        if output_path is None:
            output_path = self.default_path

        stream1.write('musicxml', fp=output_path)

        return str(output_path)