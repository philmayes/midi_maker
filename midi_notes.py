import logging
import re

from midi_types import *

note_to_offset: dict[str, int] = {
    'Cb':11, 'C':  0, 'C#': 1,
    'Db': 1, 'D':  2, 'D#': 3,
    'Eb': 3, 'E':  4, 'E#': 5,
    'Fb': 4, 'F':  5, 'F#': 6,
    'Gb': 6, 'G':  7, 'G#': 8,
    'Ab': 8, 'A':  9, 'A#':10,
    'Bb':10, 'B': 11, 'B#':12,
}
# Format of a note as supplied by tune command. Takes the format:
# duration note octave. Succeeding notes can omit the duration
# or octave; they will be picked up from the preceding note.
# The note is (roughly) the first letter of the NoteDuration
# with an optional prefix of t or d for triplets or doublets.
re_note = re.compile(r'([t|d]?[dhqcmsb])?(\.)?([A-G|X][#|b]?)(\d)?')

class NoteDuration:
    # note durations
    demisemiquaver = 120    # thirtysecond note      120
    semiquaver = 2 * demisemiquaver # sixteenth note 240
    quaver = 2 * semiquaver # eighth note            480
    crotchet = 2 * quaver   # quarter note           960
    minim = 2 * crotchet    # half note             1920
    semibreve = 2 * minim   # whole note            3840
    breve = 2 * semibreve   # double whole note     7680
    # triplets
    t_demisemiquaver = demisemiquaver // 3  #         40
    t_semiquaver = 2 * t_demisemiquaver     #         80
    t_quaver = 2 * t_semiquaver             #        160
    t_crotchet = 2 * t_quaver               #        320
    t_minim = 2 * t_crotchet                #        640
    t_semibreve = 2 * t_minim               #       1280
    t_breve = 2 * t_semibreve               #       2560
    # doublets, i.e. 2 x triplets, so triplet + doublet = note
    d_demisemiquaver = 2 * t_demisemiquaver #         80
    d_semiquaver = 2 * d_demisemiquaver     #        160
    d_quaver = 2 * d_semiquaver             #        320
    d_crotchet = 2 * d_quaver               #        640
    d_minim = 2 * d_crotchet                #       1280
    d_semibreve = 2 * d_minim               #       2560
    d_breve = 2 * d_semibreve               #       5120
    # shorthand
    d = demisemiquaver
    h = semiquaver
    q = quaver
    c = crotchet
    m = minim
    s = semibreve
    b = breve
    td = t_demisemiquaver
    th = t_semiquaver
    tq = t_quaver
    tc = t_crotchet
    tm = t_minim
    ts = t_semibreve
    tb = t_breve
    dd = d_demisemiquaver
    dh = d_semiquaver
    dq = d_quaver
    dc = d_crotchet
    dm = d_minim
    ds = d_semibreve
    db = d_breve
    default = crotchet  # used when duration is not supplied

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

def str_to_duration(text: str) -> int:
    """Returns the note duration described by the string."""
    if text:
        # A leading minus sign inverts the value of the note
        neg = text[0] == '-'
        if neg:
            text = text[1:]
        # Direct numbers are accepted.
        if text.isdigit():
            return int(text)
        # Look up the name and return its value
        d = NoteDuration.__dict__
        if text in d:
            duration =  d[text]
            if neg:
                duration = -duration
            return duration
        logging.warning(f'Duration "{text}" not recognized')
    return NoteDuration.default

def str_to_note(note_str: str) -> Note:
    """Returns the note described by the string."""
    match = re_note.match(note_str)
    if match:
        # process the duration
        duration = match.group(1)
        if not duration:
            ticks = NoteDuration.default
        else:
            ticks = get_duration(duration)
            dot = match.group(2)
            if dot is not None:
                ticks += ticks // 2
            last_duration = ticks

        # process the note
        note = match.group(3)
        # A note of X is silence; indicate this with pitch < 0.
        if note == 'X':
            note_pitch = -1000
        else:
            note_pitch = note_to_offset[note]

        # process the octave
        octave = match.group(4)
        if not octave:
            octave = 4
        octave = int(octave)
        octave_pitch = octave * 12

        pitch = note_pitch + octave_pitch
        # print(f'{note_str}=={pitch}')
        return Note(ticks, note, octave, pitch)

    return Note(0, '', 0, 0)

def str_to_notes(notes: str) -> Tune:
    """Returns the notes (duration and pitch) described by the string."""
    tune: Tune = []
    last_duration = 0
    last_octave_pitch = -1
    first = True
    for note_str in notes.split(','):
        note = str_to_note(note_str)
        if first:
            last_duration = note.duration
            last_octave_pitch = note.octave * 12
        tune.append(note)

    return tune
