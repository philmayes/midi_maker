import re
import midi_notes as mn
import midi_types as mt

class Chord:
    no_octave = -1
    def __init__(self, start: int, key: str, chord: str, octave: int):
        self.start = start
        self.key = key
        self.chord = chord
        self.octave = octave

    def __eq__(self, other):
        return self.start == other.start and\
               self.key == other.key and\
               self.chord == other.chord and\
               self.octave == other.octave

ch1 = r'^([tseqhnd+-\.]+)*'             # duration prefix (needs validating)
ch2 = r'([A-G][#b]*)([a-z]*)([4679]?)(@(\d))?$'  # key chord-type chord-mod
re_chord = re.compile('^' + ch2)        # chord
re_dur_chord = re.compile(ch1 + ch2)    # duration + chord

chords: dict[str, list[int]]  = {
    'maj':  [0, 4, 7],        # C E  G
    'min':  [0, 3, 7],        # C Eb G
    'dim':  [0, 3, 6],        # C Eb Gb
    'aug':  [0, 4, 8],        # C E  G#
    'maj7': [0, 4, 7, 11],    # C E  G  B
    'min7': [0, 3, 7, 10],    # C Eb G  Bb
    'dom7': [0, 4, 7, 10],    # C E  G  Bb
    'dim7': [0, 3, 6, 9],     # C Eb Gb A
    'maj6': [0, 4, 7, 9],     # C E  G  A
    'min6': [0, 3, 7, 9],     # C Eb G  A
    'maj9': [0, 4, 7, 11, 14],# C E  G  B  D
    'min9': [0, 3, 7, 10, 14],# C Eb G  Bb D
    'sus4': [0, 5, 7],        # C F  G
}

def chord_to_intervals(text: str) -> list[int]:
    """Convert a chord name to list of intervals."""
    match = re_chord.match(text)
    assert match, f'Unknown chord "{text}"'
    chord_name = match.group(2) + match.group(3)
    assert chord_name in chords, f'Unknown chord "{text}"'
    offset: int = mn.note_to_interval[match.group(1)]
    intervals: list[int] = chords[chord_name]
    result: list[int] = [interval + offset for interval in intervals]
    return result
interval_to_note: list[str] = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']

def chord_to_pitches(chord: str, octave: int) -> list[int]:
    """Convert a chord name to list of intervals for a specific octave."""
    assert 0 <= octave < 12, f'Octave {octave} out of range'
    octave *= 12
    intervals: list[int] = chord_to_intervals(chord)
    result: list[int] = [interval + octave for interval in intervals]
    return result

def get_chord(text: str) -> tuple[int, Chord]:
    """Parse a string describing a chord into duration and Chord().

    Return duration: > 0   This duration was supplied
                     = 0   No duration was supplied
                     < 0   Parsing failed
    """
    match = re_dur_chord.match(text)
    if match:
        dur = match.group(1)
        key = match.group(2)
        cho = match.group(3)
        mod = match.group(4)
        oct = match.group(6)
        # The regex gets a jumbled duration of "tseqhnd", ".", "+" and "-".
        # get_duration() does further checks for validity.
        if dur is None:
            dur2 = 0
        else:
            dur2 = mn.get_duration(dur) # Has same meanings as above.
        if not cho:
            if mod == '7':
                cho = 'dom'
            else:
                cho = 'maj'
        elif cho == 'm':
            cho = 'min'
        cho = cho + mod
        if cho in chords:
            octave = Chord.no_octave if oct is None else int(oct)
            return dur2, Chord(0, key, cho, octave)

    return (-1, Chord(0,'','', Chord.no_octave))

def str_to_notes(text: str, start: int, last_dur: int, octave: int) -> mt.Notes:
    """Convert a chord name to a list of Note instances."""
    result: mt.Notes = []
    dur, chord = get_chord(text)
    if dur >= 0:
        if dur == 0:
            dur = last_dur
        offset: int = mn.note_to_interval[chord.key]
        intervals: list[int] = chords[chord.chord]
        for interval in intervals:
            interval += offset
            pitch = interval + octave * 12
            interval %= 12
            name = interval_to_note[interval]
            octave2 = pitch // 12
            note = mt.Note(start, dur, name, interval, octave2, pitch)
            result.append(note)
    return result
