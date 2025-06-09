import logging

from midi_channels import Channel

class Voice:
    def __init__(self, channel: Channel,
                 voice: int,
                 volume: int,
                 min_pitch:int=0,
                 max_pitch:int=127,
                 ) -> None:
        # if channel < Channel.perc0:
        #     self.channel = channel
        # else:
        #     self.channel = Channel.percussion
        self.channel = channel
        self.voice = voice
        self.volume = volume
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        # The following 3 are used by improv to improve the melody lines.
        self.prev_pitch = -1    # pitch of the last note played
        self.prev_duration = 0  # duration of the last note played
        self.overlap = 0        # amount by which last note extends into next bar

    def constrain_pitch(self, pitch: int) -> int:
        """Limit the pitch to that described in the voice."""
        if not 0 <= pitch <= 127:
            logging.warning(f'Pitch {pitch} is out of range')
        while pitch < self.min_pitch:
            pitch += 12
        while pitch > self.max_pitch:
            pitch -= 12
        return pitch
