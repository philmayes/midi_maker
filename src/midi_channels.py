
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
    none = 999

def is_midi(channel: Channel) -> bool:
    return channel != Channel.percussion

def is_perc(channel: Channel) -> bool:
    return channel == Channel.percussion

def str_to_channel(name: str) -> Channel:
    """Returns the Channel described by the string."""
    for ch in Channel:
        if ch.name == name:
            return ch
    return Channel.none
