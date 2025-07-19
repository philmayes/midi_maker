"""This module manages dynamic values for voices.

For each channel, it assembles a list of Change items
from which the level at any time can be calculated.
"""
import logging

import midi_notes
import utils

# When the change rate is 1, the level should change by 1 every:
ticks_per_rate = midi_notes.Duration.quarter

class Change:
    def __init__(self, tick: int, vol: int, rate: int):
        self.tick = tick
        self.vol = vol
        self.rate = rate

class Timer:
    def __init__(self, name: str, default: int):
        self.name = name
        self.default = default
        self.level_dict: dict[int, list[Change]] = {}
        self.max_level = 128

    def reset_level(self) -> None:
        """Reset all level info (helps with testing)."""
        self.level_dict.clear()

    def set_level(self,
                  channel: int,
                  tick: int,
                  level: int | None,
                  delta: int | None,
                  rate:int) -> None:
        """Adjust the level of the channel in various ways.

        case  level  delta   rate  set level  set rate
        1     Y      -      -    to level      -
        2     -      Y      -    by delta      -
        3     -      Y      Y    old level     Y
        4     Y             Y    old level     Y
        There are only 4 cases because level or delta is a requirement
        and they may not coexist.
        """

        global level_dict
        if channel not in self.level_dict:
            self.level_dict[channel] = []
        values: list[Change] = self.level_dict[channel]

        assert level is not None or delta is not None, 'one of them must exist'
        assert level is None or delta is None, 'cannot supply level AND delta'
        assert rate >= 0,'negative level rate illegal'

        if not values and not level:
            logging.warning(f'First level command should not not have a sign')

        # Remove any entries later than <tick> -- this handles the issue of a
        # level change being requested while a rate change is in progress.
        while values and values[-1].tick > tick:
            values.pop()

        old_level: int = values[-1].vol if values else self.default

        # First set the current level
        new_level: int
        if level is not None and rate == 0:
            new_level = level               # case 1
        elif delta is not None and rate == 0:
            new_level = old_level + delta   # case 2
        else:
            new_level = old_level           # case 3 or4
        new_level = utils.make_in_range(new_level,
                                        self.max_level,
                                        f'{self.name} channel1')
        values.append(Change(tick, new_level, 0))

        # Then set up possible rate change
        if rate:                        # case 3 or 4
            if level is not None:       # case 4
                end_level = level
            elif delta is not None:     # case 3
                end_level = new_level + delta
            else:
                assert 0, 'oops'
            end_level = utils.make_in_range(end_level,
                                            self.max_level,
                                            f'{self.name} channel2')
            change = abs(end_level - new_level)
            change *= ticks_per_rate
            change_time = change // rate
            # Add a second Change describing when the new level will be reached.
            values.append(Change(tick + change_time, end_level, rate))

    def get_level(self, channel: int, tick: int) -> int:
        """Returns the level for the channel at a specific time.

        In this example, ticks_per_rate is assumed to be 1000
        to make the table have simple numbers.
        index   tick   level   rate
        +----- +------+--------+------+
        |  0   |    0 |    100 |    0 | created by level = 100  at t 0
        |  0   | 1000 |     80 |    0 | created by delta = -20  at t 1000
        |  0   | 3000 |     60 |    0 | created by delta = -20  at t 3000
        |  0   | 5000 |     40 |   10 | ...with rate = 10
        +----- +------+--------+------+

        Interim levels are calculated thus:

        L1------`'-,                level L1 at tick t1
        L-------|---`'-,            level L  at tick t
                |   |   `'-,
        L2------|---|--------'-,    level L2 at tick t2
                |   |          |
                t1  t          t2

            t - t1
        L = -------  x (L2 - L1) + L1
            t2 - t1
        """
        values: list[Change] = self.level_dict[channel]
        if not values:
            logging.error(f'get_level called when no level set')
            return self.default
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
        assert 0, f'Cannot find time {tick} in level table'
        return self.default

# Timer() instances. They are only constructed after prefs have been set up.
vol_pan = Timer
vol_timer: Timer
