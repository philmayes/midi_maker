from typing import TypeAlias

# Used in midi.py
Notes: TypeAlias = list[str]
Pitches: TypeAlias = list[int]
Rhythm: TypeAlias = list[int]
Rhythms: TypeAlias = dict[str, Rhythm]

# Used in midi_parse.py
Verb: TypeAlias = str
Param: TypeAlias = list[str]
Params: TypeAlias = list[Param]
Command: TypeAlias = tuple[Verb, Params]
