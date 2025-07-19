"""Dumps midi file events to stdout."""
"""
For use, see:
  https://mido.readthedocs.io/en/stable/intro.html
  https://www.twilio.com/en-us/blog/developers/tutorials/building-blocks/working-with-midi-data-in-python-using-mido
"""

import argparse

from mido import MidiFile

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='dump MIDI file')
    parser.add_argument('input', help=f'MIDI file to dump')
    args = parser.parse_args()

    mid = MidiFile(args.input, clip=True)
    print(mid)
