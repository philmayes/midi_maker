import logging
import re

from midi_channels import Channel, is_midi, str_to_channel
from midi_items import *
from midi_notes import *
import midi_percussion
from midi_voice import Voice
from midi_types import *
import midi_voices
from midi_volumes import volumes
import utils

re_text = re.compile('[a-zA-Z_]')

def clean_line(line: str) -> str:
    # Remove possible comment
    c = line.find(';')
    if c >= 0:
        line = line[:c]
    # Remove leading & trailing whitespace
    return line.strip()

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
                logging.warning(f'Bad verb in {command}')
                break
        else:
            if '=' not in word:
                # Subsequent words should be of the form key=value
                logging.warning(f'Missing "=" in {command}')
                break
            key, value = word.split('=', 1)
            if not value:
                logging.warning(f'Missing value in {command}')
                break
            params.append([key, value])
    else:
        # Weird python syntax: the loop finished without a break
        return item, params
    return '', []

class Commands:
    def __init__(self, in_file: str):
        with open(in_file, "r") as f_in:
            self.commands = f_in.readlines()
        self.channel_names = self.get_channel_names()

    def get_channel_names(self) -> list[str]:
        """Gets a list of all channel names that are in use."""
        names: list[str] = []
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]
            if item == 'voice':
                for param in params:
                    key, value = param
                    if key == 'channel':
                        names.append(value)
        return names

    def get_channels(self, params: Params) -> list[Channel]:
        """Returns a list of all the channels supplied in params."""
        channels: list[Channel] = []
        for kv in params:
            if kv[0] == 'channel':
                name = kv[1]
                if name in self.channel_names:
                    channels.append(str_to_channel(name))
                else:
                    logging.error(f'Channel {name} does not exist')
        return channels

    def get_composition(self, name: str='') -> Composition:
        """Gets the list of items between."""
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
                if not name:
                    in_composition = True
                elif params:
                    key, value = params[0]
                    if key == 'name' and value == name:
                        in_composition = True
                continue

            if not in_composition:
                continue

            elif item == 'bar':
                if params:
                    key, value = params[0]
                    if key == 'key':
                        composition += Bar(value)

            elif item == 'beat':
                if params:
                    key, value = params[0]
                    if key == 'name':
                        channels = self.get_channels(params)
                        composition += Beat(value, channels)

            elif item == 'loop':
                composition += Loop()
                pass
            elif item == 'mute':
                channels = self.get_channels(params)
                composition += Mute(channels)

            elif item == 'play':
                channels = self.get_channels(params)
                composition += Play(channels)

            elif item == 'repeat':
                composition += Repeat()

            elif item == 'tempo':
                if params:
                    key, value = params[0]
                    if key == 'bpm':
                        if value.isdigit():
                            composition += Tempo(int(value))
                            continue
                logging.warning(f'Bad tempo in {command}')

            elif item == 'volume':
                channels = self.get_channels(params)
                if channels:
                    vol = Volume(0, 0, 0, channels)
                    for param in params:
                        # No need to range-check here;
                        # it is done by ChannelInfo.set_volume
                        key, value = param
                        if key == 'delta':
                            number = utils.get_signed_number(value)
                            if number is not None:
                                vol.delta = number
                        if key == 'abs':
                            if value.isdigit():
                                vol.abs = int(value)
                        if key == 'rate':
                            if value.isdigit():
                                vol.rate = int(value)
                    if vol.delta or vol.abs:
                        composition += vol

        return composition

    def get_opus(self, name: str) -> str:
        """Gets parts of the named opus."""
        names: list[str] = []
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]
            if not item:
                continue

            if item == 'opus':
                found = False
                parts = ''
                for param in params:
                    key, value = param
                    if key == 'name' and value == name:
                        found = True
                    elif key == 'parts':
                        parts = value
                if found:
                    return parts
        return ''

    def get_rhythms(self) -> Rhythms:
        """Constructs Voice() instances from the list of commands."""
        rhythms: Rhythms = {}
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]

            if item == 'rhythm':
                name: str = ''
                values: str = ''
                rhythm: Rhythm = []
                for param in params:
                    if param[0] == 'name':
                        name = param[1]
                    elif param[0] == 'values':
                        values = param[1]

                if name and values:
                    notes = values.split(',')
                    for note in notes:
                        duration: int = str_to_note(note)
                        # TODO: error handling?
                        rhythm.append(duration)
                    rhythms[name] = rhythm

        return rhythms

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
                    logging.warning(f'Missing "=" in {command}')
                    continue
                key, value = word.split('=', 1)
                if not value:
                    logging.warning(f'Missing value in {command}')
                    continue

                if key == 'channel':
                    channel = str_to_channel(value)

                elif key == 'min_pitch':
                    if not value.isdigit() or not 0 <= int(value) <= 127:
                        logging.warning(f'Bad min_pitch in {command}')
                        continue
                    min_pitch = int(value)

                elif key == 'max_pitch':
                    if not value.isdigit() or not 0 <= int(value) <= 127:
                        logging.warning(f'Bad max_pitch in {command}')
                        continue
                    max_pitch = int(value)

                elif key == 'voice':
                    if channel == Channel.none:
                        logging.warning(f'Channel must precede voice in "{command}"')
                        continue
                    table: dict[str, int] = midi_voices.voices\
                        if is_midi(channel)\
                        else midi_percussion.percussion
                    if value not in table:
                        logging.warning(f'Bad voice in {command}')
                        continue
                    voice = table[value]

                elif key == 'volume':
                    if value in volumes:
                        volume = volumes[value]
                    elif value.isdigit():
                        volume = utils.make_in_range(int(value), 128, 'Voice volume')
                    else:
                        logging.warning(f'Bad volume in {command}')

            if channel == Channel.none:
                logging.warning(f'No channel in {command}')
                continue
            voices[channel] = Voice(channel, voice, volume, min_pitch, max_pitch)
        return voices

    def get_works(self, name: str) -> list[str]:
        """Gets a list of all opuses or compositions."""
        names: list[str] = []
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]
            if not item:
                continue

            if item == name:
                if params:
                    key, value = params[0]
                    if key == 'name':
                        names.append(value)
        return names
