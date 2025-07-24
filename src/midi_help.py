import argparse

import midi_chords as mc
import midi_notes as mn
import midi_percussion as mp
import midi_voice as mv
import midi_voices
import midi_volume as mvol

topics = """\
instruments
percussion
chords
commands
styles
volumes
"""
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
        loop
        mute
        opus
        play
        repeat
        rhythm
        tempo
        timesig
        unmute
        volume
See README.md for details.\
"""
chord_help = """\
A missing chord is a major: "C" is "Cmaj".
A missing chord with the 7th is a dominant: "D7" is "Ddom7".
You can create your own chord with a command in the .ini file like
    "chord name=pairs notes=C,D,E,F#"
The chord is in the key of C. You can create an inversion thus:
    "chord name=inv notes=E,G,C"\
"""
vol_help = """\
are the default values for
the styles with the same names. You can override or add to the
existing volume settings with a command in the .ini file like
    "volume name=vname level=#"\
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

def instruments():
    print("""The following instrument sounds are available:""")
    print_2cols(midi_voices.voices, True)

def percussion():
    print("""The following percussion sounds are available:""")
    print_2cols(mp.percussion)

def styles():
    print("""The following styles are available for voices:""")
    for name, level in mvol.dynamics.items():
        print(f'    {name:10} = {level:>4}')
    for name in mv.styles.keys():
        print(f'    {name}')

def volumes():
    print("""The following names can be used for volume levels:""")
    styles = list(mv.volume.items())
    for name, level in mvol.dynamics.items():
        print(f'    {name:10} = {level:>4}')
    for name, level in styles:
        print(f'    {name:10} = {level:>4}')
    print(f'The volumes called {styles[0][0]}...{styles[-1][0]} ', end = '')
    print(vol_help)

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
