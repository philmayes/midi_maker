from src import midi_items as mi
from src.midi_notes import Duration as dur
from src import midi_parse as mp
from src import midi_types as mt
from src.midi_voice import Voice
from src import midi_voices

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
        assert isinstance(item, mi.Bar)
        bar_chord: mt.BarChord = item.chords[0]
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
        assert isinstance(item, mi.Bar)
        bar_chord: mt.BarChord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'
        bar_chord: mt.BarChord = item.chords[1]
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
        assert isinstance(item, mi.Bar)
        bar_chord: mt.BarChord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'
        bar_chord: mt.BarChord = item.chords[1]
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
        assert isinstance(item, mi.Bar)
        bar_chord: mt.BarChord = item.chords[0]
        assert bar_chord.start == 0
        assert bar_chord.key == 'C'
        assert bar_chord.chord == 'maj'
        bar_chord: mt.BarChord = item.chords[1]
        assert bar_chord.start == dur.half + dur.quarter
        assert bar_chord.key == 'G'
        assert bar_chord.chord == 'maj'

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
        assert isinstance(item, mi.Bar)
        assert item.chords[0].key == key

    def test_composition1(self):
        """Test that a composition is found when no name supplied."""
        commands = mp.Commands(TestComposition.lines1)
        comp: mi.Composition = commands.get_composition()
        assert len(comp.items) == 6
        item: mi.Item = comp.items[0]
        assert isinstance(item, mi.TimeSig)

    def test_composition2(self):
        """Test that a composition is found when name is supplied."""
        commands = mp.Commands(TestComposition.lines1)
        comp: mi.Composition = commands.get_composition('wabash')
        assert len(comp.items) == 6
        item: mi.Item = comp.items[0]
        assert isinstance(item, mi.TimeSig)

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

class TestRhythm:
    def test_rhythm1(self):
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

    def test_rhythm2(self):
        """Test rhythm command with supplied durations."""
        lines: list[str] = [
            'rhythm name=r0 durations=t_eighth,d_eighth,eighth,q,eighth,e,quarter'
        ]
        commands = mp.Commands(lines)
        assert len(commands.rhythms) == 1
        rhythm: mt.Rhythm = commands.rhythms['r0']
        assert rhythm == [dur.te, dur.de, dur.e, dur.q, dur.e, dur.e, dur.q]

class TestVoice:
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
        assert voice.voice == midi_voices.voices['rock_organ']

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
        assert voice.voice == 16
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
