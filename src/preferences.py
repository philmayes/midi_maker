"""Supply default preferences."""

class Preferences:
    """Default preferences."""
    def __init__(self):
        # Supply probabilities for random rhythm and improv.
        self.improv_repeat = 0.3
        self.rhythm_repeat = 0.3
        self.rhythm_rest = 0.5

        self.default_volume = 100

        # ticks_per_beat was removed because midi_notes sets up its values at
        # load time. Changing tpb in preferences is too late. It could be done
        # with some juggling, but it is an obscure setting, and it is easier
        # to just change the value directly in midi_notes.
        # self.ticks_per_beat = 960   # aka PPQN, Pulses Per Quarter Note

        # Parameters to fluidsynth.
        self.reverb_damp = 0.3      # [min=0.0, max=1.0, def=0.3]
        self.reverb_level = 0.7     # [min=0.0, max=1.0, def=0.7]
        self.reverb_roomsize = 0.5  # [min=0.0, max=1.0, def=0.5]
        self.reverb_width = 0.8     # [min=0.0, max=100.0, def=0.8]

        # Max values of error added to start time, duration and volume.
        # utils.add_error() uses these to generate a gaussian distribution.
        self.err_tim = 10
        self.err_dur = 10
        self.err_vol = 5

prefs = Preferences()
