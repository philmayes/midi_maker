from typing import Any

# from src.midi_chords import Chord
import src.midi_chords as mc
import src.midi_items as mi
# from src.midi_items import midi_items as mi
from src.midi_notes import Duration as dur
import src.midi_parse as mp
import src.midi_types as mt
from src.midi_voice import Voice
import src.midi_voices as mv

"""
assert isinstance(item, mi.Bar) has started failing since the midi_maker
modules were moved into src/
E AssertionError: assert False
E  +  where False = isinstance(<<midi_items.Bar.Bar object at 0x00000253B5806510>,
                               <class 'src.midi_items.Bar'>)
E  +    where <class 'src.midi_items.Bar'> = mi.Bar
i.e. the Bar instances are not seen as the same.
It is because commands.get_composition() imports objects from other modules
at the same level.
The fix is to replace isinstance with same_name which compares names.
"""
def same_name(obj_: Any, type_: type) -> bool:
    return obj_.__class__.__name__ == type_.__name__

class TestBar:
    def test_bar1(self):
        """Test a single chord."""
        lines: list[str] = [
            'bar chords=Cmaj',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Bar)
        bar_chord: mc.Chord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'

    def test_bar2(self):
        """Test two chords without duration."""
        lines: list[str] = [
            'bar chords=Cmaj,G',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Bar)
        bar_chord: mc.Chord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'
        bar_chord: mc.Chord = item.chords[1]
        assert bar_chord.start == dur.quarter
        assert bar_chord.key == 'G'
        assert bar_chord.chord == 'maj'

    def test_bar3(self):
        """Test two chords with duration."""
        lines: list[str] = [
            'bar chords=hCmaj,G',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Bar)
        bar_chord: mc.Chord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'
        bar_chord: mc.Chord = item.chords[1]
        assert bar_chord.start == dur.half
        assert bar_chord.key == 'G'
        assert bar_chord.chord == 'maj'

    def test_bar4(self):
        """Test two chords with dotted duration."""
        lines: list[str] = [
            'bar chords=h.Cmaj,G',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Bar)
        bar_chord: mc.Chord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'
        bar_chord: mc.Chord = item.chords[1]
        assert bar_chord.start == dur.half + dur.quarter
        assert bar_chord.key == 'G'
        assert bar_chord.chord == 'maj'

    def test_bar5(self):
        """Test chords with different durations."""
        lines: list[str] = [
            'bar chords=eC,G,F',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Bar)
        chords: list[mc.Chord] = item.chords
        #                              start  key   chord  octave
        assert chords[0] == mc.Chord(      0, 'C', 'maj', mc.Chord.no_octave)
        assert chords[1] == mc.Chord(1*dur.e, 'G', 'maj', mc.Chord.no_octave)
        assert chords[2] == mc.Chord(3*dur.e, 'F', 'maj', mc.Chord.no_octave)

class TestComposition:
    lines1: list[str] = [
        'voice name=bass style=bass voice=electric_bass_picked',
        'rhythm name=bass durations=h,q,q',
        'composition name=wabash',
        'timesig value=4/4',
        'tempo  bpm=140',
        'rhythm voices=bass rhythms=bass',
        'volume voices=bass level=100',
        'bar    chords=C',
        'bar    chords=G',
    ]
    lines2: list[str] = [
        'voice name=bass style=bass voice=electric_bass_picked',
        'rhythm name=bass durations=h,q,q',
        'composition name=one',
        'bar    chords=C',
        'composition name=two',
        'bar    chords=G',
        'bar    chords=A',
    ]
    lines3: list[str] = [
        'voice name=bass style=bass voice=electric_bass_picked',
        'rhythm name=bass durations=h,q,q',
        'bar    chords=C',
        'composition name=two',
        'bar    chords=G',
        'bar    chords=A',
    ]

    def expect(self, comp: mi.Composition, length: int, key: str):
        """Assert that the item list has correct length and key."""
        assert len(comp.items) == length
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Bar)
        assert item.chords[0].key == key

    def test_composition1(self):
        """Test that a composition is found when no name supplied."""
        commands = mp.Commands(TestComposition.lines1)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 6
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.TimeSig)

    def test_composition2(self):
        """Test that a composition is found when name is supplied."""
        commands = mp.Commands(TestComposition.lines1)
        comp: mi.Composition = commands.get_composition('wabash')
        assert len(comp.items) == 6
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.TimeSig)

    def test_composition3(self):
        """Test that no composition is found when wrong name supplied."""
        commands = mp.Commands(TestComposition.lines1)
        comp: mi.Composition = commands.get_composition('wrong')
        assert len(comp.items) == 0

    def test_composition4(self):
        """Two named compositions; get the 1st one."""
        commands = mp.Commands(TestComposition.lines2)
        comp: mi.Composition = commands.get_composition('one')
        self.expect(comp, 1, 'C')

    def test_composition5(self):
        """Two named compositions; get the 2nd one."""
        commands = mp.Commands(TestComposition.lines2)
        comp: mi.Composition = commands.get_composition('two')
        self.expect(comp, 2, 'G')

    def test_composition6(self):
        """Two named compositions; get unnamed one."""
        commands = mp.Commands(TestComposition.lines2)
        comp: mi.Composition = commands.get_composition('')
        self.expect(comp, 1, 'C')

    def test_composition7(self):
        """Two compositions, 1st unnamed; get unnamed one."""
        commands = mp.Commands(TestComposition.lines3)
        comp: mi.Composition = commands.get_composition('')
        self.expect(comp, 1, 'C')

    def test_composition8(self):
        """Two compositions, 1st unnamed; get named one."""
        commands = mp.Commands(TestComposition.lines3)
        comp: mi.Composition = commands.get_composition('two')
        self.expect(comp, 2, 'G')

