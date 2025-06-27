"""Parse the input file."""
import logging
import re

from midi_channels import Channel, is_midi, str_to_channel
import midi_chords
import midi_items as mi
import midi_notes as mn
import midi_percussion
import midi_types as mt
import midi_voice
import midi_voices
import midi_volume as mv
from preferences import prefs
import rando
import utils

re_rhythm = re.compile(r'([a-z]+)(-?[\d]+)')
re_text = re.compile('[a-zA-Z_]')
re_timesig = re.compile(r'(\d+)/(\d+)$')

def clean_line(line: str) -> str:
    max_len = 250
    if len(line) > max_len:
        logging.error(f'Line starting "{line[:16]}..." is longer than ({max_len} chars)')
        return ''
    # Remove possible comment
    c = line.find(';')
    if c >= 0:
        line = line[:c]
    # Remove leading & trailing whitespace
    return line.strip()

def get_float(cmds: mt.CmdDict, param: str, min_val: float, max_val: float, default: float|str) -> float:
    value = cmds.get(param, str(default))
    result = utils.get_float(value, min_val, max_val)
    if result is None:
        return 0.0
    return result

def get_int(cmds: mt.CmdDict, param: str, default: int|str) -> int:
    value = cmds.get(param, str(default))
    if value.isnumeric():
        return int(value)
    return int(default)

def get_signed_int(cmds: mt.CmdDict, param: str, default: int|str) -> int:
    """Return possibly signed number as int."""
    value: str = cmds.get(param, str(default))
    if not value:
        logging.error(f'Bad signed number {value}')
        return int(default)
    number = utils.get_signed_int(value)
    if number is None:
        logging.error(f'Bad signed number {value}')
        return int(default)
    return number

def is_text(text: str) -> bool:
    return re_text.match(text) is not None

def parse_command(command: str) -> mt.Cmd:
    """Parse command into verb and params."""
    item: mt.Verb = ''
    params: mt.Params = []
    assert command, 'Empty command'
    words = command.split()

    # parse parameters into the default values
    for index, word in enumerate(words):
        if index == 0:
            # First word is the command aka Item
            if word.isalpha():
                item = word
            else:
                logging.warning(f'Bad verb in "{command}"')
                break
        else:
            if '=' not in word:
                # Subsequent words should be of the form key=value
                logging.warning(f'Missing "=" in "{command}"')
                break
            key, value = word.split('=', 1)
            if not value:
                logging.warning(f'Missing value in "{command}"')
                break
            params.append([key, value])
    else:
        # Weird python syntax: the loop finished without a break
        return item, params
    return '', []

def parse_command_dict(command: str) -> mt.CmdDict:
    """Parse command into dictionary."""
    result: mt.CmdDict = {'command': ''}
    assert command, 'Empty command'
    words = command.split()

    # parse parameters into the default values
    for index, word in enumerate(words):
        if index == 0:
            # First word is the command aka Item
            if word.isalpha():
                result['command'] = word
            else:
                logging.warning(f'Bad verb in "{command}"')
                break
        else:
            if '=' not in word:
                # Subsequent words should be of the form key=value
                logging.warning(f'Missing "=" in "{command}"')
                break
            key, value = word.split('=', 1)
            if not value:
                logging.warning(f'Missing value in "{command}"')
                break
            # params.append([key, value])
            result[key] = value
    return result

