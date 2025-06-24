import midi_items as mi
from midi_notes import *
import midi_parse as mp
from midi_types import *
from midi_voice import Voice

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
