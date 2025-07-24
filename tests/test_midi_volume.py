import pytest

# from src import midi_volume as mv
from src import midi_timer as mtim

@pytest.fixture
def setup():
    mtim.ticks_per_rate = 1000   # instead of 960; makes assertions easier
    global mv
    mv = mtim.Timer('volume', 100)
    mv.reset_level()

def vlist(index: int, channel: int = 0) -> mtim.Change:
    """A helper function to make the tests look cleaner."""
    return mv.level_dict[channel][index]

def test_set_volume1(setup):
    """Test case 1. (See mv.set_level() for the table of test cases.)"""
    channel = 0
    #            channel, tick, level, delta, rate
    mv.set_level(channel,    0,   100,  None,    0)
    assert vlist(-1).level == 100
    mv.set_level(channel,  500,    80,  None,    0)
    assert vlist(-1).level == 80
    mv.set_level(channel,  800,    60,  None,    0)
    assert vlist(-1).level == 60

def test_set_volume2(setup):
    """Test case 2."""
    channel = 0
    tick = 0
    level = None
    delta = 40
    rate = 0
    mv.set_level(channel, tick, level, delta, rate)
    # Should not start with delta. default_volume + 40 = 140, clips to 127
    assert vlist(-1).level == 127
    tick = 500
    delta = 20
    mv.set_level(channel, tick, level, delta, rate)
    assert vlist(-1).level == 127
    tick = 800
    delta = -10
    mv.set_level(channel, tick, level, delta, rate)
    assert vlist(-1).level == 117

def test_set_volume3(setup):
    """Test case 3."""
    channel = 0
    tick = 0
    level = 100
    delta = None
    rate = 0
    mv.set_level(channel, tick, level, delta, rate)
    assert vlist(-1).level == level
    tick = 500
    level = 100
    delta = 20
    rate = 2
    mv.set_level(channel, tick, None, delta, rate)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == tick
    assert prev.level == level
    assert prev.rate == 0
    assert last.tick == tick + (delta * mtim.ticks_per_rate) // rate
    # assert last.level == level + delta
    assert last.rate == rate

def test_set_volume3neg(setup):
    """Test case 3 with negative delta."""
    channel = 0
    tick = 0
    level = 100
    delta = None
    rate = 0
    mv.set_level(channel, tick, level, delta, rate)
    assert vlist(-1).level == level
    tick = 500
    delta = -20
    rate = 2
    mv.set_level(channel, tick, None, delta, rate)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == tick
    assert prev.level == level
    assert prev.rate == 0
    assert last.tick == tick + (abs(delta) * mtim.ticks_per_rate) // rate
    assert last.level == level + delta
    assert last.rate == rate

def test_set_volume4(setup):
    """Test case 4."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_level(channel,    0,   100,  None,    0)
    mv.set_level(channel, 1000,    40,  None,   20)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == 1000
    assert prev.level == 100
    assert prev.rate == 0
    assert last.tick == 4000
    assert last.level == 40
    assert last.rate == 20

def test_set_volume4neg(setup):
    """Test case 4."""
    channel = 0
    tick = 0
    level1 = 100
    delta = None
    rate = 0
    mv.set_level(channel, tick, level1, delta, rate)
    assert vlist(-1).level == level1
    tick = 500
    level2 = 40
    delta = None
    rate = 2
    mv.set_level(channel, tick, level2, delta, rate)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == tick
    assert prev.level == level1
    assert prev.rate == 0
    assert last.tick == tick + (abs(level2 - level1) * mtim.ticks_per_rate) // rate
    assert last.level == level2
    assert last.rate == rate

def test_set_volume1_in_change(setup):
    """Test case 1 when change already in place."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_level(channel,    0,   100,  None,    0)
    mv.set_level(channel, 1000,    80,  None,    0)
    mv.set_level(channel, 3000,  None,   -30,   10)
    mv.set_level(channel, 4000,    90,  None,    0)
    last = vlist(-1)
    assert last.tick == 4000
    assert last.level == 90
    assert last.rate == 0

def test_set_volume4_in_change(setup):
    """Test case 4 when change already in place."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_level(channel,    0,   100,  None,    0)
    mv.set_level(channel, 1000,    80,  None,    0)
    mv.set_level(channel, 3000,  None,   -30,   10) # creates(6000,50,10)
    mv.set_level(channel, 4000,    90,  None,   10)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == 4000
    assert prev.level == 80 # NOT 1/3 between 80 and 50
    assert prev.rate == 0
    assert last.tick == 5000
    assert last.level == 90
    assert last.rate == 10

def test_get_volume1(setup):
    """Test case 4."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_level(channel,    0,   100,  None,    0)
    mv.set_level(channel, 1000,    80,  None,    0)
    mv.set_level(channel, 3000,  None,   -30,   10)
    assert mv.get_level(channel, 0) == 100
    assert mv.get_level(channel, 999) == 100
    assert mv.get_level(channel, 1000) == 80
    assert mv.get_level(channel, 2999) == 80
    assert mv.get_level(channel, 3000) == 80
    assert mv.get_level(channel, 4000) == 70
    assert mv.get_level(channel, 5000) == 60
    assert mv.get_level(channel, 6000) == 50
    assert mv.get_level(channel, 7000) == 50
