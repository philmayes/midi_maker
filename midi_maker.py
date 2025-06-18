import argparse
import logging
import os

from midi import make_midi
import midi_play

log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
default_log_level = log_levels[2]

def get_logging_level(args:argparse.Namespace) -> str:
    # get the logging level: can be partial word, case-insensitive
    short_level = args.log.upper()
    for log_level in log_levels:
        if log_level.startswith(short_level):
            return log_level
    print(f"Invalid log level '{short_level}'. Defaulting to '{default_log_level}'.")
    return default_log_level

def run(args:argparse.Namespace):
    in_file = args.ini
    if not os.path.exists(in_file):
        logging.critical(f'Input file "{in_file}" does not exist')
        return
    fname, _ = os.path.splitext(in_file)
    out_file =fname + '.mid'

    make_midi(in_file, out_file, args.create)

    if args.play:
        midi_play.play(out_file)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create MIDI file')
    parser.add_argument('ini', nargs='?', default='example.ini', help=f'Data to create MIDI file (default: example.ini)')
    parser.add_argument('-l', '--log', default=default_log_level, help='logging level')
    parser.add_argument('-c', '--create', default='', help='create composition or opus')
    parser.add_argument('-p', '--play', action="store_true", default=False, help='play the generated midi file')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=get_logging_level(args))

    try:
        run(args)
    except Exception as e:
        print(e)
