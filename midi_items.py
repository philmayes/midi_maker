from midi_types import *
from midi_voice import Voice

class Item:
    """Abstract class constituent of a composition."""
    pass

class Bar(Item):
    """Bar description of a composition."""
    def __init__(self, chord: str,
                 repeat: int=1,
                 ):
        self.chord = chord
        self.repeat = repeat
        self.clip = False

class Beat(Item):
    """Adjust rhythm for voice(s)."""
    def __init__(self, rhythm: str, voices: list[Voice]):
        self.rhythm = rhythm
        self.voices = voices

class Hear(Item):
    """Play (unmute) voice(s)."""
    def __init__(self, voices: list[Voice]):
        self.voices = voices

class Loop(Item):
    """Start a loop."""
    def __init__(self):
        pass

class LoopItem:
    """Item that is pushed onto the loop stack."""
    def __init__(self, item_no: int, count: int):
        self.item_no = item_no
        self.count = count

class Mute(Item):
    """Mute voice(s)."""
    def __init__(self, voices: list[Voice]):
        self.voices = voices

class Play(Item):
    """Play tune with voice."""
    def __init__(self, tune: Tune, voice: Voice):
        self.tune = tune
        self.voice = voice

class Repeat(Item):
    start = -1
    """Repeat a loop one or more times."""
    def __init__(self, repeat: int=2):
        # <repeat> is the number of times that control is returned to a Loop()
        # instance, so Repeat() or Repeat(2) means play the passage twice, and
        # we should only jump back once.
        assert repeat >= 2, 'Bad repeat count'
        self.repeat = repeat - 1

class Tempo(Item):
    """Change the tempo of a composition."""
    def __init__(self, tempo: int):
        self.tempo = tempo

class TimeSig(Item):
    """Change the time signature of a composition."""
    def __init__(self, time_sig_top: int, time_sig_bottom: int):
        self.time_sig_top = time_sig_top
        self.time_sig_bottom = time_sig_top
        # self.ticks_per_beat = semibreve // time_sig_bottom
        self.ticks_per_beat = 3840 // time_sig_bottom
        self.ticks_per_bar = self.ticks_per_beat * time_sig_top

class Volume(Item):
    """Adjust volume for voice(s)."""
    def __init__(self, delta: int, abs: int, rate: int, voices: list[Voice]):
        self.delta = delta  # Amount by which to adjust volume
        self.abs = abs      # New setting for volume (takes precedence over delta)
        self.rate = rate
        self.voices = voices

class Composition:
    """Collection of items that will generate a MIDI file."""
    def __init__(self) -> None:
        self.items: list[Item] = []

    def __iadd__(self, thing: Item | list[Item]):
        if isinstance(thing, Item):
            self.items.append(thing)
        else:
            self.items.extend(thing)
        return self
