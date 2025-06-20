import re

from midi_notes import note_to_offset

ch1 = r'([t|d]?[dhqcmsb])?'             # duration prefix
ch2 = r'([A-G][#b]*)([a-z]*)([679]?)$'  # key chord-type chord-mod
re_chord = re.compile(ch2)              # chord
re_dur_chord = re.compile(ch1 + ch2)    # duration + chord

maj = [0, 4, 7]         # C E  G
min = [0, 3, 7]         # C Eb G
dim = [0, 3, 6]         # C Eb Gb
aug = [0, 4, 8]         # C E  G#
maj7 = [0, 4, 7, 11]    # C E  G  B
min7 = [0, 3, 7, 10]    # C Eb G  Bb
dom7 = [0, 4, 7, 10]    # C E  G  Bb
dim7 = [0, 3, 6, 9]     # C Eb Gb Bbb
maj6 = [0, 4, 7, 9]     # C E  G  A
min6 = [0, 3, 7, 9]     # C Eb G  A
maj9 = [0, 4, 7, 11]    # C E  G  B  D
min9 = [0, 3, 7, 10]    # C Eb G  Bb D

chords: dict[str, list[int]]  = {
    'maj': maj,
    'min': min,
    'dim': dim,
    'aug': aug,
    'maj7': maj7,
    'min7': min7,
    'dom7': dom7,
    'dim7': dim7,
    'maj6': maj6,
    'min6': min6,
    'maj9': maj9,
    'min9': min9,
}

def chord_to_intervals(chord: str) -> list[int]:
    """Convert a chord name to list of intervals."""
    match = re_chord.match(chord)
    assert match, f'Unknown chord "{str}"'
    chord_name = match.group(2) + match.group(3)
    assert chord_name in chords, f'Unknown chord "{str}"'
    offset: int = note_to_offset[match.group(1)]
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
