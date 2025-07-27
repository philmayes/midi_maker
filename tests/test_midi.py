from midiutil import MIDIFile

from src import midi
from src.midi_channels import Channel
from src import midi_chords as mc
from src import midi_items as mi
from src.midi_notes import Duration as dur
from src import midi_parse as mp
from src import midi_voice as mv

def test_1(mocker):
    """Test note/bar clipping."""
    def test(clip: bool):
        bar_info.start = 0
        bar_info.bar = mi.Bar(chords, 1, clip)
        midi.make_bass_bar(bar_info, voice)
        # Check all calls to addNote
        # time     = args[3]
        # duration = args[4]
        calls = mock_add_note.call_args_list
        # Use "-n" indexing because mock accumulates all the calls to it.
        assert calls[-4].args[3] == 0
        assert calls[-4].args[4] == 1000
        assert calls[-3].args[3] == 1000
        assert calls[-3].args[4] == 1000
        assert calls[-2].args[3] == 2000
        assert calls[-2].args[4] == 1000
        assert calls[-1].args[3] == 3000
        last = calls[-1].args[4]
        if clip:
            assert last == 840  # last note has been truncated
        else:
            assert last == 1000 # last note has not been truncated

    lines: list[str] = [
        'voice name=lead1 style=lead voice=rock_organ',
    ]
    commands = mp.Commands(lines)
    channel = Channel.ch1
    track = 1
    midi_file = MIDIFile()
    mock_add_note = mocker.patch.object(midi_file, 'addNote')
    voice: mv.Voice = mv.Voice('vtest', track, channel, 30, 'bass')
     # Use rhythms that extend past the end of the bar:
    voice.rhythms = [[1000,1000,1000,1000,]]
   # Set error values to 0 so time and duration checks do not fail
    # because they have been adjusted by a small error,
    voice.err_dur = 0
    voice.err_tim = 0
    voice.err_vol = 0
    bar_info: midi.BarInfo = midi.BarInfo(midi_file)
    chords: list[mc.Chord] = [mc.Chord(0, 'C', 'maj', 3)]
    test(False)
    test(True)

class TestBarInfo:
    def test_barinfo1(self):
        """Test notes and silences."""
        lines: list[str] = [
            'bar chords=C',
            'bar chords=C@2,D@7,Em,F@5',
        ]
        midi_file = MIDIFile()
        voice: mv.Voice = mv.Voice('vtest', 1, Channel.ch1, 30, 'bass')
        # Create an object to hold dynamic info about the current bar.
        bar_info: midi.BarInfo = midi.BarInfo(midi_file)
        commands = mp.Commands(lines)
        composition = commands.get_composition()

        # Set position to start of 2nd bar
        bar_info.start = dur.n
        bar_info.position = bar_info.start
        bar_info.bar = composition.items[1]

        assert bar_info.get_octave(voice) == 2
        assert bar_info.get_chord() == 'Cmaj'
        assert bar_info.get_tonic() == 'C'
        # Set position to 3rd beat of 2nd bar
        bar_info.position += dur.h
        assert bar_info.get_octave(voice) == 7
        assert bar_info.get_chord() == 'Emin'
        assert bar_info.get_tonic() == 'E'
