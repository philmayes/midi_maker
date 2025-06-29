"""This module manages volumes for voices.

For each channel, it assembles a list of VolChange items
from which the volume at any time can be calculated.
"""
from collections import namedtuple
import logging

import midi_notes
from preferences import prefs
import utils

# When the change rate is 1, the volume should change by 1 every:
ticks_per_rate = midi_notes.Duration.quarter

VolChange = namedtuple('VolChange', 'tick, vol, rate')

voice_dict: dict[int, list[VolChange]] = {}

def reset_volume() -> None:
    """Reset all volume info (helps with testing)."""
    voice_dict.clear()

def set_volume(channel: int,
               tick: int,
               level: int,
               delta: int,
               rate:int) -> None:
    """Adjust the volume of the channel in various ways.

    case  level  delta   rate  set level  set rate
      1     Y      -      -    to level      -
      2     -      Y      -    by delta      -
      3     -      Y      Y    old level     Y
      4     Y             Y    old level     Y
    There are only 4 cases because level or delta is a requirement
    and they may not coexist.
    """

    global voice_dict
    if channel not in voice_dict:
        voice_dict[channel] = []
    values: list[VolChange] = voice_dict[channel]

    assert level or delta
    assert not (level and delta)
    assert rate >= 0

    if not values and not level:
        logging.warning(f'First volume command should not not have a sign')

    # Remove any entries later than <tick> -- this handles the issue of a
    # volume change being requested while  a rate change is in progress.
    while values and values[-1].tick > tick:
        values.pop()

    old_vol = values[-1].vol if values else prefs.default_volume

    # First set the current volume
    if level and not rate:
        new_vol = level             # case 1
    elif delta and not rate:
        new_vol = old_vol + delta   # case 2
    else:
        new_vol = old_vol           # case 3 or4
    new_vol = utils.make_in_range(new_vol, 128, 'Volume channel1')
    values.append(VolChange(tick, new_vol, 0))

    # Then set up possible rate change
    if rate:                        # case 3 or 4
        if level:                   # case 4
            end_vol = level
        else:                       # case 3
            end_vol = new_vol + delta
        end_vol = utils.make_in_range(end_vol, 128, 'Volume channel2')
        change = abs(end_vol - new_vol)
        change *= ticks_per_rate
        change_time = change // rate
        # Add a second VolInfo describing when the new volume will be reached.
        values.append(VolChange(tick + change_time, end_vol, rate))

def get_volume(channel: int, tick: int) -> int:
    """Returns the volume for the channel at a specific time.

    In this example, ticks_per_rate is assumed to be 1000
    to make the table have simple numbers.
    index   tick   volume   rate
    +----- +------+--------+------+
    |  0   |    0 |    100 |    0 | created by level = 100  at t 0
    |  0   | 1000 |     80 |    0 | created by delta = -20  at t 1000
    |  0   | 3000 |     60 |    0 | created by delta = -20  at t 3000
    |  0   | 5000 |     40 |   10 | ...with rate = 10
    +----- +------+--------+------+

    Interim volumes are calculated thus:

    v1------`'-,                volume v1 at tick t1
    v-------|---`'-,            volume v  at tick t
            |   |   `'-,
    v2------|---|--------'-,    volume v2 at tick v2
            |   |          |
            t1  t          t2

        t - t1
    v = -------  x (v2 - v1) + v1
        t2 - t1
    """
    values: list[VolChange] = voice_dict[channel]
    if not values:
        logging.error(f'get_volume called when no volume set')
        return prefs.default_volume
    max_len = len(values)
    for n in range(max_len - 1, -1, -1):
        vc1 = values[n]
        if tick >= vc1.tick:
            if n < max_len - 1: # i.e. this is not the last entry
                vc2 = values[n + 1]
                if vc2.rate:
                    dv = vc2.vol - vc1.vol
                    dt = vc2.tick - vc1.tick
                    now = tick - vc1.tick
                    return now * dv // dt + vc1.vol
            return vc1.vol
    assert 0, f'Cannot find time {tick} in volume table'
    return prefs.default_volume
