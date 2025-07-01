import argparse
import logging
import os

from midi import make_midi
import midi_play
import midi_voices as mv
import midi_percussion as mp


topics = """\
voices
percussion
commands
"""
def voice_str(items: dict[str, int], name: str, width: int) -> str:
    no: int = items[name]
    return f'{no:3} {name:{width}}'

def print_2cols(items: dict[str, int], by8: bool=False):
    max_len = 0
    names = list(items.keys())
    max_len = max(len(vv) for vv in names)
    print(max_len)
    row_count = (len(names)+ 1) // 2
    for n in range(row_count):
        if by8 and n > 0 and n % 8 == 0:
            print()
        print(voice_str(items, names[n], max_len + 1), end='')
        if n + row_count < len(names):
            print(voice_str(items, names[n + row_count], 1))

def percussion():
    print("""help for percussion""")
    print_2cols(mp.percussion)

def voices():
    print("""help for voices""")
    print_2cols(mv.voices, True)

commands = """\
The commands are:
    bar
    chord
    chords
    composition
    hear
    mute
    note durations
    notes
    opus
    play
    rhythm
    rhythm
    tempo
    timesig
    tune
    voice
    volume
See README.md for details.
"""

def help(args:argparse.Namespace):
    gbls = globals()
    if args.topic:
        topic = args.topic
        if topic in gbls:
            t2 = gbls[topic]
            if isinstance(t2, str):
                print(t2)
            else:
                t2()
        else:
            print(f'the topic {topic} is unknown')
    else:
        print('For help on the following topics, use:')
        for t in topics.split():
            print(f'    help {t}')
