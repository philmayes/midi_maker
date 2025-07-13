"""Play the MIDI file that has been created."""
"""
Command line: https://www.mankier.com/1/fluidsynth
"""
import logging
import os
import subprocess

from preferences import prefs

player1 = r"E:\devtools\FluidSynth\bin\fluidsynth.exe"
sound_file1 = r"E:\devtools\MIDISoundFiles\FluidR3 GM.sf2"
player2 = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"

def play(midi_file: str, wav_file: str='') -> None:
    """Plays a midi file or creates a wav file."""
    if os.path.exists(player1) and os.path.exists(sound_file1):
        # Construct the command line for fluidsynth.
        params: list[str] = []
        params.append(player1)
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
        if wav_file:
            params.append('-F') # Render MIDI file to audio and store in:
            params.append(wav_file)# this file
            params.append('-T') # ...as format:
            params.append('wav')# ...audio file type
        params.append(sound_file1)
        params.append(midi_file)
        subprocess.run(params)
    elif not wav_file and os.path.exists(player2):
        subprocess.run([player2, midi_file])
    else:
        logging.error('Cannot find program to play midi file')
