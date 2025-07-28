"""Play the MIDI file or create a .wav file."""

""" Command line information for supporting programs:
    https://www.mankier.com/1/fluidsynth
    https://wiki.videolan.org/VLC_command-line_help
"""
import argparse
import logging
import os
import subprocess
import sys

from preferences import prefs

# Shortcuts for the -p parameter
known_programs = ('fluidsynth', 'vlc', 'wmplayer')

if sys.platform == 'win32':
    players = [
        r"E:\devtools\FluidSynth\bin\fluidsynth.exe",
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe",
    ]
    soundfont1 = r"E:\devtools\MIDISoundFiles\FluidR3 GM.sf2"
elif sys.platform == 'darwin':
    players = [
        '/opt/homebrew/bin/fluidsynth',
        '/Applications/VLC.app',
    ]
    soundfont1 = "/Users/philmayes/Library/Audio/Sounds/Banks/FluidR3 GM.sf2"
else:   # 'linux'
    players = [
        '/usr/bin/fluidsynth',
    ]
    soundfont1 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

def space_quote(filename: str) -> str:
    """If filename contains spaces, ensure it is quoted."""
    if not filename.startswith('"'):
        if ' ' in filename:
            filename = f'"{filename}"'
    return filename

def get_player(args:argparse.Namespace) -> str:
    """Get the program that will play a midi file or create a wav file."""
    if args.play not in ('none', 'bare'):
        # The program name has been supplied
        if os.path.exists(args.play):
            return space_quote(args.play)
        # If the program name alone has been supplied,
        # see if we know its location.
        lower = args.play.lower()
        if lower in known_programs:
            for player in players:
                if lower in player.lower() and os.path.exists(player):
                    return player
        logging.warning(f'program "{args.play}" does not exist')
    # Look through all the programs we know about.
    for player in players:
        if os.path.exists(player):
            return player
    return ''

def get_soundfont(args:argparse.Namespace) -> str:
    if args.sf2:
        if os.path.exists(args.sf2):
            return args.sf2
        logging.warning(f'sound file "{args.sf2}" does not exist')
    if os.path.exists(soundfont1):
        return soundfont1
    return ''

def play(midi_file: str, args:argparse.Namespace) -> None:
    """Plays a midi file or creates a wav file.

    The args.play command line argument has the values:
        none:   no argument was supplied
        bare:   -p          was supplied
        file:   -p program  was supplied
    It interacts with the -w argument as follows:
    | -p   | -w | program | output |
    +------+----+---------+--------+
    | none |    | none    | none   |
    |  "   | -w | builtin | wav    |
    | bare |    | builtin | audio  |
    |  "   | -w | builtin | wav    |
    | file |    | file    | audio  |
    |  "   | -w | file    | wav    |
"""
    if args.play == 'none' and args.wav == False:
        return

    # Make the output filename absolute, as some programs are stupid.
    midi_file = space_quote(os.path.abspath(midi_file))
    # Make the name of the wav file in case it is needed.
    wav_file = space_quote(midi_file.replace('.mid', '.wav'))

    # Find the program to use.
    program = get_player(args)
    if not program:
        if args.wav:
            logging.warning(f'Cannot find program to play midi file')
        else:
            logging.warning(f'Cannot find program to make wav file')
        return

    params: list[str] = []
    params.append(program)
    lowercase_program = program.lower()
    if 'fluidsynth' in lowercase_program:
        sf2 = get_soundfont(args)
        if not sf2:
            logging.warning(f'Cannot find soundfont')
            return

        # Construct the command line for fluidsynth.
        params.append('-n') # Don't create driver to read MIDI input events
        params.append('-i') # Don't read commands from the shell
        # params.append('-v') # Print out verbose messages about midi events
        # params.append('-d') # Dump incoming and outgoing MIDI events to stdout
        params.append('-q') # Do not print welcome message etc
        # Inject the reverb values supplied in preferences.
        for opt in [
            f'synth.reverb.damp={prefs.reverb_damp}',
            f'synth.reverb.level={prefs.reverb_level}',
            f'synth.reverb.room-size={prefs.reverb_roomsize}',
            f'synth.reverb.width={prefs.reverb_width}',
            ]:
            params.append('-o')
            params.append(opt)
        if args.wav:
            params.append('-F')     # Render MIDI file to audio and store in:
            params.append(wav_file) # ...this file
            params.append('-T')     # ...as format:
            params.append('wav')    # ...audio file type
        params.append(sf2)
        params.append(midi_file)
        subprocess.run(params)

    elif 'vlc' in lowercase_program:
        sf2 = get_soundfont(args)
        params.append('-I')     # Run VLC in...
        params.append('dummy')  # ...headless mode
        params.append(midi_file)
        if sf2:
            # This may not be necessary; a soundfont file can be preset in VLC.
            # On Linux, this parameter is not recognized.
            params.append('--soundfont')
            params.append(sf2)
        if args.wav:
            params.append('--sout')
            param = ''.join(['#transcode{acodec=s16l,channels=2}:std{access=file,mux=wav,dst=',
                             wav_file,
                             '}'])
            params.append(param)
        params.append('vlc://quit')
        subprocess.run(params)

    else:
        subprocess.run([program, midi_file])
