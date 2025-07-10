import re
import midi_notes as mn

class Chord:
    def __init__(self, start: int, key: str, chord: str):
        self.start = start
        self.key = key
        self.chord = chord

from midi_notes import note_to_interval

ch1 = r'^([tseqhnd+-\.]+)*'             # duration prefix (needs validating)
ch2 = r'([A-G][#b]*)([a-z]*)([4679]?)$'  # key chord-type chord-mod
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

def chord_to_intervals(chord: str) -> list[int]:
    """Convert a chord name to list of intervals."""
    match = re_chord.match(chord)
    assert match, f'Unknown chord "{str}"'
    chord_name = match.group(2) + match.group(3)
    assert chord_name in chords, f'Unknown chord "{str}"'
    offset: int = note_to_interval[match.group(1)]
    intervals: list[int] = chords[chord_name]
    result: list[int] = [interval + offset for interval in intervals]
    return result

def chord_to_pitches(chord: str, octave: int) -> list[int]:
    """Convert a chord name to list of intervals for a specific octave."""
    assert 0 <= octave < 12, f'Octave {octave} out of range'
    octave *= 12
    intervals: list[int] = chord_to_intervals(chord)
    result: list[int] = [interval + octave for interval in intervals]
    return result

def get_barchord(chord: str) -> tuple[int, Chord]:
    """Parse a string describing a chord into a Chord() and its duration.

    A parsing failure is indicated by duration == 0.
    """
    match = re_dur_chord.match(chord)
    if match:
        dur = match.group(1)
        key = match.group(2)
        cho = match.group(3)
        mod = match.group(4)
        # The regex gets a jumbled duration of "tseqhnd", ".", "+" and "-".
        # get_duration() does further checks for validity.
        if dur is None:
            dur2 = mn.Duration.default
        else:
            dur2 = mn.get_duration(dur)
            if dur2 == 0:
                dur2 = mn.Duration.default
            elif dur2 < 0:
                dur2 = 0
        if not cho:
            if mod == '7':
                cho = 'dom'
            else:
                cho = 'maj'
        elif cho == 'm':
            cho = 'min'
        cho = cho + mod
        if cho in chords:
            return dur2, Chord(0, key, cho)

    return (0, Chord(0,'',''))