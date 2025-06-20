import logging
import re

from midi_channels import Channel, is_midi, str_to_channel
import midi_chords
from midi_items import *
from midi_notes import *
import midi_percussion
from midi_types import *
import midi_voice
import midi_voices
import rando
import utils

re_float = re.compile(r'\d*\.?\d+$')
re_rhythm = re.compile(r'([a-z]+)(-?[\d]+)')
re_text = re.compile('[a-zA-Z_]')

def clean_line(line: str) -> str:
    max_len = 250
    if len(line) > max_len:
        logging.error(f'Line starting "{line[:16]}" is longer than ({max_len} chars)')
        return ''
    # Remove possible comment
    c = line.find(';')
    if c >= 0:
        line = line[:c]
    # Remove leading & trailing whitespace
    return line.strip()

def get_float(cmds: CommandDict, param: str, default: float|str) -> float:
    value = cmds.get(param, str(default))
    if re_float.match(value):
        return float(value)
    return 0.0

def get_int(cmds: CommandDict, param: str, default: int|str) -> int:
    value = cmds.get(param, str(default))
    if value.isnumeric():
        return int(value)
    return int(default)

def get_signed_int(cmds: CommandDict, param: str, default: int|str) -> int:
    """Returns possibly signed number as int."""
    value: str = cmds.get(param, str(default))
    if not value:
        logging.error(f'Bad signed number {value}')
        return int(default)
    neg = False
    if not value.isdigit():
        sign = value[0]
        value = value[1:]
        if sign == '-':
            neg = True
        elif sign != '+':
            logging.error(f'Bad signed number {value}')
            return int(default)
    if value.isdigit():
        number = int(value)
        if neg:
            number = -number
        return number
    return int(default)

def is_text(text: str) -> bool:
    return re_text.match(text) is not None

def parse_command(command: str) -> Command:
    """Parse command into verb and params."""
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

def parse_command_dict(command: str) -> CommandDict:
    """Parse command into dictionary."""
    result: CommandDict = {'command': ''}
    command = clean_line(command)
    if command:
        words = command.split()

        # parse parameters into the default values
        for index, word in enumerate(words):
            if index == 0:
                # First word is the command aka Item
                if word.isalpha():
                    result['command'] = word
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
                # params.append([key, value])
                result[key] = value
    return result

