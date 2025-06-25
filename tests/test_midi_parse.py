import midi_items as mi
from midi_notes import *
import midi_parse as mp
from midi_types import *
from midi_voice import Voice
import midi_voices

lines: list[str] = [
# 'voice name=lead1 style=lead voice=rock_organ volume=120',
'bar chords=Cmaj',
]

def test_bar1():
    lines: list[str] = [
        'bar chords=Cmaj',
    ]
    commands = mp.Commands(lines)
    comp: mi.Composition = commands.get_composition()
    assert len(comp.items) == 1
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    bar_chord: BarChord = item.chords[0]
    assert bar_chord.start == 0
    assert bar_chord.key == 'C'
    assert bar_chord.chord == 'maj'

def test_voice1():
    """Test normal voice command."""
    lines: list[str] = [
        'voice name=lead1 style=lead voice=rock_organ',
    ]
    commands = mp.Commands(lines)
    assert len(commands.voices) == 1
    voice: Voice = commands.voices[0]
    assert voice.name == 'lead1'
    assert voice.style == 'lead'
    assert voice.voice == midi_voices.voices['rock_organ']

def test_voice2():
    """Test normal voice command with numeric voice, min, max."""
    lines: list[str] = [
        'voice name=lead1 style=lead voice=16 min_pitch=40 max_pitch=60',
    ]
    commands = mp.Commands(lines)
    assert len(commands.voices) == 1
    voice: Voice = commands.voices[0]
    assert voice.name == 'lead1'
    assert voice.style == 'lead'
    assert voice.voice == 16
    assert voice.min_pitch == 40
    assert voice.max_pitch == 60

def test_voice3():
    """Test voice command with invalid text voice."""
    lines: list[str] = [
        'voice name=lead1 style=perc voice=john_lennon',
    ]
    commands = mp.Commands(lines)
    assert len(commands.voices) == 0

def test_voice4():
    """Test voice command with invalid numeric voice."""
    lines: list[str] = [
        'voice name=lead1 style=perc voice=16',
    ]
    commands = mp.Commands(lines)
    assert len(commands.voices) == 0

def test_voice5():
    """Test normal voice command with min, max wrong."""
    lines: list[str] = [
        'voice name=lead1 style=improv voice=16 min_pitch=70 max_pitch=60',
    ]
    commands = mp.Commands(lines)
    assert len(commands.voices) == 1
    voice: Voice = commands.voices[0]
    assert voice.min_pitch == 0
    assert voice.max_pitch == 127
