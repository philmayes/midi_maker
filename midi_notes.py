import logging
import re

note_to_offset = {
    'Cb':11, 'C':  0, 'C#': 1,
    'Db': 1, 'D':  2, 'D#': 3,
    'Eb': 3, 'E':  4, 'E#': 5,
    'Fb': 4, 'F':  5, 'F#': 6,
    'Gb': 6, 'G':  7, 'G#': 8,
    'Ab': 8, 'A':  9, 'A#':10,
    'Bb':10, 'B': 11, 'B#':12,
}
re_note = re.compile(r'([t|d]?[dhqcmsb])?([A-G][#|b]?)(\d)')

class Note:
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
    'd': Note.demisemiquaver,
    'h': Note.semiquaver,
    'q': Note.quaver,
    'c': Note.crotchet,
    'm': Note.minim,
    's': Note.semibreve,
    'b': Note.breve,
}

def get_duration(text: str) -> int:
    duration = letter_to_duration[text[-1]]
    if len(text) == 2:
        factor = text[0]
        duration //= 3
        if factor == 'd':
            duration *= 2
    return duration

def str_to_note(name: str) -> tuple[int, int]:
    """Returns the note duration and pitch described by the string."""
    assert len(name) > 0, 'No name provided for note'
    match = re_note.match(name)
    if match:
        duration = match.group(1)
        note = match.group(2)
        octave = match.group(3)
        if duration is None:
            ticks = 0
        else:
            ticks = get_duration(duration)
        if octave is not None:
            if note in note_to_offset:
                pitch = note_to_offset[note] + int(octave) * 12
        return ticks, pitch
    logging.warning(f'{name} is not a valid note')
    return 0, 0

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
    d = Note.__dict__
    if name in d:
        duration =  d[name]
        if neg:
            duration = -duration
        return duration
    logging.warning(f'Note "{name}" not recognized')
    return 0