class TestLoop:
    def test_loop1(self):
        lines: list[str] = [
            'loop',
            'bar chords=G',
            'bar chords=C',
            'repeat',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 4
        item: mi.Item = comp.items[1]
        assert same_name(item, mi.Bar)
        assert item.chords[0].key == 'G'
        item: mi.Item = comp.items[2]
        assert same_name(item, mi.Bar)
        assert item.chords[0].key == 'C'

class TestPan:
    def test_pan1(self):
        lines: list[str] = [
            'voice name=bass style=bass voice=electric_bass_picked',
            'pan voices=bass level=1',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Pan)

class TestParsing:
    def test_parse2(self):
        """Test detection of unexpected parameter."""
        expect = ['voices', 'overhang', 'octave']
        line = 'effects voices=arp overhang=0.3 octave=4 unexpected=666'
        cmd_dict = mp.parse_command(line)
        assert not mp.expect(cmd_dict, expect)

    def test_parse3(self):
        """Test detection of ambiguous parameter."""
        expect = ['voices', 'overhang', 'octave']
        line = 'effects voices=arp overhang=0.3 o=4'
        cmd_dict = mp.parse_command(line)
        assert not mp.expect(cmd_dict, expect)

    def test_parse4(self):
        """Test recognition of truncated parameters."""
        expect = ['voices', 'overhang', 'octave']
        lines: list[str] = [
            'effects overhang=1.25 oct=4 rev=100'
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Effects)
        assert item.overhang == 1.25
        assert item.octave == 4
        assert item.reverb == 100
        assert item.chorus == None

class TestRhythm:
    def test_rhythm1(self):
        """Test rhythm command that generates a random list of durations."""
        lines: list[str] = [
            'rhythm name=r0 seed=11 rest=0.3 repeat=0.4 durations=d1,h1,q1,c1,m1'
        ]
        commands = mp.Commands(lines)
        # It's impossible to assert anything about the randomly generated rhythm
        # except that it exists.
        assert len(commands.rhythms) == 1
        rhythm: mt.Rhythm = commands.rhythms['r0']
        assert same_name(rhythm, list)
        assert len(rhythm) > 0

    def test_rhythm2(self):
        """Test rhythm command with supplied durations."""
        lines: list[str] = [
            'rhythm name=r0 durations=t_eighth,d_eighth,eighth,q,eighth,e,quarter'
        ]
        commands = mp.Commands(lines)
        assert len(commands.rhythms) == 1
        rhythm: mt.Rhythm = commands.rhythms['r0']
        assert rhythm == [dur.te, dur.de, dur.e, dur.q, dur.e, dur.e, dur.q]

class TestStrToNotes:
    def test_str_to_notes1(self):
        tune: mt.Tune = mp.str_to_notes('nC@5,h-qE,qA,C@6', {})
        assert len(tune) == 4
        # #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.n, 'C',  0, 5, 60)
        assert tune[1] == mt.Note(4*dur.q, dur.q, 'E',  4, 5, 64)
        assert tune[2] == mt.Note(5*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[3] == mt.Note(6*dur.q, dur.q, 'C',  0, 6, 72)

    def test_str_to_notes2(self):
        """Test tune without duration or octave for first note."""
        tune: mt.Tune = mp.str_to_notes('C,h-qE,qA,C6', {})
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
        tune: mt.Tune = mp.str_to_notes('nC@5,h-q,qA,C@6', {})
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

    def test_str_to_notes4(self):
        """Test tune starting with chord, no duration, no octave."""
        tune: mt.Tune = mp.str_to_notes('Emaj,C,h,D@4', {})
        assert len(tune) == 5
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'E',  4, 5, 64)
        assert tune[1] == mt.Note(      0, dur.q, 'Ab', 8, 5, 68)
        assert tune[2] == mt.Note(      0, dur.q, 'B', 11, 5, 71)
        assert tune[3] == mt.Note(1*dur.q, dur.q, 'C',  0, 5, 60)
        assert tune[4] == mt.Note(4*dur.q, dur.q, 'D',  2, 4, 50)

    def test_str_to_notes5(self):
        """Test tune made of other tunes."""
        lines: list[str] = [
            'tune name=tune1 notes=C,D,E',
            'tune name=tune2 notes=F,G,A',
        ]
        commands = mp.Commands(lines)
        assert len(commands.tunes) == 2
        tunes: mt.TuneDict = commands.tunes
        tune: mt.Tune = mp.str_to_notes('tune1,tune2,tune1', tunes)
        assert len(tune) == 9
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'C',  0, 5, 60)
        assert tune[1] == mt.Note(1*dur.q, dur.q, 'D',  2, 5, 62)
        assert tune[2] == mt.Note(2*dur.q, dur.q, 'E',  4, 5, 64)
        assert tune[3] == mt.Note(3*dur.q, dur.q, 'F',  5, 5, 65)
        assert tune[4] == mt.Note(4*dur.q, dur.q, 'G',  7, 5, 67)
        assert tune[5] == mt.Note(5*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[6] == mt.Note(6*dur.q, dur.q, 'C',  0, 5, 60)
        assert tune[7] == mt.Note(7*dur.q, dur.q, 'D',  2, 5, 62)
        assert tune[8] == mt.Note(8*dur.q, dur.q, 'E',  4, 5, 64)

    def test_str_to_notes6(self):
        """Test that tune durations are not inherited."""
        tune: mt.Tune = mp.str_to_notes('E,hC,D@4', {})
        assert len(tune) == 3
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'E',  4, 5, 64)
        assert tune[1] == mt.Note(1*dur.q, dur.h, 'C',  0, 5, 60)
        assert tune[2] == mt.Note(3*dur.q, dur.q, 'D',  2, 4, 50)

    def test_str_to_notes7(self):
        """Test that tune note octave is inherited from prev note."""
        tune: mt.Tune = mp.str_to_notes('E@6,hC,D@4', {})
        assert len(tune) == 3
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'E',  4, 6, 76)
        assert tune[1] == mt.Note(1*dur.q, dur.h, 'C',  0, 6, 72) # octave==6
        assert tune[2] == mt.Note(3*dur.q, dur.q, 'D',  2, 4, 50)

    def test_str_to_notes8(self):
        """Test that tune note octave is inherited from prev chord."""
        tune: mt.Tune = mp.str_to_notes('Emaj@6,hC,D@4', {})
        assert len(tune) == 5
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'E',  4, 6, 76)
        assert tune[1] == mt.Note(      0, dur.q, 'Ab', 8, 6, 80)
        assert tune[2] == mt.Note(      0, dur.q, 'B', 11, 6, 83)
        assert tune[3] == mt.Note(1*dur.q, dur.h, 'C',  0, 6, 72) # octave==6
        assert tune[4] == mt.Note(3*dur.q, dur.q, 'D',  2, 4, 50)

    def test_str_to_notes9(self):
        """Test that tune chord octave is inherited from prev note."""
        tune: mt.Tune = mp.str_to_notes('C@6,hEmaj,D@4', {})
        assert len(tune) == 5
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'C',  0, 6, 72)
        assert tune[1] == mt.Note(1*dur.q, dur.h, 'E',  4, 6, 76) # octave==6
        assert tune[2] == mt.Note(1*dur.q, dur.h, 'Ab', 8, 6, 80)
        assert tune[3] == mt.Note(1*dur.q, dur.h, 'B', 11, 6, 83)
        assert tune[4] == mt.Note(3*dur.q, dur.q, 'D',  2, 4, 50)

    def test_str_to_notes10(self):
        """Test that tune chord octave is inherited from prev note."""
        #          0 1 2 3    4   5  6   7 8  9
        notes = 'q,G,A,B,hC@6,h.C,qC,G@5,A,hB,h.B'
        tune: mt.Tune = mp.str_to_notes(notes, {})
        assert len(tune) == 10
        hdot = dur.h + dur.q
        #                            start    dur name int oct pitch
        assert tune[0] == mt.Note( 1*dur.q, dur.q, 'G',  7, 5, 67)
        assert tune[1] == mt.Note( 2*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[2] == mt.Note( 3*dur.q, dur.q, 'B', 11, 5, 71)
        assert tune[3] == mt.Note( 4*dur.q, dur.h, 'C',  0, 6, 72)
        assert tune[4] == mt.Note( 6*dur.q, hdot , 'C',  0, 6, 72)
        assert tune[5] == mt.Note( 9*dur.q, dur.q, 'C',  0, 6, 72)
        assert tune[6] == mt.Note(10*dur.q, dur.q, 'G',  7, 5, 67)
        assert tune[7] == mt.Note(11*dur.q, dur.q, 'A',  9, 5, 69)

class TestTune:
    def test_tune1(self):
        """Test that a rest is handled & durations are not inherited."""
        lines: list[str] = [
            'tune name=tune1 notes=G@5,h,A,hF,C',
        ]
        commands = mp.Commands(lines)
        assert len(commands.tunes) == 1
        tunes: mt.TuneDict = commands.tunes
        tune: mt.Tune = tunes['tune1']
        assert len(tune) == 4
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'G',  7, 5, 67)
        assert tune[1] == mt.Note(3*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[2] == mt.Note(4*dur.q, dur.h, 'F',  5, 5, 65)
        assert tune[3] == mt.Note(6*dur.q, dur.q, 'C',  0, 5, 60)

    def test_tune2(self):
        """Test multiple notes.

        The 2nd (hB) is longer and overlaps the next note (qA).
        """
        lines: list[str] = [
            'tune name=tune1 notes=G@5+hB,qA,qC',
        ]
        commands = mp.Commands(lines)
        assert len(commands.tunes) == 1
        tunes: mt.TuneDict = commands.tunes
        tune: mt.Tune = tunes['tune1']
        assert len(tune) == 4
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'G',  7, 5, 67)
        assert tune[1] == mt.Note(      0, dur.h, 'B', 11, 5, 71)
        assert tune[2] == mt.Note(1*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[3] == mt.Note(2*dur.q, dur.q, 'C',  0, 5, 60)

    def test_tune3(self):
        """Test multiple notes.

        The 2nd (hB) is longer and overlaps the next note (qA)
        and is a different octave, which should not be propagated.
        """
        lines: list[str] = [
            'tune name=tune1 notes=G@5+hB@6,qA,qC',
        ]
        commands = mp.Commands(lines)
        assert len(commands.tunes) == 1
        tunes: mt.TuneDict = commands.tunes
        tune: mt.Tune = tunes['tune1']
        assert len(tune) == 4
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'G',  7, 5, 67)
        assert tune[1] == mt.Note(      0, dur.h, 'B', 11, 6, 83)
        assert tune[2] == mt.Note(1*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[3] == mt.Note(2*dur.q, dur.q, 'C',  0, 5, 60)

    def test_tune4(self):
        """Test embedded tune.

        The embedded tune should be in the list with the correct start times.
        """
        lines: list[str] = [
            'tune name=tune1 notes=C,D,E',
            'tune name=tune2 notes=G@5,tune1,qA,qC',
        ]
        commands = mp.Commands(lines)
        assert len(commands.tunes) == 2
        tunes: mt.TuneDict = commands.tunes
        tune: mt.Tune = tunes['tune2']
        assert len(tune) == 6
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'G',  7, 5, 67)
        assert tune[1] == mt.Note(  dur.q, dur.q, 'C',  0, 5, 60)
        assert tune[2] == mt.Note(2*dur.q, dur.q, 'D',  2, 5, 62)
        assert tune[3] == mt.Note(3*dur.q, dur.q, 'E',  4, 5, 64)
        assert tune[4] == mt.Note(4*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[5] == mt.Note(5*dur.q, dur.q, 'C',  0, 5, 60)

    def test_tune5(self):
        """Test embedded tune with overlapping notes.

        The embedded tune should be in the list with the correct start times.
        """
        lines: list[str] = [
            'tune name=tune1 notes=C+hG,D,E',
            'tune name=tune2 notes=G@5,tune1,qA,qC',
        ]
        commands = mp.Commands(lines)
        assert len(commands.tunes) == 2
        tunes: mt.TuneDict = commands.tunes
        tune: mt.Tune = tunes['tune2']
        assert len(tune) == 7
        #                           start    dur name int oct pitch
        assert tune[0] == mt.Note(      0, dur.q, 'G',  7, 5, 67)
        assert tune[1] == mt.Note(  dur.q, dur.q, 'C',  0, 5, 60)
        assert tune[2] == mt.Note(  dur.q, dur.h, 'G',  7, 5, 67)
        assert tune[3] == mt.Note(2*dur.q, dur.q, 'D',  2, 5, 62)
        assert tune[4] == mt.Note(3*dur.q, dur.q, 'E',  4, 5, 64)
        assert tune[5] == mt.Note(4*dur.q, dur.q, 'A',  9, 5, 69)
        assert tune[6] == mt.Note(5*dur.q, dur.q, 'C',  0, 5, 60)

class TestVolume:
    def test_volume1(self):
        """Test non-zero level."""
        lines: list[str] = [
            'voice name=bass style=bass voice=electric_bass_picked',
            'volume voices=bass level=1',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Volume)
        assert item.delta == None
        assert item.level == 1
        assert item.rate == 0

    def test_volume2(self):
        """Test zero level."""
        lines: list[str] = [
            'voice name=bass style=bass voice=electric_bass_picked',
            'volume voices=bass level=0',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Volume)
        assert item.delta == None
        assert item.level == 0
        assert item.rate == 0

    def test_volume3(self):
        """Test delta."""
        lines: list[str] = [
            'voice name=bass style=bass voice=electric_bass_picked',
            'volume voices=bass level=-20 rate=4',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 1
        item: mi.Item = comp.items[0]
        assert same_name(item, mi.Volume)
        assert item.delta == -20
        assert item.level == None
        assert item.rate == 4

    def test_volume4(self):
        """Test no level or delta."""
        lines: list[str] = [
            'voice name=bass style=bass voice=electric_bass_picked',
            'volume voices=bass rate=4',
        ]
        commands = mp.Commands(lines)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 0

class TestVoiceDefinition:
    def test_voice1(self):
        """Test normal voice command."""
        lines: list[str] = [
            'voice name=lead1 style=lead voice=rock_organ',
        ]
        commands = mp.Commands(lines)
        assert len(commands.voices) == 1
        voice: Voice = commands.voices[0]
        assert voice.name == 'lead1'
        assert voice.style == 'lead'
        assert voice.voice == mv.voices['rock_organ'] - 1

    def test_voice2(self):
        """Test normal voice command with numeric voice, min, max."""
        lines: list[str] = [
            'voice name=lead1 style=lead voice=16 min_pitch=40 max_pitch=60',
        ]
        commands = mp.Commands(lines)
        assert len(commands.voices) == 1
        voice: Voice = commands.voices[0]
        assert voice.name == 'lead1'
        assert voice.style == 'lead'
        assert voice.voice == 15
        assert voice.min_pitch == 40
        assert voice.max_pitch == 60

    def test_voice3(self):
        """Test voice command with invalid text voice."""
        lines: list[str] = [
            'voice name=lead1 style=perc voice=john_lennon',
        ]
        commands = mp.Commands(lines)
        assert len(commands.voices) == 0

    def test_voice4(self):
        """Test voice command with invalid numeric voice."""
        lines: list[str] = [
            'voice name=lead1 style=perc voice=16',
        ]
        commands = mp.Commands(lines)
        assert len(commands.voices) == 0

    def test_voice5(self):
        """Test normal voice command with min, max wrong."""
        lines: list[str] = [
            'voice name=lead1 style=improv voice=16 min_pitch=70 max_pitch=60',
        ]
        commands = mp.Commands(lines)
        assert len(commands.voices) == 1
        voice: Voice = commands.voices[0]
        assert voice.min_pitch == 0
        assert voice.max_pitch == 127
