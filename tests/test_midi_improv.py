from src import midi_chords as mc
from src import midi_items as mi
from src import midi_improv as mimp

class TestMakeBar:
    def test_make_bar1(self):
        """Plain key, duration and chord implied."""
        chord = mc.Chord(1000, 'C', 'maj', -1)
        bar = mi.Bar([chord])
        result = mimp.make_bar(bar)
        assert result.repeat == 1
