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
# The duration is one or more of the shorthand NoteDurations
# with a possible dot suffix to add 50%. Durations can be added
# together, e.g. q+m or c.+c and are parsed using a secondary regex.
re_note = re.compile(r'([tdhqcmsb+\.]*)([A-G|X][#|b]?)(\d)?$')
re_duration = re.compile(r'([t|d]?[dhqcmsb])?(\.)?$')

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
    h = semiquaver  # The only shorthand that is not the first letter
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

def get_duration(text: str) -> int:
    """Translates the duration string into ticks."""
    total: int = 0
    if text:
        for bit in text.split('+'):
            match = re_duration.match(bit)
            if match is None:
                # logging.error(f'Bad duration: "{bit}')
                break
            dur = match.group(1)
            dot = match.group(2)
            d = NoteDuration.__dict__
            if dur not in d:
                logging.error(f'Bad duration: "{bit}')
                break
            duration =  d[dur]
            if dot:
                duration *= 3
                duration //= 2
            total += duration
    return total

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
        duration = get_duration(text)
        if neg:
            duration = -duration
        return duration
        # logging.warning(f'Duration "{text}" not recognized')
    return NoteDuration.default

def str_to_note(note_str: str) -> Note:
    """Returns the note described by the string."""
    match = re_note.match(note_str)
    if match:
        # process the duration
        duration = match.group(1)
        ticks = get_duration(duration)
        if ticks == 0:
            ticks = NoteDuration.default

        # process the note
        name = match.group(2)
        # A note of X is silence; indicate this with pitch < 0.
        if name == 'X':
            note_pitch = -1000
        else:
            note_pitch = note_to_offset[name]

        # process the octave
        octave = match.group(3)
        if not octave:
            octave = 4
        octave = int(octave)
        octave_pitch = octave * 12

        pitch = note_pitch + octave_pitch
        return Note(ticks, name, octave, pitch)

    return Note(0, '', 0, 0)

def str_to_notes(notes: str) -> Tune:
    """Returns the notes (duration and pitch) described by the string."""
    tune: Tune = []
    last_duration = 0
    last_octave_pitch = -1
    first = True
    for note_str in notes.split(','):
        note = str_to_note(note_str)
        if not note.name:
            logging.error(f'Bad note: "{note_str}"')
            continue
        if first:
            last_duration = note.duration
            last_octave_pitch = note.octave * 12
            first = False
        else:
            if note.duration == 0:
                note.duration = last_duration
            if note.octave == 0:
                note.octave = last_octave_pitch
        tune.append(note)

    return tune
