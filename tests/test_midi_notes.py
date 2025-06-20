import pytest

from midi_notes import *

bad_note: Note = Note(0, '', 0, 0)
class TestStrToNote:
    def test_str_to_note1(self):
        result = str_to_note('C')
        assert result.duration == NoteDuration.default
        assert result.name == 'C'
        assert result.octave == 4
        assert result.pitch == 48

    def test_str_to_note2(self):
        result = str_to_note('qEb5')
        assert result.duration == NoteDuration.quaver
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
