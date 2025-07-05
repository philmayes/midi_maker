from src import midi_notes as mn
from src.midi_notes import Duration as dur
from src import midi_types as mt

bad_note: mt.Note = mt.Note(0, 0, '', 0, 0, 0)
class TestGetSubDuration:
    def test_get_neg_duration0(self):
        """Test empty duration."""
        result = mn.get_sub_duration('')
        assert result == 0

    def test_get_sub_duration1(self):
        """Test single duration."""
        result = mn.get_sub_duration('h')
        assert result == dur.half

    def test_get_sub_duration2(self):
        """Test correct subtraction."""
        result = mn.get_sub_duration('h-q')
        assert result == dur.q

    def test_get_sub_duration3(self):
        """Test dotted duration."""
        result = mn.get_sub_duration('q.')
        assert result == dur.quarter + dur.eighth

    def test_get_sub_duration4(self):
        """Test multiple subtractions."""
        result = mn.get_sub_duration('n-h-q')
        assert result == dur.quarter

    def test_get_sub_duration5(self):
        """Test invalid format (trailing sign)."""
        result = mn.get_sub_duration('q-h-')
        assert result < 0

class TestGetDuration:
    def test_get_duration0(self):
        result = mn.get_duration('')
        assert result == 0

    def test_get_duration1(self):
        result = mn.get_duration('C')
        assert result == 0

    def test_get_duration2(self):
        result = mn.get_duration('h')
        assert result == dur.half

    def test_get_duration3(self):
        result = mn.get_duration('q.')
        assert result == dur.quarter + dur.eighth

    def test_get_duration4(self):
        result = mn.get_duration('q+h')
        assert result == dur.quarter + dur.half

    def test_get_duration5(self):
        result = mn.get_duration('q.+h')
        assert result == dur.quarter\
                       + dur.eighth\
                       + dur.half

    def test_get_duration6(self):
        result = mn.get_duration('q+q')
        assert result == dur.half

    def test_get_duration7(self):
        result = mn.get_duration('quarter')
        assert result == dur.quarter

    def test_get_duration8(self):
        result = mn.get_duration('half.')
        assert result == dur.half +  dur.quarter

    def test_get_duration9(self):
        result = mn.get_duration('half.+quarter')
        assert result == dur.note

    def test_get_duration10(self):
        result = mn.get_duration('n-q')
        assert result == dur.half + dur.quarter

    def test_get_duration11(self):
        result = mn.get_duration('q+n-q')
        assert result == dur.note

    def test_get_duration12(self):
        result = mn.get_duration('q+n-')
        assert result == 0

    def test_get_duration13(self):
        result = mn.get_duration('half.-quarter')
        assert result == dur.half

class TestStrToDuration:
    def test_str_to_duration0(self):
        result = mn.str_to_duration('')
        assert result == 0

    def test_str_to_duration1(self):
        result = mn.str_to_duration('C')
        assert result == 0

    def test_str_to_duration2(self):
        result = mn.str_to_duration('h')
        assert result == dur.half

    def test_str_to_duration3(self):
        result = mn.str_to_duration('q.')
        assert result == dur.quarter + dur.eighth

    def test_str_to_duration4(self):
        result = mn.str_to_duration('q+h')
        assert result == dur.quarter + dur.half

    def test_str_to_duration5(self):
        result = mn.str_to_duration('q.+h')
        assert result == dur.quarter\
                       + dur.eighth\
                       + dur.half

    def test_str_to_duration6(self):
        result = mn.str_to_duration('h-q')
        assert result == dur.quarter

    def test_str_to_duration7(self):
        result = mn.str_to_duration('quarter')
        assert result == dur.quarter

    def test_str_to_duration8(self):
        result = mn.str_to_duration('half.')
        assert result == dur.half +  dur.quarter

    def test_str_to_duration9(self):
        result = mn.str_to_duration('half.+quarter')
        assert result == dur.note

    def test_str_to_duration10(self):
        result = mn.str_to_duration('n-q')
        assert result == dur.half + dur.quarter

    def test_str_to_duration11(self):
        result = mn.str_to_duration('q+n-q')
        assert result == dur.note

    def test_str_to_duration12(self):
        result = mn.str_to_duration('half.-quarter')
        assert result == dur.half

