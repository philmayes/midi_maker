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
    in_file = args.input
    # The first parameter does double duty as input filename and help request.
    if in_file == 'help':
        midi_help.help(args)
        return
    if not os.path.exists(in_file):
        logging.critical(f'Input file "{in_file}" does not exist')
        return

    # Assemble the output filename:
    #   if 2nd param is a directory, use the input filename there
    #   if 2nd param is a filename, use it
    #   else use the input filename in the input directory
    out_file = args.output
    if out_file == '':
        fname, _ = os.path.splitext(in_file)
        out_file =fname + '.mid'
    elif os.path.isdir(out_file):
        base = os.path.basename(in_file)
        fname, _ = os.path.splitext(base)
        out_file = os.path.join(out_file, fname + '.mid')

    # Make the MIDI file.
    make_midi(in_file, out_file, args.name)
    # Play MIDI file or make wav file if requested.
    midi_play.play(out_file, args)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create MIDI file',
                                     epilog='The positional arguments can also be "help [option]"')
    parser.add_argument('input', nargs='?', default='', help=f'Data to create MIDI file')
    parser.add_argument('output', nargs='?', default='', help=f'Output file or folder (defaults to input filename & location)')
    parser.add_argument('-n', '--name', default='', help='use the named composition or opus from the input file')
    parser.add_argument('-p', '--play', nargs='?', const='bare', default='none', help='play the generated midi file [with program]')
    parser.add_argument('-s', '--sf2', help='sound file to use')
    parser.add_argument('-w', '--wav', action="store_true", default=False, help='create a wav file')
    parser.add_argument('-l', '--log', default=default_log_level, help='logging level')
    parser.add_argument('-v', '--version', action="store_true", help='version')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=get_logging_level(args))

    try:
        if args.input == '':
            parser.print_help()
        else:
            run(args)
    except Exception as e:
        print(e)
