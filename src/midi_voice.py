"""Class that handles MIDI voices."""

import logging
from typing import TypeAlias

from midi_channels import Channel
from midi_notes import Duration as n
import midi_types as mt
import utils

# Default values follow. Not every style needs all of these values;
# they exist in the dictionaries for ease of coding and possible
# future use.
styles: dict[str, int] = {
    # This is used by midi_parse to validate the style name.
    'arpeggio': 1,
    'bass': 1,
    'improv': 1,
    'lead': 1,
    'perc': 1,
    'rhythm': 1,
}
rhythm: dict[str, mt.Rhythm] = {
    'arpeggio': [n.quarter, n.quarter, n.quarter, n.quarter,],
    'bass': [n.quarter, n.quarter, n.quarter, n.quarter,],
    'improv': [n.quarter, n.quarter, n.quarter, n.quarter,],
    'lead': [n.quarter, n.quarter, n.quarter, n.quarter,],
    'perc': [n.quarter, n.quarter, n.quarter, n.quarter,],
    'rhythm': [n.quarter, n.quarter, n.quarter, n.quarter,],
}
volume: dict[str, int] = {
    'arpeggio': 60,
    'bass': 100,
    'improv': 120,
    'lead': 100,
    'perc': 100,
    'rhythm': 60,
}
octave: dict[str, int] = {
    'arpeggio': 4,
    'bass': 3,
    'improv': 4,
    'lead': 4,
    'perc': 4,
    'rhythm': 4,
}
rate: dict[str, int] = {
    'arpeggio': n.quarter,
    'bass': n.quarter,
    'improv': n.quarter,
    'lead': n.quarter,
    'perc': n.quarter,
    'rhythm': n.quarter,
}

class Voice:
    """Represents a MIDI channel or percussion track."""

    def __init__(self,
                 name: str,
                 track: int,
                 channel: Channel,
                 voice: int,
                 style: str,
                 min_pitch: int=0,
                 max_pitch: int=127,
                 ):
        self.name = name
        self.track = track
        self.channel = channel
        self.voice = voice
        self.style = style
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        # The following 3 are used by improv to improve the melody lines.
        self.prev_pitch = -1    # pitch of the last note played
        self.prev_duration = 0  # duration of the last note played
        self.overlap = 0        # amount by which last note extends into next bar
        # Following is information for a channel (which includes percussion)
        # that can be adjusted dynamically.
        self.active = True
        self.rhythms: mt.Rhythms = [rhythm[style]]
        self.rhythm_index = 0
        self.pan = 64
        # staccato and overhang can be:
        # * an integer that clips a note to that duration
        # * a float that changes the duration by that factor
        # * None
        self.staccato: int | float | None = None
        self.overhang: int | float | None = None
        self.clip = True    # Clip overhang to the end of the bar
        self.octave: int = octave[style]
        self.rate: int = rate[style]
        self.vibrato: int = 0
        self.reverb: int = 0
        self.chorus: int = 0

    def add_note(self,
                 midi_file,
                 pitch,
                 position,
                 play_time,
                 volume) -> None:
        midi_file.addNote(self.track,
                          self.channel,
                          pitch,
                          utils.add_error(position, 10),
                          play_time,
                          volume)


    def adjust_duration(self, duration: int) -> int:
        """Adjust the duration of a note by the effects command."""
        if self.staccato:
            if isinstance(self.staccato, int):
                # A staccato integer clips the note to that value.
                return min(duration, self.staccato)
            else:
                # A staccato float is always < 1.0 and reduces
                # the duration by that factor.
                return int(duration * self.staccato)
        elif self.overhang:
            if isinstance(self.overhang, int):
                # An overhang integer adds that value to the note.
                return duration + self.overhang
            else:
                # An overhang float is always > 1.0 and increases
                # the duration by that factor.
                return int(duration * self.overhang)
        return duration

    def constrain_pitch(self, pitch: int) -> int:
        """Limit the pitch to that described in the voice."""
        if not 0 <= pitch <= 127:
            logging.warning(f'Pitch {pitch} is out of range')
        while pitch < self.min_pitch:
            pitch += 12
        while pitch > self.max_pitch:
            pitch -= 12
        return pitch

    def get_rhythm(self) -> mt.Rhythm:
        """Get the next rhythm in turn, wrapping around."""
        if self.rhythm_index >= len(self.rhythms):
            self.rhythm_index = 0
        rhythm = self.rhythms[self.rhythm_index]
        self.rhythm_index += 1
        return rhythm

Voices: TypeAlias = list[Voice]
