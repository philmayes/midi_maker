import argparse

import midi_chords as mc
import midi_notes as mn
import midi_percussion as mp
import midi_voices as mv

topics = """\
instruments
percussion
chords
commands
"""
chord_help = """\
A missing chord is a major: "C" is "Cmaj".
A missing chord with the 7th is a dominant: "D7" is "Ddom7".
You can create your own chord with a command in the .ini file like
    "chord name=pairs notes=C,D,E,F#"
The chord is in the key of C. You can create an inversion thus:
    "chord name=inv notes=E,G,C"\
"""
def voice_str(items: dict[str, int], name: str, width: int) -> str:
    no: int = items[name]
    return f'{no:3} {name:{width}}'

def print_2cols(items: dict[str, int], by8: bool=False):
    max_len = 0
    names = list(items.keys())
    max_len = max(len(vv) for vv in names)
    row_count = (len(names)+ 1) // 2
    for n in range(row_count):
        if by8 and n > 0 and n % 8 == 0:
            print()
        print(voice_str(items, names[n], max_len + 1), end='')
        if n + row_count < len(names):
            print(voice_str(items, names[n + row_count], 1))

def chords():
    print('The following chords are available:')
    for name, intervals in mc.chords.items():
        keys = []
        for i in intervals:
            keys.append(f'{mn.interval_to_note[i%12]:3}')
        print(f'    {name:4} = {' '.join(keys)}')
    print(chord_help)

def percussion():
    print("""The following percussion sounds are available:""")
    print_2cols(mp.percussion)

def instruments():
    print("""The following instrument sounds are available:""")
    print_2cols(mv.voices, True)

commands = """\
The commands in the input file can be:
    Definition Commands
        chord
        preferences
        rhythm
        tune
        voice
        volume
    Performance Commands
        bar
        composition
        effects
        hear
        loop
        mute
        opus
        play
        repeat
        rhythm
        tempo
        timesig
        volume
See README.md for details.
"""

def help(args:argparse.Namespace):
    """Print help for command line "midi_maker.py help...."""
    gbls = globals()
    if args.output:
        topic = args.output
        if topic in gbls:
            t2 = gbls[topic]
            if isinstance(t2, str):
                print(t2)
            else:
                t2()
        else:
            print(f'The topic "{topic}" is unknown')
    else:
        print('For help on the following topics, use:')
        for t in topics.split():
            print(f'    help {t}')
