import os
import re
from typing import TypeAlias

from midi_channels import Channel
from midi_items import *
from midi_percussion import percussion as p
from midi_voice import Voice
import midi_voices

Verb: TypeAlias = str
Param: TypeAlias = list[str]
Params: TypeAlias = list[Param]
Command: TypeAlias = tuple[Verb, Params]

re_text = re.compile('[a-zA-Z_]')

volumes = {
    'arpeggio': 60,
    'bass': 100,
    'chord': 60,
    'lead': 120,
    'percussion': 60,
    'default': 100,
}

def clean_line(line: str) -> str:
    # Remove possible comment
    c = line.find('#')
    if c >= 0:
        line = line[:c]
    # Remove leading & trailing whitespace
    line = line.strip()
    return line

def get_channels(params: Params) -> list[Channel]:
    """Returns a list of all the channels suppied in params."""
    return [str_to_channel(kv[1]) for kv in params if kv[0] == 'channel']

def get_number(text: str) -> int | None:
    """Returns possibly signed number as int or None."""
    assert text != ''
    neg = False
    if not text.isdigit():
        neg = text == '-'
        text = text[1:]
    if text.isdigit():
        delta = int(text)
        if neg:
            delta = -delta
        return delta

def get_parameter(text: str, prefix: str) -> str:
    if not text.startswith(prefix):
        return ''
    text = text[len(prefix):]
    if is_text(text):
        return text
    return ''

def is_text(text: str) -> bool:
    return re_text.match(text) is not None

def parse_command(command: str) -> Command:
    command = clean_line(command)
    item: Verb = ''
    params: Params = []
    if not command:
        return item, params
    words = command.split()

    # parse parameters into the default values
    for index, word in enumerate(words):
        if index == 0:
            # First word is the command aka Item
            if word.isalpha():
                item = word
            else:
                print(f'Bad verb in {command}')
                break
        else:
            if '=' not in word:
                # Subsequent words should be of the form key=value
                print(f'Missing "=" in {command}')
                break
            key, value = word.split('=', 1)
            if not value:
                print(f'Missing value in {command}')
                break
            params.append([key, value])
    else:
        # Weird python syntax: the loop finished without a break
        return item, params
    return '', []

def str_to_channel(name: str) -> Channel:
    """Returns the Channel described by the string."""
    for ch in Channel:
        if ch.name == name:
            return ch
    return Channel.none

class Commands:
    def __init__(self, in_dir: str, in_file: str):
        path = os.path.join(in_dir, in_file)
        with open(path, "r") as input_file:
            self.commands = input_file.readlines()

    def get_voices(self) -> dict[Channel, Voice]:
        """Constructs Voice() instances from the list of commands."""
        voices: dict[Channel, Voice] = {}
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
                    channel = str_to_channel(value)

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
            voices[channel] = Voice(channel, voice, volume, min_pitch, max_pitch)
        return voices

    def get_composition(self, name: str) -> Composition:
        composition: Composition = Composition()
        in_composition = False
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]
            if not item:
                continue

            if item == 'composition':
                if in_composition:
                    break
                if params:
                    key, value = params[0]
                    if key == 'name' and value == name:
                        in_composition = True
                continue

            if not in_composition:
                continue

            if item == 'tempo':
                if params:
                    key, value = params[0]
                    if key == 'bpm':
                        if value.isdigit():
                            composition += Tempo(int(value))
                            continue
                print(f'Bad tempo in {command}')

            elif item == 'play':
                channels = get_channels(params)
                composition += Play(channels)

            elif item == 'bar':
                if params:
                    key, value = params[0]
                    if key == 'key':
                        composition += Bar(value)

            elif item == 'volume':
                if params:
                    key, value = params[0]
                    if key == 'delta':
                        delta = get_number(value)
                        if delta is not None:
                            channels = get_channels(params)
                            composition += Volume(delta, channels)

            elif item == 'loop':
                composition += Loop()
                pass
            elif item == 'mute':
                channels = get_channels(params)
                composition += Mute(channels)

            elif item == 'repeat':
                composition += Repeat()

        return composition
