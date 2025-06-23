from midi_types import *
from midi_voice import Voice

class Item:
    """Abstract class constituent of a composition."""
    pass

class Bar(Item):
    """Bar description of a composition."""
    def __init__(self, chords: list[BarChord], repeat: int=1):
        self.chords: list[BarChord] = chords
        self.repeat = repeat
        self.clip = False

    def get_chord(self, at: int) -> str:
        for chord in reversed(self.chords):
            if at >= chord.start:
                return chord.key + chord.chord
        assert 0, 'chord lookup failed'
        return ''

    def get_tonic(self, at: int) -> str:
        for chord in reversed(self.chords):
            if at >= chord.start:
                return chord.key
        assert 0, 'tonic lookup failed'
        return ''

class Beat(Item):
    """Supply rhythm(s) for voice.
    This is the internal representation of a composition rhythm command.
    """
    def __init__(self, voice: Voice, rhythms: Rhythms):
        self.voice = voice
        self.rhythms = rhythms

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
    def __init__(self, voice: Voice, tunes: Tunes):
        self.voice = voice
        self.tunes = tunes

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
        self.time_sig_bottom = time_sig_bottom
        # self.ticks_per_beat = note // time_sig_bottom
        self.ticks_per_beat = 3840 // time_sig_bottom
        self.ticks_per_bar = self.ticks_per_beat * time_sig_top

class Volume(Item):
    """Adjust volume for voice(s)."""
    def __init__(self, delta: int, level: int, rate: int, voices: list[Voice]):
        self.delta = delta  # Amount by which to adjust volume
        self.level = level  # New setting for volume (takes precedence over delta)
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
