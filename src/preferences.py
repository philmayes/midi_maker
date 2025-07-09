"""Supply default preferences."""

class Preferences:
    def __init__(self):
        self.improv_repeat = 0.3
        self.rhythm_repeat = 0.3
        self.rhythm_silence = 0.5
        self.default_volume = 100
        self.ticks_per_beat = 960   # aka PPQN, Pulses Per Quarter Note
        self.reverb_damp = 0.3      # [min=0.0, max=1.0, def=0.3]
        self.reverb_level = 0.7     # [min=0.0, max=1.0, def=0.7]
        self.reverb_roomsize = 0.5  # [min=0.0, max=1.0, def=0.5]
        self.reverb_width = 0.8     # [min=0.0, max=100.0, def=0.8]

prefs = Preferences()
