import logging
import os
import subprocess

player1 = "E:\\devtools\\FluidSynth\\bin\\fluidsynth.exe"
sound_file1 = "E:\\devtools\\MIDISoundFiles\\FluidR3 GM.sf2"
player2 = "C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe"

def play(midi_file: str) -> None:
    """Looks for a possible player and plays a midi file."""
    if os.path.exists(player1) and os.path.exists(sound_file1):
        subprocess.run([player1, '-n', '-i', sound_file1, midi_file])
    elif os.path.exists(player2):
        subprocess.run([player2, midi_file])
    else:
        logging.error('Cannot find program to play midi file')
