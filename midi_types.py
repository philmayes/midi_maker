from collections import namedtuple
from typing import TypeAlias

BarChord = namedtuple('BarChord', 'start key chord')

class Note:
    def __init__(self, duration: int, name: str, interval: int, octave: int, pitch: int):
        self.duration = duration
        self.name = name
        self.interval = interval
        self.octave = octave
        self.pitch = pitch

    def __str__(self):
        return f'{self.duration:4} {self.name} {self.interval} {self.octave} {self.pitch}'

# Used in midi.py
Notes: TypeAlias = list[str]
Pitches: TypeAlias = list[int]
Rhythm: TypeAlias = list[int]
RhythmDict: TypeAlias = dict[str, Rhythm]
Rhythms: TypeAlias = list[Rhythm]

# Used in midi_parse.py
Verb: TypeAlias = str
Param: TypeAlias = list[str]
Params: TypeAlias = list[Param]
Command: TypeAlias = tuple[Verb, Params]
CommandDict: TypeAlias = dict[str, str]
Tune: TypeAlias = list[Note]
TuneDict: TypeAlias = dict[str, Tune]
Tunes: TypeAlias = list[Tune]

