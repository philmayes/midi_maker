
from enum import IntEnum

class Channel(IntEnum):
    bass = 0
    rhythm = 1
    arpeggio = 2
    improv1 = 3
    improv2 = 4
    percussion = 9
    # Above are real MIDI channels;
    # below are pseudo-channels used as percussion tracks.
    perc0 = 16
    perc1 = 17
    perc2 = 18
    perc3 = 19
    perc4 = 20
    perc5 = 21
    perc6 = 22
    perc7 = 23
    perc8 = 24
    perc9 = 25
    max_channels = 26   # Can be extended if more percussion tracks needed.
    none = 99

def is_midi(channel: Channel) -> bool:
    return channel < Channel.perc0

def is_perc(channel: Channel) -> bool:
    return channel >= Channel.perc0

def str_to_channel(name: str) -> Channel:
    """Returns the Channel described by the string."""
    for ch in Channel:
        if ch.name == name:
            return ch
    return Channel.none
