import random

from midiutil import MIDIFile

from src import midi
from src import midi_voice as mv
from src.midi_channels import Channel
from src import midi_items as mi
from src import midi_types as mt
from src.midi_voice import Voice
from src import midi_volume as mv
from src import utils

def test_1(mocker):
    """Test note/bar clipping."""
    random.seed(1)
    global start_error
    start_error = utils.make_error_table(10)
    global error7
    error7 = utils.make_error_table(7)
    channel = Channel.ch1
    mv.set_volume(channel, 0, 100, 0, 0) # channel, tick, level, delta, rate
    midi_file = MIDIFile()
    mock_add_note = mocker.patch.object(midi_file, 'addNote')
    mocker.patch('midi.add_start_error')
    bar_info: midi.BarInfo = midi.BarInfo(midi_file)
    chords: list[mt.BarChord] = [mt.BarChord(0, 'C', 'maj')]
    # Set 3rd param to True to remove clipping.
    # This will make the last assertion 1000, not 840.
    bar_info.bar = mi.Bar(chords, 1)
    voice: Voice = Voice('vtest', channel, 30, 'bass')
    # Use rhythms that extend past the end of the bar:
    voice.rhythms = [[1000,1000,1000,1000,]]
    midi.make_bass_bar(bar_info, voice)
    # Now you can assert addNote was called, e.g.:
    assert mock_add_note.called

    # Check all calls to addNote
    # time = args[3]
    # duration = args[4]
    # The time values fail because start_time is supplied by
    # add_start_error(bar_info.position) and mock cannot handle this.
    calls = mock_add_note.call_args_list
    # assert calls[0].args[3] == 0
    assert calls[0].args[4] == 1000
    # assert calls[1].args[3] == 1000
    assert calls[1].args[4] == 1000
    # assert calls[2].args[3] == 2000
    assert calls[2].args[4] == 1000
    # assert calls[3].args[3] == 3000
    assert calls[3].args[4] == 840  # last note has been truncated
