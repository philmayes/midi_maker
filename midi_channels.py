
from enum import IntEnum

class Channel(IntEnum):
    ch1 = 0
    ch2 = 1
    ch3 = 2
    ch4 = 3
    ch5 = 4
    ch6 = 5
    ch7 = 6
    ch8 = 7
    ch9 = 8
    ch10 = 10
    ch11 = 11
    ch12 = 12
    ch13 = 13
    ch14 = 14
    ch15 = 15
    percussion = 9
    # Above are real MIDI channels;
    # below are pseudo-channels used as percussion tracks.
    perc1 = 16
    perc2 = 17
    perc3 = 18
    perc4 = 19
    perc5 = 20
    perc6 = 21
    perc7 = 22
    perc8 = 23
    perc9 = 24
    perc10 = 25
    max_channels = 26   # Can be extended if more percussion tracks needed.
    none = 99

def is_midi(channel: Channel) -> bool:
    return channel < Channel.perc1

def is_perc(channel: Channel) -> bool:
    return channel >= Channel.perc1

def str_to_channel(name: str) -> Channel:
    """Returns the Channel described by the string."""
    for ch in Channel:
        if ch.name == name:
            return ch
    return Channel.none
