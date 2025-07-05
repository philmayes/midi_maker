from src import midi_notes as mn
from src.midi_notes import Duration as dur
from src import midi_chords as mc

class TestBarChord:
    def test_barchord1(self):
        """Plain key, duration and chord implied."""
        d, bc = mc.get_barchord('F#')
        assert d == dur.default
        assert bc.key == 'F#'
        assert bc.chord == 'maj'
        assert bc.chord in mc.chords

    def test_barchord2(self):
        """Duration, key and chord supplied."""
        d, bc = mc.get_barchord('eDm')
        assert d == dur.eighth
        assert bc.key == 'D'
        assert bc.chord == 'min'
        assert bc.chord in mc.chords

    def test_barchord3(self):
        """Compound durations added."""
        d, bc = mc.get_barchord('e+qDm')
        assert d == dur.eighth + dur.quarter
        assert bc.key == 'D'
        assert bc.chord == 'min'
        assert bc.chord in mc.chords

    def test_barchord4(self):
        """Compound durations subtracted."""
        d, bc = mc.get_barchord('h-eDm')
        assert d == dur.eighth + dur.quarter
        assert bc.key == 'D'
        assert bc.chord == 'min'
        assert bc.chord in mc.chords

    def test_barchord5(self):
        """Compound durations badly formatted."""
        d, bc = mc.get_barchord('h-e-Dm')
        assert d == 0

    def test_barchord6(self):
        """Compound durations with invalid letter z."""
        d, bc = mc.get_barchord('h-zDm')
        assert d == 0

    def test_barchord7(self):
        """Compound durations with leading sign."""
        d, bc = mc.get_barchord('-h-zDm')
        assert d == 0

    def test_barchord8(self):
        """Diminished."""
        d, bc = mc.get_barchord('eDdim')
        assert d == dur.eighth
        assert bc.key == 'D'
        assert bc.chord == 'dim'
        assert bc.chord in mc.chords

    def test_barchord9(self):
        """Diminished."""
        d, bc = mc.get_barchord('Asus4')
        assert d == dur.q
        assert bc.key == 'A'
        assert bc.chord == 'sus4'
        assert bc.chord in mc.chords
