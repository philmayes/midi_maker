from typing import TypeAlias

class Note:
    def __init__(self,
                 start: int,
                 duration: int,
                 name: str, interval: int,
                 octave: int,
                 pitch: int):
        self.start = start
        self.duration = duration
        self.name = name
        self.interval = interval
        self.octave = octave
        self.pitch = pitch

    def __str__(self):
        return f'{self.start:5} {self.duration:4} {self.name} {self.interval} {self.octave} {self.pitch}'

    def __eq__(self, other):
        return self.start == other.start and\
               self.duration == other.duration and\
               self.name == other.name and\
               self.interval == other.interval and\
               self.octave == other.octave and\
               self.pitch == other.pitch

class Rhythm:
    def __init__(self):
        self.durations: list[int] = []
        self.pitch: int = 4

# Used in midi.py
Notes: TypeAlias = list[str]
Pitches: TypeAlias = list[int]
RhythmDict: TypeAlias = dict[str, Rhythm]
Rhythms: TypeAlias = list[Rhythm]

# Used in midi_parse.py
Verb: TypeAlias = str
Param: TypeAlias = list[str]
Params: TypeAlias = list[Param]
Cmd: TypeAlias = tuple[Verb, Params]
CmdDict: TypeAlias = dict[str, str]
Tune: TypeAlias = list[Note]
TuneDict: TypeAlias = dict[str, Tune]
Tunes: TypeAlias = list[Tune]

