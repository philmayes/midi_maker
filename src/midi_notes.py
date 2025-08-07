"""Names of notes and functions for parsing strings of notes."""

import logging
import re

import midi_types as mt

note_to_interval: dict[str, int] = {
    'Cb':11, 'C':  0, 'C#': 1,
    'Db': 1, 'D':  2, 'D#': 3,
    'Eb': 3, 'E':  4, 'E#': 5,
    'Fb': 4, 'F':  5, 'F#': 6,
    'Gb': 6, 'G':  7, 'G#': 8,
    'Ab': 8, 'A':  9, 'A#':10,
    'Bb':10, 'B': 11, 'B#':12,
}
interval_to_note: list[str] = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
fifths: list[str] = ['C','F','Bb','Eb','Ab','C#','F#','B','E','A','D','G',]
# Format of a note as supplied by tune command. Takes the format:
# duration note octave. Succeeding notes can omit the duration
# or octave; they will be picked up from the preceding note.
# The duration is one or more of the shorthand NoteDurations
# with a possible dot suffix to add 50%. Durations can be added
# together, e.g. q+n or q.+q and are parsed using a secondary regex.
re_note = re.compile(r'([tseqhnd+-\.]*)([A-G][#|b]?)(@(\d))?$')

ticks_per_beat = 960
n32 = ticks_per_beat // 8
class Duration:
    # note durations
    thirtysecondth = n32    # thirtysecond note      120
    sixteenth = 2 * thirtysecondth # sixteenth note  240
    eighth = 2 * sixteenth  # eighth note            480
    quarter = 2 * eighth    # quarter note           960
    half = 2 * quarter      # half note             1920
    note = 2 * half         # whole note            3840
    doublenote = 2 * note   # double whole note     7680

    # triplets
    t_thirtysecondth = thirtysecondth // 3  #         40
    t_sixteenth = 2 * t_thirtysecondth      #         80
    t_eighth = 2 * t_sixteenth              #        160
    t_quarter = 2 * t_eighth                #        320
    t_half = 2 * t_quarter                  #        640
    t_note = 2 * t_half                     #       1280
    t_doublenote = 2 * t_note               #       2560

    # doublets, i.e. 2 x triplets, so triplet + doublet = note
    d_thirtysecondth = 2 * t_thirtysecondth #         80
    d_sixteenth = 2 * d_thirtysecondth      #        160
    d_eighth = 2 * d_sixteenth              #        320
    d_quarter = 2 * d_eighth                #        640
    d_half = 2 * d_quarter                  #       1280
    d_note = 2 * d_half                     #       2560
    d_doublenote = 2 * d_note               #       5120

    # shorthand
    t = thirtysecondth
    s = sixteenth
    e = eighth
    q = quarter
    h = half
    n = note
    d = doublenote
    tt = t_thirtysecondth
    ts = t_sixteenth
    te = t_eighth
    tq = t_quarter
    th = t_half
    tn = t_note
    td = t_doublenote
    dt = d_thirtysecondth
    ds = d_sixteenth
    de = d_eighth
    dq = d_quarter
    dh = d_half
    dn = d_note
    dd = d_doublenote
    default = quarter  # used when duration is not supplied

tick_to_name = (
    (999999, 'bad'),
    (11520, 'd.'),
    (7680, 'd'),

    (5760, 'n.'),
    (5120, 'dd'),
    (3840, 'n'),

    (2880, 'h.'),
    (2560, 'td'),   # (2560, 'dn'),
    (1920, 'h'),

    (1440, 'q.'),
    (1280, 'tn'),   # (1280, 'dh'),
    (960, 'q'),

    (720, 'e.'),
    (640, 'th'),    # (640, 'dq'),
    (480, 'e'),

    (360, 's.'),
    (320, 'tq'),    # (320, 'de'),
    (240, 's'),

    (180, 't.'),
    (160, 'te'),    # (160, 'ds'),
    (120, 't'),

    (80, 'ts'),     # (80, 'dt'),
    (40, 'tt'),
)