class TestStrToDurations:
    def test_str_to_durations0(self):
        """Test empty durations."""
        result = mn.str_to_durations('')
        assert result == []

    def test_str_to_durations1(self):
        result = mn.str_to_durations('q,e,e')
        assert result == [dur.q, dur.e, dur.e]

    def test_str_to_durations2(self):
        """Test arithmetic in durations."""
        result = mn.str_to_durations('h-q,q,q+q,q')
        assert result == [dur.q, dur.q, dur.h, dur.q]

    def test_str_to_durations3(self):
        """Test negative durations."""
        result = mn.str_to_durations('-q,q,-h+h,h')
        assert result == [-dur.q, dur.q, -dur.n, dur.h]

class TestStrToNote:
    def test_str_to_note1(self):
        result = mn.str_to_note('C')
        assert result.duration == dur.default
        assert result.name == 'C'
        assert result.octave == 0
        assert result.pitch == 0

    def test_str_to_note2(self):
        result = mn.str_to_note('eEb5')
        assert result.duration == dur.eighth
        assert result.name == 'Eb'
        assert result.octave == 5
        assert result.pitch == 63

    def test_str_to_note3(self):
        result = mn.str_to_note('m5X')
        assert result == bad_note

    def test_str_to_note4(self):
        result = mn.str_to_note('quarter')
        assert result == bad_note

    def test_str_to_note5(self):
        result = mn.str_to_note('h-qE')
        assert result.name == 'E'
        assert result.octave == 0
        assert result.pitch == 4

class TestStrToNotes:
    def test_str_to_notes1(self):
        tune: mt.Tune = mn.str_to_notes('nC5,h-qE,qA,C6')
        note: mt.Note = tune[0]
        assert note.duration == dur.note
        assert note.name == 'C'
        assert note.octave == 5
        assert note.pitch == 60
        note: mt.Note = tune[1]
        assert note.duration == dur.quarter
        assert note.name == 'E'
        assert note.octave == 5
        assert note.pitch == 64
        note: mt.Note = tune[2]
        assert note.duration == dur.quarter
        assert note.name == 'A'
        assert note.octave == 5
        assert note.pitch == 69
        note: mt.Note = tune[3]
        assert note.duration == dur.quarter
        assert note.name == 'C'
        assert note.octave == 6
        assert note.pitch == 72

    def test_str_to_notes2(self):
        """Test tune without duration or octave for first note."""
        tune: mt.Tune = mn.str_to_notes('C,h-qE,qA,C6')
        note: mt.Note = tune[0]
        assert note.duration == dur.quarter
        assert note.name == 'C'
        assert note.octave == 5
        assert note.pitch == 60
        note: mt.Note = tune[1]
        assert note.duration == dur.quarter
        assert note.name == 'E'
        assert note.octave == 5
        assert note.pitch == 64

    def test_str_to_notes3(self):
        """Test tune with duration in it."""
        tune: mt.Tune = mn.str_to_notes('nC5,h-q,qA,C6')
        note0: mt.Note = tune[0]
        assert note0.start == 0
        assert note0.duration == dur.note
        assert note0.name == 'C'
        assert note0.octave == 5
        assert note0.pitch == 60
        note1: mt.Note = tune[1]
        assert note1.start == dur.n + dur.q
        assert note1.duration == dur.quarter
        assert note1.name == 'A'
        assert note1.octave == 5
        assert note1.pitch == 69
        note2: mt.Note = tune[2]
        assert note2.start == dur.n + dur.h
        assert note2.duration == dur.quarter
        assert note2.name == 'C'
        assert note2.octave == 6
        assert note2.pitch == 72
