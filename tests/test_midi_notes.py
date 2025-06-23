from midi_notes import *

bad_note: Note = Note(0, '', 0, 0, 0)
class TestGetDuration:
    def test_get_duration0(self):
        result = get_duration('')
        assert result == NoteDuration.default

    def test_get_duration1(self):
        result = get_duration('C')
        assert result == NoteDuration.default

    def test_get_duration2(self):
        result = get_duration('h')
        assert result == NoteDuration.half

    def test_get_duration3(self):
        result = get_duration('c.')
        assert result == NoteDuration.quarter + NoteDuration.eighth

    def test_get_duration4(self):
        result = get_duration('c+m')
        assert result == NoteDuration.quarter + NoteDuration.half

    def test_get_duration5(self):
        result = get_duration('c.+m')
        assert result == NoteDuration.quarter\
                       + NoteDuration.eighth\
                       + NoteDuration.half

    def test_get_duration6(self):
        result = get_duration('c+c')
        assert result == NoteDuration.half

class TestStrToNote:
    def test_str_to_note1(self):
        result = str_to_note('C')
        assert result.duration == NoteDuration.default
        assert result.name == 'C'
        assert result.octave == 4
        assert result.pitch == 48

    def test_str_to_note2(self):
        result = str_to_note('qEb5')
        assert result.duration == NoteDuration.eighth
        assert result.name == 'Eb'
        assert result.octave == 5
        assert result.pitch == 63

    def test_str_to_note3(self):
        result = str_to_note('m5X')
        assert result == bad_note

    def test_str_to_note4(self):
        result = str_to_note('Cf#')
        assert result.duration == NoteDuration.default
        assert result.name == 'C'
        assert result.octave == 4
        assert result.pitch == 48
