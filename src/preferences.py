"""Supply default preferences."""

class Preferences:
    def __init__(self):
        self.improv_repeat = 0.3
        self.rhythm_repeat = 0.3
        self.rhythm_silence = 0.5
        self.default_volume = 100
        self.ticks_per_beat = 960   # aka PPQN, Pulses Per Quarter Note

prefs = Preferences()
