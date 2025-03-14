import copy
from pathlib import Path
from typing import List, Tuple, Optional, Any, Dict
from dataclasses import dataclass

import pretty_midi
from music21 import stream, chord, converter, key, meter, tie
from music21.note import Note
from music21 import environment
from config import XMLS_DIR


import platform
if platform.system() == 'Windows':
    lilypond_path = r"C:\Users\ITMO-Share\Downloads\lilypond-2.24.4\bin\lilypond.exe"
else:
    lilypond_path = '/usr/bin/lilypond'

environment.UserSettings()['lilypondPath'] = lilypond_path


class SubmissionProcessor:
    """
    This class is used to process the user's submission and create a visualization of the user's submission compared to
    the original music.
    """

    def __init__(self, original_stream: stream.Stream, user_notes: List[pretty_midi.Note], tempo: int, viz_path: str = None,
                 key: Optional[List[str]] = None, only_notes: bool = False,
                 note_fractions: Optional[List[float]] = None,
                 time_signature: Tuple[int, int] = (4, 4)):

        self.original_stream = original_stream
        self.user_notes = user_notes
        self.tempo = tempo
        self.viz_path = viz_path
        self.key = key
        self.only_notes = only_notes
        if note_fractions is None:
            note_fractions = [0.5, 1, 1.5, 2, 2.5, 4]
        self.note_fractions = note_fractions
        self.time_signature = time_signature

    def _create_skeleton(self) -> Tuple[List[str], List[float]]:
        """
        Create a skeleton of the original music.
        :return: Tuple of lists of original notes and their durations.
        """
        if self.key is not None:
            self.original_stream.keySignature = key.Key(self.key[0], self.key[1])
        if self.time_signature is not None:
            self.original_stream.insert(0, meter.TimeSignature(f"{self.time_signature[0]}/{self.time_signature[1]}"))
        stream_notes = self.original_stream.notes

        fractions = []
        original_notes = []
        for note in stream_notes:
            if note.isRest:
                continue
            if note.tie == tie.Tie("stop"):
                fractions[-1] += note.quarterLength
                continue
            original_notes.append(note.pitch.midi)
            fractions.append(note.quarterLength)

        return original_notes, fractions

    def make_viz(self, make_svg: bool = False) -> List[Dict[str, Any]]:
        """
        Create a visualization of the user's submission compared to the original music.
        The visualization is saved as a musicxml file.

        :param make_svg: Whether to create an svg file of the visualization.
        :return: A list of dictionaries containing the index of the note, the note name,
                 the duration of the note, and any errors.
        """
        original_notes, fractions = self._create_skeleton()
        stream_error = copy.deepcopy(self.original_stream)
        notes_in_one_sec = self.tempo / 60
        one_time = round(1 / notes_in_one_sec, 2)

        if not self.user_notes or not original_notes:
            return []

        results = []
        user_index, orig_index, stream_pointer = 0, 0, 0

        while user_index < len(self.user_notes) and orig_index < len(original_notes):
            user_note = self.user_notes[user_index]
            orig_note = original_notes[orig_index]

            user_pitch = user_note.pitch
            user_duration = user_note.end - user_note.start
            user_fraction = min(self.note_fractions, key=lambda x: abs(x - (user_duration / one_time)))

            # Skip very short notes
            if user_duration < 0.05:
                user_index += 1
                continue

            error = None

            if user_pitch == orig_note:
                # Check duration
                if user_fraction != fractions[orig_index]:
                    # error = "DURATION"
                    # stream_error.notes[stream_pointer].style.color = "yellow"
                    pass
                else:
                    stream_error.notes[stream_pointer].style.color = "green"

                results.append({"index": user_index, "note": user_pitch, "duration": user_fraction, "error": error})
                orig_index += 1
                stream_pointer += 1
            else:
                # Handle pitch mismatch
                error = "NOTE"
                wrong_note = Note(user_pitch, quarterLength=fractions[orig_index])
                wrong_note.style.color = "red"

                orig_note_obj = stream_error.notes[stream_pointer]
                orig_note_obj.style.color = "green"

                # Create a chord visualization
                chord_element = chord.Chord([orig_note_obj, wrong_note])
                stream_error.replace(orig_note_obj, chord_element)

                results.append({"index": user_index, "note": user_pitch, "duration": user_fraction, "error": error})
                orig_index += 1
                stream_pointer += 1

            user_index += 1

        # Mark unplayed notes
        for i in range(orig_index, len(original_notes)):
            stream_error.notes[stream_pointer].style.color = "red"
            stream_pointer += 1

        # Apply key signature if available
        if self.key is not None:
            stream_error.keySignature = key.Key(self.key[0], self.key[1])

        # Write the output file
        stream_error.write('musicxml', fp=self.viz_path)

        # Optionally create SVG
        if make_svg:
            svg = str(self.viz_path).replace(".xml", "")
            conv = converter.subConverters.ConverterLilypond()
            conv.write(stream_error, fmt='lilypond', fp=svg, subformats=['pdf'])
            print(f"SVG created at {svg}")

        return results

    def make_viz_new_algo(self, make_svg: bool = False) -> List[Dict[str, Any]]:
        """
        Create a visualization of the user's submission compared to the original music.
        The visualization is saved as a musicxml file.

        :param make_svg: Whether to create an svg file of the visualization.
        :return: A list of dictionaries containing the index of the note, the note name,
                 the duration of the note, and any errors.
        """

        original_notes, fractions = self._create_skeleton()
        stream_error = copy.deepcopy(self.original_stream)
        notes_in_one_sec = self.tempo / 60
        one_time = round(1 / notes_in_one_sec, 2)

        if not self.user_notes or not original_notes:
            return []

        results = []
        user_index, orig_index, stream_pointer = 0, 0, 0
        m, n = len(self.user_notes), len(original_notes)

        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if self.user_notes[i - 1].pitch == original_notes[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        i, j = m, n
        matched_notes = []
        linked_notes = []
        while i > 0 and j > 0:
            if self.user_notes[i - 1].pitch == original_notes[j - 1]:
                linked_notes.append((original_notes[j - 1], self.user_notes[i - 1], "correct"))
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                linked_notes.append((None, self.user_notes[i - 1].pitch, "wrong"))
                i -= 1
            else:
                linked_notes.append((original_notes[j - 1], None, "skipped"))
                j -= 1

        while i > 0:
            linked_notes.append((None, self.user_notes[i - 1].pitch, "wrong"))
            i -= 1
        while j > 0:
            linked_notes.append((original_notes[j - 1], None, "skipped"))
            j -= 1

        linked_notes.reverse()

        for i, res in enumerate(linked_notes):
            correct_note, user_note_obj, status = res
            original_duration = fractions[i] if correct_note is not None else None
            played_duration = (user_note_obj.end - user_note_obj.start) / one_time if user_note_obj else None
            tact_number = int(user_note_obj.start / one_time) if user_note_obj else None

            if status == "correct":
                stream_error.notes[stream_pointer].style.color = "green"
            elif status == "wrong":
                wrong_note = Note(user_note_obj, quarterLength=fractions[i])
                wrong_note.style.color = "red"

                orig_note_obj = stream_error.notes[stream_pointer]
                orig_note_obj.style.color = "green"

                # Create a chord visualization
                chord_element = chord.Chord([orig_note_obj, wrong_note])
                stream_error.replace(orig_note_obj, chord_element)
            else:
                stream_error.notes[stream_pointer].style.color = "red"

            if stream_error.notes[stream_pointer].tie == tie.Tie("start"):
                stream_pointer += 1
            stream_pointer += 1
            if stream_pointer >= len(stream_error.notes):
                break
        
        if played_duration and original_duration:
            if played_duration > original_duration * 1.2:
                status = "duration+"
            elif played_duration < original_duration * 0.8:
                status = "duration-"

        results.append({
            "original_note": pretty_midi.note_number_to_name(correct_note) if correct_note else None,
            "played_note": pretty_midi.note_number_to_name(user_note_obj.pitch) if user_note_obj else None,
            "status": status,
            "original_duration": str(original_duration) if original_duration else "None",
            "played_duration": str(played_duration) if played_duration else "None",
            "tact_number": tact_number,
            "start_time": round(user_note_obj.start, 3) if user_note_obj else None,
            "end_time": round(user_note_obj.end, 3) if user_note_obj else None
        })

        # Apply key signature if available
        if self.key is not None:
            stream_error.keySignature = key.Key(self.key[0], self.key[1])

        # Write the output file
        stream_error.write('musicxml', fp=self.viz_path)

        # Optionally create SVG
        if make_svg:
            svg = str(self.viz_path).replace(".xml", "")
            conv = converter.subConverters.ConverterLilypond()
            conv.write(stream_error, fmt='lilypond', fp=svg, subformats=['pdf'])
            print(f"SVG created at {svg}")
        print([(pretty_midi.note_number_to_name(t[0]), pretty_midi.note_number_to_name(t[1].pitch), t[-1]) for t in linked_notes])
        return results
