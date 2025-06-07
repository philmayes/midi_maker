import os
import re

from midi_channels import Channel
from midi_percussion import percussion as p
from midi_voice import Voice
import midi_voices

re_text = re.compile('[a-zA-Z_]')

volumes = {
    'arpeggio': 60,
    'bass': 100,
    'chord': 60,
    'lead': 120,
    'percussion': 60,
    'default': 100,
}

def get_parameter(text: str, prefix: str) -> str:
    if not text.startswith(prefix):
        return ''
    text = text[len(prefix):]
    if is_text(text):
        return text
    return ''

def is_text(text: str) -> bool:
    return re_text.match(text) is not None

def clean_line(line: str) -> str:
    # Remove possible comment
    c = line.find('#')
    if c >= 0:
        line = line[:c]
    # Remove leading & trailing whitespace
    line = line.strip()
    return line

class Commands:
    def __init__(self, in_dir: str, in_file: str):
        path = os.path.join(in_dir, in_file)
        with open(path, "r") as input_file:
            self.commands = input_file.readlines()

    def get_voices(self) -> list[Voice]:
        voices: list[Voice] = []
        for command in self.commands:
            command = clean_line(command)
            if not command:
                continue
            words = command.split()
            if words[0] != 'voice':
                continue

            # Set up default values
            channel: Channel = Channel.none
            voice: int = 0
            volume: int = 0
            min_pitch = 0
            max_pitch = 127

            # parse parameters into the default values
            for word in words[1:]:
                if '=' not in word:
                    print(f'Missing "=" in {command}')
                    continue
                key, value = word.split('=', 1)
                if not value:
                    print(f'Missing value in {command}')
                    continue

                if key == 'channel':
                    for ch in Channel:
                        if ch.name == value:
                            channel = ch
                            break
                    else:
                        continue

                elif key == 'voice':
                    if value not in midi_voices.voices:
                        print(f'Bad voice in {command}')
                        continue
                    voice = midi_voices.voices[value]

                elif key == 'volume':
                    if value not in volumes:
                        print(f'Bad volume in {command}')
                        continue
                    volume = volumes[value]

                elif key == 'min_pitch':
                    if not value.isdigit() or not 0 <= int(value) <= 127:
                        print(f'Bad min_pitch in {command}')
                        continue
                    min_pitch = int(value)

                elif key == 'max_pitch':
                    if not value.isdigit() or not 0 <= int(value) <= 127:
                        print(f'Bad max_pitch in {command}')
                        continue
                    max_pitch = int(value)

            if channel == Channel.none:
                print(f'No channel in {command}')
                continue
            voices.append(Voice(channel, voice, volume, min_pitch, max_pitch))
        return voices

# in_dir = "E:\\tmp"
# in_file = "phil.txt"
# commands = Commands(in_dir, in_file)
# commands.get_voices()

