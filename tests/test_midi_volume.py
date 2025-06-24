import pytest

import midi_volume as mv

@pytest.fixture
def setup():
    mv.reset_volume()
    mv.ticks_per_rate = 1000   # instead of 960; makes assertions easier

def vlist(index: int, channel: int = 0) -> mv.VolChange:
    """A helper function to make the tests look cleaner."""
    return mv.voice_dict[channel][index]

def test_set_volume1(setup):
    """Test case 1. (See mv.set_volume() for the table of test cases.)"""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_volume(channel,    0,   100,     0,    0)
    assert vlist(-1).vol == 100
    mv.set_volume(channel,  500,    80,     0,    0)
    assert vlist(-1).vol == 80
    mv.set_volume(channel,  800,    60,     0,    0)
    assert vlist(-1).vol == 60

def test_set_volume2(setup):
    """Test case 2."""
    channel = 0
    tick = 0
    level = 0
    delta = 40
    rate = 0
    mv.set_volume(channel, tick, level, delta, rate)
    # Should not start with delta. default_volume + 40 = 140, clips to 127
    assert vlist(-1).vol == 127
    tick = 500
    delta = 20
    mv.set_volume(channel, tick, level, delta, rate)
    assert vlist(-1).vol == 127
    tick = 800
    delta = -10
    mv.set_volume(channel, tick, level, delta, rate)
    assert vlist(-1).vol == 117

def test_set_volume3(setup):
    """Test case 3."""
    channel = 0
    tick = 0
    level = 100
    delta = 0
    rate = 0
    mv.set_volume(channel, tick, level, delta, rate)
    assert vlist(-1).vol == level
    tick = 500
    delta = 20
    rate = 2
    mv.set_volume(channel, tick, 0, delta, rate)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == tick
    assert prev.vol == level
    assert prev.rate == 0
    assert last.tick == tick + (delta * mv.ticks_per_rate) // rate
    assert last.vol == level + delta
    assert last.rate == rate

def test_set_volume3neg(setup):
    """Test case 3 with negative delta."""
    channel = 0
    tick = 0
    level = 100
    delta = 0
    rate = 0
    mv.set_volume(channel, tick, level, delta, rate)
    assert vlist(-1).vol == level
    tick = 500
    delta = -20
    rate = 2
    mv.set_volume(channel, tick, 0, delta, rate)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == tick
    assert prev.vol == level
    assert prev.rate == 0
    assert last.tick == tick + (abs(delta) * mv.ticks_per_rate) // rate
    assert last.vol == level + delta
    assert last.rate == rate

def test_set_volume4(setup):
    """Test case 4."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_volume(channel,    0,   100,     0,    0)
    mv.set_volume(channel, 1000,    40,     0,   20)



    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == 1000
    assert prev.vol == 100
    assert prev.rate == 0
    assert last.tick == 4000
    assert last.vol == 40
    assert last.rate == 20

def test_set_volume4neg(setup):
    """Test case 4."""
    channel = 0
    tick = 0
    level1 = 100
    delta = 0
    rate = 0
    mv.set_volume(channel, tick, level1, delta, rate)
    assert vlist(-1).vol == level1
    tick = 500
    level2 = 40
    delta = 0
    rate = 2
    mv.set_volume(channel, tick, level2, delta, rate)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == tick
    assert prev.vol == level1
    assert prev.rate == 0
    assert last.tick == tick + (abs(level2 - level1) * mv.ticks_per_rate) // rate
    assert last.vol == level2
    assert last.rate == rate

def test_set_volume1_in_change(setup):
    """Test case 1 when change already in place."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_volume(channel,    0,   100,     0,    0)
    mv.set_volume(channel, 1000,    80,     0,    0)
    mv.set_volume(channel, 3000,     0,   -30,   10)
    mv.set_volume(channel, 4000,    90,     0,    0)
    last = vlist(-1)
    assert last.tick == 4000
    assert last.vol == 90
    assert last.rate == 0

def test_set_volume4_in_change(setup):
    """Test case 4 when change already in place."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_volume(channel,    0,   100,     0,    0)
    mv.set_volume(channel, 1000,    80,     0,    0)
    mv.set_volume(channel, 3000,     0,   -30,   10) # creates(6000,50,10)
    mv.set_volume(channel, 4000,    90,     0,   10)
    prev = vlist(-2)
    last = vlist(-1)
    assert prev.tick == 4000
    assert prev.vol == 80 # NOT 1/3 between 80 and 50
    assert prev.rate == 0
    assert last.tick == 5000
    assert last.vol == 90
    assert last.rate == 10

def test_get_volume1(setup):
    """Test case 4."""
    channel = 0
    #             channel, tick, level, delta, rate
    mv.set_volume(channel,    0,   100,     0,    0)
    mv.set_volume(channel, 1000,    80,     0,    0)
    mv.set_volume(channel, 3000,     0,   -30,   10)
    assert mv.get_volume(channel, 0) == 100
    assert mv.get_volume(channel, 999) == 100
    assert mv.get_volume(channel, 1000) == 80
    assert mv.get_volume(channel, 2999) == 80
    assert mv.get_volume(channel, 3000) == 80
    assert mv.get_volume(channel, 4000) == 70
    assert mv.get_volume(channel, 5000) == 60
    assert mv.get_volume(channel, 6000) == 50
    assert mv.get_volume(channel, 7000) == 50