def duration_to_text(dur: int) -> str:
    neg = '-' if dur < 0 else ''
    dur = abs(dur)
    bits = []
    remaining = round_d(dur)
    table_index = 0
    last_dur = 98765
    while remaining > 0:
        dur, name = tick_to_name[table_index]
        while remaining >= dur:
            remaining -= dur
            half_dur = dur // 2
            if remaining >= half_dur:
                bits.append(name + '.')
                remaining -= half_dur
            else:
                bits.append(name)
        table_index += 1
    return neg + '+'.join(bits)

def durations_to_text(durs: list[int]) -> str:
    bits: list[str] = []
    for dur in durs:
        bits.append(duration_to_text(dur))
    return ','.join(bits)

def round_d(number: int) -> int:
    """Round a duration."""
    min_err = 99999
    val = 99999
    for dur, name in tick_to_name:
        error = abs(number - dur)
        if error < min_err:
            min_err = error
            val = dur
    return val

def get_sub_duration(text: str, silent=False) -> int:
    """Translates the duration string into ticks.

    Expects one or more note names, possibly with a trailing dot,
    and joined with "-" characters.
    The <silent> option is for the benefit of str_to_notes because a tune
    can contain both notes and durations (indicating silences), and
    parsing for durations first would generate error messages.
    Returns: >0 = duration
             =0 = no duration
             <0 = bad duration
    """
    total: int = 0
    first = True
    if text:
        d = Duration.__dict__
        for bit in text.split('-'):
            if bit == '':
                if not silent:
                    logging.error(f'Bad duration: "{text}"')
                total = -1
                break
            dur = bit
            dot = dur[-1] == '.'
            if dot:
                dur = dur[:-1]

            if dur not in d:
                if not silent:
                    logging.error(f'Bad duration: "{bit}"')
                total = -1
                break
            duration =  d[dur]
            if dot:
                duration *= 3
                duration //= 2
            if first:
                total = duration
                first = False
            else:
                total -= duration
    if total <= 0:
        if not silent:
            logging.error(f'Invalid note duration: "{text}"')
        # total = 0
    return total

def get_duration(text: str, silent=False) -> int:
    """Translates the duration string into ticks.

    Expects one or more note names, possibly with a trailing dot,
    and joined with "+" or "-" characters.
    Returns: >0 = duration
             =0 = no duration
             <0 = bad duration
    """
    total: int = 0
    if text:
        d = Duration.__dict__
        for bit in text.split('+'):
            neg = get_sub_duration(bit, silent)
            if neg < 0:
                return -1
            total += neg
    return total

def str_to_duration(text: str, silent=False) -> int:
    """Returns the note duration described by the string.

    Returns: >0 = duration
             <0 = a negative duration
             =0 = bad duration
    """
    if text:
        # A leading minus sign inverts the value of the note
        neg = text[0] == '-'
        if neg:
            text = text[1:]
        # Direct numbers are accepted.
        if text.isdigit():
            return int(text)
        # Look up the name and return its value
        duration = get_duration(text, silent)
        if duration < 0:
            return 0
        if neg:
            duration = -duration
        return duration
    return 0

def str_to_durations(text: str) -> list[int]:
    """Returns the note durations described by the string."""
    if not text:
        return []   # because the code below would return [0]
    durations: list[int] = []
    for note in text.split(','):
        d = str_to_duration(note)
        if d != 0:
            durations.append(d)
    return durations

def str_to_note(note_str: str) -> mt.Note:
    """Returns the note described by the string."""
    match = re_note.match(note_str)
    if match:
        # process the duration
        duration = match.group(1)
        ticks = get_duration(duration)
        if ticks == 0:
            ticks = Duration.default

        # process the note
        name = match.group(2)
        interval = note_to_interval[name]

        # process the octave
        octave = match.group(4)
        if octave is None:
            octave = 0
        else:
            octave = int(octave)

        pitch = interval + octave * 12
        return mt.Note(0, ticks, name, interval, octave, pitch)

    return mt.Note(0, 0, '', 0, 0, 0)