class Commands:
    """Class that parses the .ini file."""
    def __init__(self, in_file: str):
        with open(in_file, "r") as f_in:
            self.commands = f_in.readlines()
        self.volumes = self.get_volumes()
        self.voices: list[Voice] = self.get_all_voices()
        self.tunes = self.get_all_tunes()
        self.rhythms = self.get_all_rhythms()

    def get_composition(self, name: str='') -> Composition:
        """Gets the list of items between named composition & the next one.
        
        However, if no name is supplied, return all items. This is done so
        that a beginner does not have to deal with composition syntax.
        """
        composition: Composition = Composition()
        is_named: bool = name != ''
        in_composition = not is_named
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]
            if not item:
                continue

            if item == 'composition' and is_named:
                # syntax: composition name=foobar
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
                # syntax: bar key=cCmaj,qGmaj7
                if params:
                    key, value = params[0]
                    if key == 'chords':
                        chords: list[BarChord] = []
                        tick = 0
                        for chord in value.split(','):
                            match = midi_chords.re_dur_chord.match(chord)
                            if match:
                                dur = match.group(1)
                                key = match.group(2)
                                cho = match.group(3)
                                mod = match.group(4)
                                dur2 = NoteDuration.default
                                if not cho:
                                    cho = 'maj'
                                cho = cho + mod
                                if not cho in midi_chords.chords:
                                    logging.error(f'Bad chord {chord}')
                                    break
                                chords.append(BarChord(tick, key, cho))
                                tick += dur2
                            else:
                                logging.error(f'Bad bar chord "{chord}"')
                        if chords:
                            composition += Bar(chords)

            elif item == 'rhythm':
                # syntax: rhythm voice=vvv rhythms=r1,r2,...
                voice: Voice | None = None
                rhythms: Rhythms = []
                for param in params:
                    key, value = param
                    if key == 'voice':
                        voice = self.get_voice(value)
                    elif key == 'rhythms':
                        rhythms = self.get_rhythms(value)
                    elif key == 'name':
                        # Not an error, but not a good .ini layout.
                        logging.warning('Rhythm definition found within composition')
                        voice = None
                        break
                if voice and rhythms:
                    composition += Beat(voice, rhythms)

            elif item == 'hear':
                voices = self.get_voices(params)
                composition += Hear(voices)

            elif item == 'loop':
                composition += Loop()
                pass
            elif item == 'mute':
                voices = self.get_voices(params)
                composition += Mute(voices)

            elif item == 'play':
                voice: Voice | None = None
                tunes: Tunes = []
                for param in params:
                    key, value = param
                    if key == 'voice':
                        voice = self.get_voice(value)
                    elif key == 'tunes':
                        tunes = self.get_tunes(value)
                if tunes and voice:
                    composition += Play(voice, tunes)

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
                voices = self.get_voices(params)
                if voices:
                    vol = Volume(0, 0, 0, voices)
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

    def get_all_rhythms(self) -> RhythmDict:
        """Constructs Rhythm dictionary from the list of commands."""
        rhythms: RhythmDict = {}
        for command in self.commands:
            cmds: CommandDict = parse_command_dict(command)
            if cmds['command'] == 'rhythm':
                rhythm: Rhythm = []
                name: str = cmds.get('name', '')
                values = cmds.get('values', '')
                seed = get_signed_int(cmds, 'seed', -1)
                silence = get_float(cmds, 'silence', 0.5)
                repeat = get_float(cmds, 'repeat', 0.3)
                notes = cmds.get('notes', '')
                if name and values:
                    for note in values.split(','):
                        duration: int = str_to_duration(note)
                        # TODO: error handling?
                        rhythm.append(duration)
                    rhythms[name] = rhythm
                elif name and seed >= 0:
                    random = rando.Rando(int(seed))
                    # Construct a table of possible durations
                    probs: list[int] = []
                    bits = notes.split(',')
                    for bit in bits:
                        match = re_rhythm.match(bit)
                        if match:
                            dur = str_to_duration(match.group(1))
                            for _ in range(int(match.group(2))):
                                probs.append(dur)
                        else:
                            logging.debug(f'Bad note {bit} in rhythm')
                    # Build a rhythm. We don't know how long the bar is,
                    # could be 4/4, 7/4, etc., so construct for 8/4.
                    tick = 0
                    end = NoteDuration.breve
                    dur = 0
                    while tick < end:
                        if tick == 0 or not random.test(repeat):
                            index = int(len(probs) * random.number)
                            dur = probs[index]
                        if random.test(silence):
                            rhythm.append(-dur)
                        else:
                            rhythm.append(dur)
                        tick += dur
                    logging.debug(f'random rhythm {rhythm}')
                    rhythms[name] = rhythm
                elif name:
                    logging.error(f'Bad rhythm command "{command}"')
                else:
                    # This is a composition rhythm command. We are too lazy
                    # to check that it actually live within a composition.
                    pass
        return rhythms

    def get_all_tunes(self) -> TuneDict:
        """Constructs Tune dictionary from the list of commands."""
        tunes: TuneDict = {}
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]

            if item == 'tune':
                name: str = ''
                notes: str = ''
                tune: Tune = []
                for param in params:
                    if param[0] == 'name':
                        name = param[1]
                    elif param[0] == 'notes':
                        notes = param[1]

                if name and notes:
                    tune = str_to_notes(notes)
                    if name in tunes:
                        logging.error(f'Tune "{name}" already used')
                    else:
                        tunes[name] = tune

        return tunes

    def get_all_voices(self) -> list[Voice]:
        """Constructs Voice() instances from the list of commands."""
        voices: list[Voice] = []
        next_voice_channel = 1
        next_perc_channel = 1
        for command in self.commands:
            command = clean_line(command)
            if not command:
                continue
            words = command.split()
            if words[0] != 'voice':
                continue

            # Set up default values
            name: str = ''
            channel: Channel = Channel.none
            voice: int = 0
            style: str = ''
            volume: int = 0
            min_pitch: int = 0
            max_pitch: int = 127
            rate: int = NoteDuration.crotchet

            # parse parameters into the default values
            for word in words[1:]:
                if '=' not in word:
                    logging.warning(f'Missing "=" in {command}')
                    continue
                key, value = word.split('=', 1)
                if not value:
                    logging.warning(f'Missing value in {command}')
                    continue

                if key == 'name':
                    name = value

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

                elif key == 'rate':
                    rate: int = str_to_duration(value)

                elif key == 'style':
                    if value in midi_voice.Voice.styles:
                        style = value
                    else:
                        style = 'bass'
                        logging.warning(f'Bad style in {command}, using {style}')

                elif key == 'voice':
                    if value in midi_voices.voices:
                        if next_voice_channel >= 16:
                            logging.warning(f'Too many voice channels')
                            continue
                        voice = midi_voices.voices[value]
                        channel = str_to_channel(f'ch{next_voice_channel}')
                        next_voice_channel += 1
                    elif value in midi_percussion.percussion:
                        if next_perc_channel >= 10:
                            logging.warning(f'Too many percussion channels')
                            continue
                        voice = midi_percussion.percussion[value]
                        channel = str_to_channel(f'perc{next_perc_channel}')
                        next_perc_channel += 1
                    else:
                        logging.warning(f'Bad voice in {command}')
                        continue

                elif key == 'volume':
                    if value in self.volumes:
                        volume = self.volumes[value]
                    elif value.isdigit():
                        volume = utils.make_in_range(int(value), 128, 'Voice volume')
                    else:
                        logging.warning(f'Bad volume in {command}')

            if channel == Channel.none:
                logging.warning(f'No channel in {command}')
                continue
            voices.append(Voice(name, channel, voice, style, volume, min_pitch, max_pitch, rate))
        return voices

    def get_rhythms(self, value: str) -> Rhythms:
        """Returns a list of all the rhythms supplied in param."""
        rhythms: Rhythms = []
        rhythm_names = value.split(',')
        for rhythm_name in rhythm_names:
            if rhythm_name in self.rhythms:
                rhythms.append(self.rhythms[rhythm_name])
            else:
                logging.error(f'rhythm {rhythm_name} does not exist')
        return rhythms

    def get_tunes(self, value: str) -> Tunes:
        """Returns a list of all the tunes supplied in param."""
        tunes: Tunes = []
        tune_names = value.split(',')
        for tune_name in tune_names:
            if tune_name in self.tunes:
                tunes.append(self.tunes[tune_name])
            else:
                logging.error(f'tune {tune_name} does not exist')
        return tunes

    def get_voice(self, name: str) -> Voice | None:
        """Returns the named voice."""
        for voice in self.voices:
            if voice.name == name:
                return voice
        else:
            logging.error(f'Voice {name} does not exist')

    def get_voices(self, params: Params) -> list[Voice]:
        """Returns a list of all the voices supplied in params."""
        voices: list[Voice] = []
        for kv in params:
            if kv[0] == 'voices':
                voice_names = kv[1].split(',')
                for voice_name in voice_names:
                    for voice in self.voices:
                        if voice.name == voice_name:
                            if voice not in voices:
                                voices.append(voice)
                            else:
                                logging.error(f'{voice_name} repeated')
                            break
                    else:
                        logging.error(f'Voice {voice_name} does not exist')
        return voices

    def get_volumes(self):
        """Gets a dictionary of all volume names and values."""
        volumes: dict[str, int] = {'default': utils.default_volume}
        for command in self.commands:
            cmd = parse_command(command)
            item: Verb = cmd[0]
            params: Params = cmd[1]
            if item == 'volname':
                if params:
                    key, value = params[0]
                    if is_text(key) and value.isdigit():
                        volumes[key] = utils.make_in_range(int(value), 128, 'volname')
                    else:
                        logging.error(f'volname "{params[0]}" is invalid')
        return volumes

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
