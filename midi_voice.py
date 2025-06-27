import logging

from midi_channels import Channel
from midi_notes import NoteDuration as n
import midi_types as mt

default_rhythm: mt.Rhythm = [n.quarter, n.quarter, n.quarter, n.quarter,]

class Voice:
    styles = {
        'arpeggio': 60,
        'bass': 100,
        'improv': 120,
        'lead': 100,
        'perc': 100,
        'rhythm': 60,
    }

    def __init__(self,
                 name: str,
                 channel: Channel,
                 voice: int,
                 style: str,
                 min_pitch:int=0,
                 max_pitch:int=127,
                 rate: int=n.quarter
                 ) -> None:
        self.name = name
        self.channel = channel
        self.voice = voice
        self.style = style
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.rate = rate
        # The following 3 are used by improv to improve the melody lines.
        self.prev_pitch = -1    # pitch of the last note played
        self.prev_duration = 0  # duration of the last note played
        self.overlap = 0        # amount by which last note extends into next bar
        # Following is information for a channel (which includes percussion)
        # that can be adjusted dynamically.
        self.active = True
        self.rhythms: mt.Rhythms = [default_rhythm]
        self.rhythm_index = 0

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
        if self.rhythm_index >= len(self.rhythms):
            self.rhythm_index = 0
        rhythm = self.rhythms[self.rhythm_index]
        self.rhythm_index += 1
        return rhythm
