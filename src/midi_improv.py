from typing import NamedTuple, TypeAlias

import midi_chords as mc
import midi_items as mi
import midi_notes as mn
import rando

NoteList: TypeAlias = list[str]
class KeyChord(NamedTuple):
    key: str
    name: str
    notes: NoteList

    def __str__(self):
        return f'{self.key}{self.name}'

all: list[KeyChord] = []

def get_all() -> list[KeyChord]:
    # Construct a list of all known chords.
    all: list[KeyChord] = []
    for n in range(12):
        k = mn.interval_to_note[n]
        for name, ints in mc.chords.items():
            notes: NoteList = [mn.interval_to_note[(n + i) % 12] for i in ints]
            all.append(KeyChord(k, name, notes))
    return all

def index_to_key(index: int) -> str:
    return(mn.fifths[(index + 12) % 12])

def key_to_index(key: str) -> int:
    return mn.fifths.index(key)

def key_offset(key: str, offset: int):
    """Get the key that is <offset> semitones away from <key>."""
    return index_to_key(key_to_index(key) + offset)

def get_close(key: str, center: int=0):
    close: list[str] = []
    for offset in range(center - 2, center + 3):
        close.append(key_offset(key, offset))
    return close

def pick_two(notes: NoteList, rgen: rando.Rando) -> NoteList:
    n1 = rgen.choice(notes)
    n2 = n1
    while n2 == n1:
        n2 = rgen.choice(notes)
    return [n1, n2]

def make_bars(prev: mi.Bar, repeat: int, clip: bool, seed: int) -> list[mi.Bar]:
    """Return a list of improvised Bars."""
    # Make a pseudo-random number generator that will be the same for a
    # particular seed.
    rgen: rando.Rando = rando.Rando(seed)
    bars: list[mi.Bar] = [prev]
    for _ in range(repeat):
        bars.append(make_bar(bars[-1], clip, rgen))
    return bars[1:]

def make_bar(prev: mi.Bar, clip: bool, rgen: rando.Rando) -> mi.Bar:

    # Construct a dictionary of all known chords once only.
    global all
    if not all:
        all = get_all()

    # Start with the last one picked.
    # Get its notes.
    last_chord: mc.Chord = prev.chords[-1]
    ints = mc.chords[last_chord.chord]
    n = mn.note_to_interval[last_chord.key]
    cnotes: NoteList = [mn.interval_to_note[(n + i) % 12] for i in ints]
    # Pick two of them.
    two: NoteList = pick_two(cnotes, rgen)
    # Find all the closely-related chords that share these two notes.
    #   New chord x must be within 2 mn.fifths away of:
    #   existing major (M) or minor (m):
    #   mn.fifths:     |  |  m  |  |  M  |  |  |  |  |  |
    #   new major:           x--x--x--x--x
    #   new minor:  x--x--x--x--x
    if last_chord.chord.startswith('min'):
        close_major = get_close(last_chord.key, 3)
        close_minor = get_close(last_chord.key)
    else:
        close_major = get_close(last_chord.key)
        close_minor = get_close(last_chord.key, -3)
    picks: list[KeyChord] = []
    for key_chord in all:
        # Don't repeat a chord
        if key_chord.key == last_chord.key and key_chord.name == last_chord.chord:
            continue
        if key_chord.name.startswith('min'):
            if key_chord.key not in close_minor:
                continue
        else:
            if key_chord.key not in close_major:
                continue
        if two[0] in key_chord.notes and two[1] in key_chord.notes:
            picks.append(key_chord)
    # Pick one of those chords at random.
    x = rgen.choice(picks)
    return mi.Bar([mc.Chord(0, x.key, x.name, last_chord.octave)], 1, clip)
