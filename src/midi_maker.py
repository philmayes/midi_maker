import argparse
import logging
import os

from midi import make_midi
import midi_help
import midi_play

major = 0
minor = 0
patch = 0
version = f'{major}.{minor}.{patch}'

log_levels = (
    'DEBUG',    # Detailed information, typically of interest only when
                # diagnosing problems.
    'INFO',     # Confirmation that things are working as expected.
    'WARNING',  # An indication that something unexpected happened,
                # or indicative of some problem in the near future, e.g. disk
                # space low. The software is still working as expected.
    'ERROR',    # Due to a more serious problem, the software has not been
                # able to perform some function.
    'CRITICAL', # A serious error, indicating that the program itself may be
                # unable to continue running.
    )
default_log_level = log_levels[2]

def get_logging_level(args:argparse.Namespace) -> int:
    """Gets the logging level: can be partial word, case-insensitive."""
    short_level = args.log.upper()
    for log_level in log_levels:
        if log_level.startswith(short_level):
            return getattr(logging, log_level)
    print(f"Invalid log level '{short_level}'. Defaulting to '{default_log_level}'.")
    return getattr(logging, default_log_level)

def run(args:argparse.Namespace):
    if args.version:
        print(f'Version {version}')
        return
    in_file = args.ini
    if in_file == 'help':
        midi_help.help(args)
        return
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
    parser.add_argument('topic', nargs='?', help=f'Help topic')
    parser.add_argument('-v', '--version', action="store_true", help='version')
    parser.add_argument('-l', '--log', default=default_log_level, help='logging level')
    parser.add_argument('-c', '--create', default='', help='create composition or opus')
    parser.add_argument('-p', '--play', action="store_true", default=False, help='play the generated midi file')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=get_logging_level(args))


    try:
        run(args)
    except Exception as e:
        print(e)
