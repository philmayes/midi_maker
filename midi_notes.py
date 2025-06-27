import logging
import re

import midi_types as mt
from preferences import prefs

note_to_interval: dict[str, int] = {
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
# together, e.g. q+n or q.+q and are parsed using a secondary regex.
re_note = re.compile(r'([tseqhnd+\.]*)([A-G|X][#|b]?)(\d)?$')

n32 = prefs.ticks_per_beat // 8
class NoteDuration:
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

def get_duration(text: str) -> int:
    """Translates the duration string into ticks.

    Expects one or more note names, possibly with a trailing dot,
    and joined with "+" characters.
    """
    total: int = 0
    if text:
        d = NoteDuration.__dict__
        for bit in text.split('+'):
            dur = bit
            dot = dur[-1] == '.'
            if dot:
                dur = dur[:-1]

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
    return NoteDuration.default

def str_to_note(note_str: str) -> mt.Note:
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
            interval = -1000
        else:
            interval = note_to_interval[name]

        # process the octave
        octave = match.group(3)
        if octave is None:
            octave = 0
        # if not octave:
        #     octave = 4
        octave = int(octave)

        pitch = interval + octave * 12
        return mt.Note(ticks, name, interval, octave, pitch)

    return mt.Note(0, '', 0, 0, 0)

def str_to_notes(notes: str) -> mt.Tune:
    """Returns the notes (duration and pitch) described by the string."""
    tune: mt.Tune = []
    last_duration = 0
    last_octave = -1
    first = True
    for note_str in notes.split(','):
        note: mt.Note = str_to_note(note_str)
        if not note.name:
            logging.error(f'Bad note: "{note_str}"')
            continue
        if first:
            last_duration = note.duration
            last_octave = note.octave
            first = False
        else:
            if note.duration == 0:
                note.duration = last_duration
            if note.octave == 0:
                note.octave = last_octave
            last_duration = note.duration
            last_octave = note.octave
        note.pitch = note.interval + note.octave * 12
        # print(note)
        tune.append(note)

    return tune
