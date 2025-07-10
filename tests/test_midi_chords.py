from src import midi_notes as mn
from src.midi_notes import Duration as dur
from src import midi_chords as mc
from src import midi_types as mt

class TestGetChord:
    def test_get_chord1(self):
        """Plain key, duration and chord implied."""
        d, bc = mc.get_chord('F#')
        assert d == 0
        assert bc.key == 'F#'
        assert bc.chord == 'maj'
        assert bc.chord in mc.chords

    def test_get_chord2(self):
        """Duration, key and chord supplied."""
        d, bc = mc.get_chord('eDm')
        assert d == dur.eighth
        assert bc.key == 'D'
        assert bc.chord == 'min'
        assert bc.chord in mc.chords

    def test_get_chord3(self):
        """Compound durations added."""
        d, bc = mc.get_chord('e+qDm')
        assert d == dur.eighth + dur.quarter
        assert bc.key == 'D'
        assert bc.chord == 'min'
        assert bc.chord in mc.chords

    def test_get_chord4(self):
        """Compound durations subtracted."""
        d, bc = mc.get_chord('h-eDm')
        assert d == dur.eighth + dur.quarter
        assert bc.key == 'D'
        assert bc.chord == 'min'
        assert bc.chord in mc.chords

    def test_get_chord5(self):
        """Compound durations badly formatted."""
        d, bc = mc.get_chord('h-e-Dm')
        assert d < 0

    def test_get_chord6(self):
        """Compound durations with invalid letter z."""
        d, bc = mc.get_chord('h-zDm')
        assert d < 0

    def test_get_chord7(self):
        """Compound durations with leading sign."""
        d, bc = mc.get_chord('-h-zDm')
        assert d < 0

    def test_get_chord8(self):
        """Diminished."""
        d, bc = mc.get_chord('eDdim')
        assert d == dur.eighth
        assert bc.key == 'D'
        assert bc.chord == 'dim'
        assert bc.chord in mc.chords

    def test_get_chord9(self):
        """Diminished."""
        d, bc = mc.get_chord('Asus4')
        assert d == 0
        assert bc.key == 'A'
        assert bc.chord == 'sus4'
        assert bc.chord in mc.chords

class TestStrToNotes:
    def test_str_to_notes1(self):
        """Plain key, duration missing."""
        notes: mt.Notes = mc.str_to_notes('C', 222, 333, 5)
        assert len(notes) == 3
        #                        start  dur name int oct pitch
        assert notes[0] == mt.Note(222, 333, 'C',  0, 5, 60)
        assert notes[1] == mt.Note(222, 333, 'E',  4, 5, 64)
        assert notes[2] == mt.Note(222, 333, 'G',  7, 5, 67)

    def test_str_to_notes2(self):
        """Key extends into next octave, duration missing."""
        notes: mt.Notes = mc.str_to_notes('A', 222, 333, 5)
        assert len(notes) == 3
        #                        start  dur name int oct pitch
        assert notes[0] == mt.Note(222, 333, 'A',  9, 5, 69)
        assert notes[1] == mt.Note(222, 333, 'C#', 1, 6, 73)
        assert notes[2] == mt.Note(222, 333, 'E',  4, 6, 76)

    def test_str_to_notes3(self):
        """Key extends into next octave, duration supplied."""
        notes: mt.Notes = mc.str_to_notes('q+qA', 222, 333, 5)
        assert len(notes) == 3
        #                        start    dur name int oct pitch
        assert notes[0] == mt.Note(222, dur.h, 'A',  9, 5, 69)
        assert notes[1] == mt.Note(222, dur.h, 'C#', 1, 6, 73)
        assert notes[2] == mt.Note(222, dur.h, 'E',  4, 6, 76)
