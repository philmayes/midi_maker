import logging
import re

from midi_types import *

note_to_offset = {
    'Cb':11, 'C':  0, 'C#': 1,
    'Db': 1, 'D':  2, 'D#': 3,
    'Eb': 3, 'E':  4, 'E#': 5,
    'Fb': 4, 'F':  5, 'F#': 6,
    'Gb': 6, 'G':  7, 'G#': 8,
    'Ab': 8, 'A':  9, 'A#':10,
    'Bb':10, 'B': 11, 'B#':12,
}
# Format of a note as supplied by tune command.
re_note = re.compile(r'([t|d]?[dhqcmsb])?([A-G|X][#|b]?)(\d)?')

class NoteDuration:
    # note durations
    demisemiquaver = 120    # thirtysecond note
    semiquaver = 2 * demisemiquaver # sixteenth note
    quaver = 2 * semiquaver # eighth note
    crotchet = 2 * quaver   # quarter note
    minim = 2 * crotchet    # half note
    semibreve = 2 * minim   # whole note
    breve = 2 * semibreve   # double whole note
    # triplets
    t_demisemiquaver = demisemiquaver // 3
    t_semiquaver = 2 * t_demisemiquaver
    t_quaver = 2 * t_semiquaver
    t_crotchet = 2 * t_quaver
    t_minim = 2 * t_crotchet
    t_semibreve = 2 * t_minim
    t_breve = 2 * t_semibreve
    # doublets, i.e. 2 x triplets, so triplet + doublet = note
    d_demisemiquaver = 2 * t_demisemiquaver
    d_semiquaver = 2 * d_demisemiquaver
    d_quaver = 2 * d_semiquaver
    d_crotchet = 2 * d_quaver
    d_minim = 2 * d_crotchet
    d_semibreve = 2 * d_minim
    d_breve = 2 * d_semibreve

letter_to_duration = {
    'd': NoteDuration.demisemiquaver,
    'h': NoteDuration.semiquaver,
    'q': NoteDuration.quaver,
    'c': NoteDuration.crotchet,
    'm': NoteDuration.minim,
    's': NoteDuration.semibreve,
    'b': NoteDuration.breve,
}

def get_duration(text: str) -> int:
    duration = letter_to_duration[text[-1]]
    if len(text) == 2:
        factor = text[0]
        duration //= 3
        if factor == 'd':
            duration *= 2
    return duration

def str_to_duration(name: str) -> int:
    """Returns the note duration described by the string."""
    assert len(name) > 0, 'No name provided for note'
    # A leading minus sign inverts the value of the note
    neg = name[0] == '-'
    if neg:
        name = name[1:]
    # Direct numbers are accepted.
    if name.isdigit():
        return int(name)
    # Look up the name and return its value
    d = NoteDuration.__dict__
    if name in d:
        duration =  d[name]
        if neg:
            duration = -duration
        return duration
    logging.warning(f'Duration "{name}" not recognized')
    return 0

def str_to_notes(notes: str) -> Tune:
    """Returns the notes (duration and pitch) described by the string."""
    tune: Tune = []
    last_duration = 0
    last_octave_pitch = -1
    for note_str in notes.split(','):
        match = re_note.match(note_str)
        if match:
            # process the duration
            duration = match.group(1)
            if duration is None:
                if last_duration:
                    ticks = last_duration
                else:
                    logging.warning(f'First note of {notes} must have a duration')
                    ticks = 0
            else:
                ticks = get_duration(duration)
                last_duration = ticks

            # process the note
            note = match.group(2)
            # A note of X is silence; indicate this with pitch < 0.
            if note == 'X':
                note_pitch = -1000
            else:
                note_pitch = note_to_offset[note]

            # process the octave
            octave = match.group(3)
            if octave is None:
                if last_octave_pitch >= 0:
                    octave_pitch = last_octave_pitch
                else:
                    logging.warning(f'First note of {notes} must have an octave')
                    octave_pitch = 36
            else:
                octave_pitch = int(octave) * 12
                last_octave_pitch = octave_pitch

            pitch = note_pitch + octave_pitch
            tune.append((ticks, pitch))

    return tune
