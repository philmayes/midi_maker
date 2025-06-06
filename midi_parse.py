import os

from midi_percussion import percussion as p
from midi_voices import voices as v

volume = {
    'arpeggio': 60,
    'bass': 100,
    'chord': 60,
    'lead': 120,
    'percussion': 60,
    'default': 100,
}
# voice Channel.bass v.electric_bass_picked volume_bass

class Commands:
    def __init__(self, in_dir: str, in_file: str):
        path = os.path.join(in_dir, in_file)
        with open(path, "r") as input_file:
            self.commands = input_file.readlines()



    def get_voices(self):
        for command in self.commands:
            words = command.split()
            if words[0] == 'voice':
                if words[2] not in v:
                    print(f'Bad voice in {command}')
                    continue
                if words[2] not in v:
                    print(f'Bad voice in {command}')
                    continue
                if words[3] not in volume:
                    print(f'Bad volume in {command}')
                    continue

