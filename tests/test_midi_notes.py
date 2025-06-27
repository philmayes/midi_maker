import midi_notes as mn
import midi_types as mt

bad_note: mt.Note = mt.Note(0, '', 0, 0, 0)
class TestGetDuration:
    def test_get_duration0(self):
        result = mn.get_duration('')
        assert result == 0

    def test_get_duration1(self):
        result = mn.get_duration('C')
        assert result == 0

    def test_get_duration2(self):
        result = mn.get_duration('h')
        assert result == mn.NoteDuration.half

    def test_get_duration3(self):
        result = mn.get_duration('q.')
        assert result == mn.NoteDuration.quarter + mn.NoteDuration.eighth

    def test_get_duration4(self):
        result = mn.get_duration('q+h')
        assert result == mn.NoteDuration.quarter + mn.NoteDuration.half

    def test_get_duration5(self):
        result = mn.get_duration('q.+h')
        assert result == mn.NoteDuration.quarter\
                       + mn.NoteDuration.eighth\
                       + mn.NoteDuration.half

    def test_get_duration6(self):
        result = mn.get_duration('q+q')
        assert result == mn.NoteDuration.half

    def test_get_duration7(self):
        result = mn.get_duration('quarter')
        assert result == mn.NoteDuration.quarter

    def test_get_duration8(self):
        result = mn.get_duration('half.')
        assert result == mn.NoteDuration.half +  mn.NoteDuration.quarter

    def test_get_duration9(self):
        result = mn.get_duration('half.+quarter')
        assert result == mn.NoteDuration.note

    def test_get_duration10(self):
        result = mn.get_duration('n-q')
        assert result == mn.NoteDuration.half + mn.NoteDuration.quarter

    def test_get_duration11(self):
        result = mn.get_duration('q+n-q')
        assert result == mn.NoteDuration.note

    def test_get_duration12(self):
        result = mn.get_duration('half.-quarter')
        assert result == mn.NoteDuration.half

class TestStrToNote:
    def test_str_to_note1(self):
        result = mn.str_to_note('C')
        assert result.duration == mn.NoteDuration.default
        assert result.name == 'C'
        assert result.octave == 0
        assert result.pitch == 0

    def test_str_to_note2(self):
        result = mn.str_to_note('eEb5')
        assert result.duration == mn.NoteDuration.eighth
        assert result.name == 'Eb'
        assert result.octave == 5
        assert result.pitch == 63

    def test_str_to_note3(self):
        result = mn.str_to_note('m5X')
        assert result == bad_note

    def test_str_to_note4(self):
        result = mn.str_to_note('quarter')
        assert result == bad_note