class Commands:
    """Class that parses the .ini file."""
    def __init__(self, lines: list[str]):
        # Remove leading & trailing whitespace and comments,
        # and validate the command.
        # Assemble command_list and command_dict for future use.
        self.commands: list[str] = []
        self.command_list: list[mt.Cmd] = [] # currently unused
        self.command_dicts: list[mt.CmdDict] = []
        for line in lines:
            clean: str = clean_line(line)
            if not clean:
                continue
            command: mt.Cmd = parse_command(clean)
            if not command[0]:
                logging.error(f'Bad command "{clean}"')
                continue
            self.commands.append(clean)
            self.command_list.append(command)
            self.command_dicts.append(parse_command_dict(clean))

        self.get_preferences()
        self.volumes = self.get_all_volumes()
        self.voices: list[mi.Voice] = self.get_all_voices()
        self.tunes = self.get_all_tunes()
        self.rhythms = self.get_all_rhythms()
        self.get_all_chords()

    def get_composition(self, name: str='') -> mi.Composition:
        """Get the list of items between named composition & the next one.
        
        However, if no name is supplied, return all items. This is done so
        that a beginner does not have to deal with composition syntax.
        """
        composition: mi.Composition = mi.Composition()
        is_named: bool = name != ''
        in_composition = not is_named
        for command in self.commands:
            cmd = parse_command(command)
            item: mt.Verb = cmd[0]
            params: mt.Params = cmd[1]
            assert item, 'Empty item'

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
                        chords: list[mt.BarChord] = []
                        tick = 0
                        for chord in value.split(','):
                            match = midi_chords.re_dur_chord.match(chord)
                            if match:
                                dur = match.group(1)
                                key = match.group(2)
                                cho = match.group(3)
                                mod = match.group(4)
                                dur2 = mn.NoteDuration.default
                                if not cho:
                                    cho = 'maj'
                                cho = cho + mod
                                if not cho in midi_chords.chords:
                                    logging.error(f'Bad chord {chord}')
                                    break
                                chords.append(mt.BarChord(tick, key, cho))
                                tick += dur2
                            else:
                                logging.error(f'Bad bar chord "{chord}"')
                        if chords:
                            composition += mi.Bar(chords)

            elif item == 'rhythm':
                # syntax: rhythm voice=vvv rhythms=r1,r2,...
                voice: mi.Voice | None = None
                rhythms: mt.Rhythms = []
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
                    composition += mi.Beat(voice, rhythms)

            elif item == 'hear':
                voices = self.get_voices(params)
                composition += mi.Hear(voices)

            elif item == 'loop':
                composition += mi.Loop()
                pass
            elif item == 'mute':
                voices = self.get_voices(params)
                composition += mi.Mute(voices)

            elif item == 'play':
                voice: mi.Voice | None = None
                tunes: mt.Tunes = []
                trans: int | None = 0
                for param in params:
                    key, value = param
                    if key == 'voice':
                        voice = self.get_voice(value)
                    elif key == 'tunes':
                        tunes = self.get_tunes(value)
                    elif key == 'transcribe':
                        trans = utils.get_signed_int(value)
                if tunes and voice and trans is not None:
                    composition += mi.Play(voice, tunes, trans)
                else:
                    logging.warning(f'Bad play command: "{command}"')

            elif item == 'repeat':
                composition += mi.Repeat()

            elif item == 'tempo':
                if params:
                    key, value = params[0]
                    if key == 'bpm':
                        if value.isdigit():
                            composition += mi.Tempo(int(value))
                            continue
                logging.warning(f'Bad tempo in "{command}"')

            elif item == 'timesig':
                if params:
                    key, value = params[0]
                    if key == 'value':
                        match = re_timesig.match(value)
                        if match:
                            top = int(match.group(1))
                            bottom = int(match.group(2))
                            if bottom.bit_count() == 1:
                                composition += mi.TimeSig(top, bottom)
                                continue
                logging.warning(f'Bad timesig in "{command}"')

            elif item == 'volume':
                voices = self.get_voices(params)
                if voices:
                    vol = mi.Volume(0, 0, 0, voices)
                    for param in params:
                        # No need to range-check here;
                        # it is done by ChannelInfo.set_volume
                        key, value = param
                        if key == 'delta':
                            number = utils.get_signed_int(value)
                            if number is not None:
                                vol.delta = number
                        if key == 'level':
                            if value.isdigit():
                                vol.level = int(value)
                        if key == 'rate':
                            if value.isdigit():
                                vol.rate = int(value)
                    if vol.delta or vol.level:
                        if vol.delta and vol.level:
                            logging.warning(f'Cannot specify both level and delta in "{command}"')
                            vol.delta = 0
                        composition += vol

        return composition

    def get_opus(self, name: str) -> str:
        """Get parts of the named opus."""
        names: list[str] = []
        for command in self.commands:
            cmd = parse_command(command)
            item: mt.Verb = cmd[0]
            params: mt.Params = cmd[1]
            assert item, 'Empty item'

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

    def get_all_chords(self):
        """Read and set up non-standard chords."""
        for command in self.commands:
            cmds: mt.CmdDict = parse_command_dict(command)
            if cmds['command'] == 'chord':
                name: str = cmds.get('name', '')
                notes = cmds.get('notes', '')
                if name and notes:
                    offsets: list[int] = []
                    last_value = -1
                    for note in notes.split(','):
                        if note in mn.note_to_interval:
                            offset = mn.note_to_interval[note]
                            while offset <= last_value:
                                offset += 12
                            offsets.append(offset)
                            last_value = offset
                        else:
                            logging.error(f'Bad note in chord "{command}"')
                            break
                    midi_chords.chords[name] = offsets
                else:
                    logging.error(f'Bad format for command "{command}"')

    def get_all_rhythms(self) -> mt.RhythmDict:
        """Construct Rhythm dictionary from the list of commands."""
        rhythms: mt.RhythmDict = {}
        for command in self.commands:
            cmds: mt.CmdDict = parse_command_dict(command)
            if cmds['command'] == 'rhythm':
                rhythm: mt.Rhythm = []
                name: str = cmds.get('name', '')
                seed = get_signed_int(cmds, 'seed', -1)
                silence = get_float(cmds, 'silence', 0.0, 1.0, prefs.rhythm_silence)
                repeat = get_float(cmds, 'repeat', 0.0, 1.0, prefs.rhythm_repeat)
                durations = cmds.get('durations', '')
                if name and seed >= 0:
                    random = rando.Rando(int(seed))
                    # Construct a table of possible durations
                    probs: list[int] = []
                    bits = durations.split(',')
                    for bit in bits:
                        match = re_rhythm.match(bit)
                        if match:
                            dur = mn.str_to_duration(match.group(1))
                            for _ in range(int(match.group(2))):
                                probs.append(dur)
                        else:
                            logging.debug(f'Bad note {bit} in rhythm')
                    # Build a rhythm. We don't know how long the bar is,
                    # could be 4/4, 7/4, etc., so construct for 8/4.
                    tick = 0
                    end = mn.NoteDuration.doublenote
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
                elif name and durations:
                    total = 0
                    for note in durations.split(','):
                        duration: int = mn.str_to_duration(note)
                        # TODO: error handling?
                        rhythm.append(duration)
                        total += abs(duration)
                    rhythms[name] = rhythm
                    logging.debug(f'rhythm named {name} has duration {total} ticks = {total/mn.NoteDuration.quarter} beats')
                elif name:
                    logging.error(f'Bad rhythm command "{command}"')
                else:
                    # This is a composition rhythm command. We are too lazy
                    # to check that it actually live within a composition.
                    pass
        return rhythms

    def get_all_tunes(self) -> mt.TuneDict:
        """Construct Tune dictionary from the list of commands."""
        tunes: mt.TuneDict = {}
        for command in self.commands:
            cmd = parse_command(command)
            item: mt.Verb = cmd[0]
            params: mt.Params = cmd[1]

            if item == 'tune':
                name: str = ''
                notes: str = ''
                tune: mt.Tune = []
                for param in params:
                    if param[0] == 'name':
                        name = param[1]
                    elif param[0] == 'notes':
                        notes = param[1]

                if name and notes:
                    tune = mn.str_to_notes(notes)
                    if name in tunes:
                        logging.error(f'Tune "{name}" already used')
                    else:
                        tunes[name] = tune
                        total = sum(note.duration for note in tune)
                        logging.debug(f'Tune {name} has duration {total:5}')

        return tunes

    def get_all_voices(self) -> list[mi.Voice]:
        """Construct Voice() instances from the list of commands."""
        voices: list[mi.Voice] = []
        next_voice_channel = 1
        next_perc_channel = 1
        for cmd in self.command_dicts:
            if cmd['command'] != 'voice':
                continue
            # Create a simulacrum of the command for use in error messages.
            command = ' '.join(f'{k}={v}' for k,v in cmd.items() if k != 'command')
            command = 'voice ' + command

            # Set up default values
            name: str = ''
            channel: Channel = Channel.none
            voice: int = 0
            style: str = ''
            min_pitch: int = 0
            max_pitch: int = 127
            rate: int = mn.NoteDuration.quarter

            if 'name' in cmd:
                name = cmd['name']

            if 'min_pitch' in cmd:
                value = utils.get_int(cmd['min_pitch'])
                if value is None:
                    logging.warning(f'Bad min_pitch in "{command}"')
                else:
                    min_pitch = value

            if 'max_pitch' in cmd:
                value = utils.get_int(cmd['max_pitch'])
                if value is None:
                    logging.warning(f'Bad max_pitch in "{command}"')
                else:
                    if value < min_pitch:
                        logging.warning(f'max_pitch less than min_pitch in "{command}"')
                        min_pitch = 0
                    else:
                        max_pitch = value

            if 'rate' in cmd:
                value = cmd['rate']
                rate: int = mn.str_to_duration(value)

            if 'style' in cmd:
                value = cmd['style']
                if value in midi_voice.Voice.styles:
                    style = value
                else:
                    style = 'bass'
                    logging.warning(f'Bad style in "{command}", using {style}')

            if 'voice' in cmd:
                value = cmd['voice']
                if style == 'perc':
                    if value in midi_percussion.percussion:
                        voice = midi_percussion.percussion[value]
                    elif value.isdigit():
                        voice = int(value)
                        if not 35 <= voice <= 81:
                            logging.warning(f'voice {voice} is not a valid percussion number')
                            continue
                    else:
                        logging.warning(f'Bad voice in "{command}"')
                        continue
                    if next_perc_channel >= 10:
                        logging.warning(f'Too many percussion channels')
                        continue
                    channel = str_to_channel(f'perc{next_perc_channel}')
                    next_perc_channel += 1
                else:
                    assert style
                    if value in midi_voices.voices:
                        voice = midi_voices.voices[value]
                    elif value.isdigit():
                        voice = int(value)
                        if not 0 <= voice < 128:
                            logging.warning(f'voice {voice} is not a valid voice number')
                            continue
                    else:
                        logging.warning(f'Bad voice in "{command}"')
                        continue
                    if next_voice_channel >= 16:
                        logging.warning(f'Too many voice channels')
                        continue
                    channel = str_to_channel(f'ch{next_voice_channel}')
                    next_voice_channel += 1

            if channel == Channel.none:
                logging.warning(f'No channel in "{command}"')
                continue
            voices.append(mi.Voice(name, channel, voice, style, min_pitch, max_pitch, rate))
            mv.set_volume(channel, 0, self.volumes[style], 0, 0)
        return voices

    def get_all_volumes(self):
        """Get a dictionary of all volume names and values."""
        volumes: dict[str, int] = {'default': prefs.default_volume}
        # prime the volumes with defaults
        for name, level in midi_voice.Voice.styles.items():
            volumes[name] = level
        for cmd in self.command_dicts:
            if cmd['command'] == 'volume':
                if 'name' in cmd and 'level' in cmd:
                    name = cmd['name']
                    level = cmd['level']
                    if level.isdigit():
                        volumes[name] = utils.make_in_range(int(level), 128, 'volume name')
                    else:
                        logging.error(f'volume name level "{level}" is invalid')
        return volumes

    def get_preferences(self) -> None:
        """Get changes to global preferences."""
        prefs_dict = prefs.__dict__
        for command in self.commands:
            item, params = parse_command(command)
            if item == 'preferences':
                for key, value in params:
                    if key in prefs_dict:
                        pref_type = type(prefs_dict[key])
                        if pref_type == float:
                            result = utils.get_float(value, 1.0)
                            if result is None:
                                logging.warning(f'Preference out of range: "{key}={value}"')
                            else:
                                prefs_dict[key] = value
                        elif pref_type == int:
                            result = utils.get_int(value)
                            if result is None:
                                logging.warning(f'Preference is not a number: "{key}={value}"')
                            else:
                                prefs_dict[key] = value
                        else:
                            logging.error(f'Preference type {pref_type} not handled')
                    else:
                        logging.warning(f'Unknown preference: "{key}={value}"')

    def get_rhythms(self, value: str) -> mt.Rhythms:
        """Return a list of all the rhythms supplied in param."""
        rhythms: mt.Rhythms = []
        rhythm_names = value.split(',')
        for rhythm_name in rhythm_names:
            if rhythm_name in self.rhythms:
                rhythms.append(self.rhythms[rhythm_name])
            else:
                logging.error(f'rhythm {rhythm_name} does not exist')
        return rhythms

    def get_tunes(self, value: str) -> mt.Tunes:
        """Return a list of all the tunes supplied in param."""
        tunes: mt.Tunes = []
        tune_names = value.split(',')
        for tune_name in tune_names:
            if tune_name in self.tunes:
                tunes.append(self.tunes[tune_name])
            else:
                logging.error(f'tune {tune_name} does not exist')
        return tunes

    def get_voice(self, name: str) -> mi.Voice | None:
        """Return the named voice."""
        for voice in self.voices:
            if voice.name == name:
                return voice
        else:
            logging.error(f'Voice {name} does not exist')

    def get_voices(self, params: mt.Params) -> list[mi.Voice]:
        """Return a list of all the voices supplied in params."""
        voices: list[mi.Voice] = []
        for kv in params:
            if kv[0] == 'voices':
                voice_names = kv[1].split(',')
                if 'all' in voice_names:
                    return self.voices
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

    def get_works(self, name: str) -> list[str]:
        """Get a list of all opuses or compositions."""
        names: list[str] = []
        for command in self.commands:
            cmd = parse_command(command)
            item: mt.Verb = cmd[0]
            params: mt.Params = cmd[1]
            assert item, 'Empty item'

            if item == name:
                if params:
                    key, value = params[0]
                    if key == 'name':
                        names.append(value)
        return names
