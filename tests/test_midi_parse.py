import midi_items as mi
# import midi_notes as mn
from midi_notes import Duration as dur
import midi_parse as mp
import midi_types as mt
from midi_voice import Voice
import midi_voices

lines: list[str] = [
# 'voice name=lead1 style=lead voice=rock_organ volume=120',
'bar chords=Cmaj',
]

def test_bar1():
    """Test a single chord."""
    lines: list[str] = [
        'bar chords=Cmaj',
    ]
    commands = mp.Commands(lines)
    comp: mi.Composition = commands.get_composition()
    assert len(comp.items) == 1
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    bar_chord: mt.BarChord = item.chords[0]
    assert bar_chord.start == 0
    assert bar_chord.key == 'C'
    assert bar_chord.chord == 'maj'

def test_bar2():
    """Test two chords without duration."""
    lines: list[str] = [
        'bar chords=Cmaj,G',
    ]
    commands = mp.Commands(lines)
    comp: mi.Composition = commands.get_composition()
    assert len(comp.items) == 1
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    bar_chord: mt.BarChord = item.chords[0]
    assert bar_chord.start == 0
    assert bar_chord.key == 'C'
    assert bar_chord.chord == 'maj'
    bar_chord: mt.BarChord = item.chords[1]
    assert bar_chord.start == dur.quarter
    assert bar_chord.key == 'G'
    assert bar_chord.chord == 'maj'

def test_bar3():
    """Test two chords with duration."""
    lines: list[str] = [
        'bar chords=hCmaj,G',
    ]
    commands = mp.Commands(lines)
    comp: mi.Composition = commands.get_composition()
    assert len(comp.items) == 1
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    bar_chord: mt.BarChord = item.chords[0]
    assert bar_chord.start == 0
    assert bar_chord.key == 'C'
    assert bar_chord.chord == 'maj'
    bar_chord: mt.BarChord = item.chords[1]
    assert bar_chord.start == dur.half
    assert bar_chord.key == 'G'
    assert bar_chord.chord == 'maj'

def test_bar4():
    """Test two chords with dotted duration."""
    lines: list[str] = [
        'bar chords=h.Cmaj,G',
    ]
    commands = mp.Commands(lines)
    comp: mi.Composition = commands.get_composition()
    assert len(comp.items) == 1
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    bar_chord: mt.BarChord = item.chords[0]
    assert bar_chord.start == 0
    assert bar_chord.key == 'C'
    assert bar_chord.chord == 'maj'
    bar_chord: mt.BarChord = item.chords[1]
    assert bar_chord.start == dur.half + dur.quarter
    assert bar_chord.key == 'G'
    assert bar_chord.chord == 'maj'

def loop1():
    lines: list[str] = [
        'loop',
        'bar chords=G',
        'bar chords=C',
        'repeat',
    ]
    commands = mp.Commands(lines)
    comp: mi.Composition = commands.get_composition()
    assert len(comp.items) == 4
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    assert item.chords[0].chord.key == 'G'
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    assert item.chords[1].chord.key == 'C'
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    assert item.chords[2].chord.key == 'G'
    item: mi.Item = comp.items[0]
    assert isinstance(item, mi.Bar)
    assert item.chords[3].chord.key == 'C'

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

def test_rhythm1():
    """Test rhythm command that generates a random list of durations."""
    lines: list[str] = [
        'rhythm name=r0 seed=11 silence=0.3 repeat=0.4 durations=d1,h1,q1,c1,m1'
    ]
    commands = mp.Commands(lines)
    # It's impossible to assert anything about the randomly generated rhythm
    # except that it exists.
    assert len(commands.rhythms) == 1
    rhythm: mt.Rhythm = commands.rhythms['r0']
    assert isinstance(rhythm, list)
    assert len(rhythm) > 0

def test_rhythm2():
    """Test rhythm command with supplied durations."""
    lines: list[str] = [
        'rhythm name=r0 durations=t_eighth,d_eighth,eighth,q,eighth,e,quarter'
    ]
    commands = mp.Commands(lines)
    assert len(commands.rhythms) == 1
    rhythm: mt.Rhythm = commands.rhythms['r0']
    assert rhythm == [dur.te, dur.de, dur.e, dur.q, dur.e, dur.e, dur.q]
