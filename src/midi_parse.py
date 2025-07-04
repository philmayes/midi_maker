"""Parse the input file."""

import logging
import re

from midi_channels import Channel, str_to_channel
import midi_chords as mc
import midi_items as mi
import midi_notes as mn
import midi_percussion
import midi_types as mt
import midi_voice as mv
import midi_voices
import midi_volume
from preferences import prefs
import rando
import utils

re_rhythm = re.compile(r'([a-z]+)(-?[\d]+)')
re_text = re.compile('[a-zA-Z_]')
re_timesig = re.compile(r'(\d+)/(\d+)$')

_ln = '$line'  # Key for the original command line. Used for error reports.

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

def expect(cmd: mt.CmdDict, names: list[str]) -> None:
    """Report any unexpected parameters in command."""
    unexpected: list[str] = []
    for key in cmd.keys():
        # Ignore the command and the text line.
        if key != 'command' and key != _ln and key not in names:
            unexpected.append(key)
    if unexpected:
        logging.error(f'Bad parameter(s) "{', '.join(unexpected)}" in "{cmd[_ln]}"')
    return

def get_effect(value: str, min_val: float, max_val: float) -> int | float | None:
    """Get staccato or overhang value.

    These can be:
    * an integer that clips a note to that duration
    * a float that changes the duration by that factor
    * None if not active
    """
    result: int | float | None
    if value.isdigit():
        result = int(value)
    else:
        result = utils.get_float(value, min_val, max_val)
    return result

def get_float(cmd: mt.CmdDict, param: str, min_val: float, max_val: float, default: float|str) -> float:
    value = cmd.get(param, str(default))
    result = utils.get_float(value, min_val, max_val)
    if result is None:
        return 0.0
    return result

def get_int(cmd: mt.CmdDict,
            param: str,
            default: int|str,
            min_val: int=0,
            max_val: int=128) -> int:
    value = cmd.get(param, str(default))
    result = utils.get_int(value, min_val, max_val)
    if result is None:
        result = int(default)
    return result

def get_signed_int(cmd: mt.CmdDict, param: str, default: int|str) -> int:
    """Return possibly signed number as int."""
    value: str = cmd.get(param, str(default))
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
        # Weird python syntax: the loop finished without a break.
        # Add the original command line for use in error reports.
        params.append([_ln, command])
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
    # Add the original command line for use in error reports.
    result[_ln] = command
    return result

class Commands:
    """Class that parses the .ini file."""
    def __init__(self, lines: list[str]):
        # Remove leading & trailing whitespace and comments,
        # and validate the command.
        # Assemble a list of CmdDict instances for future use.
        self.command_dicts: list[mt.CmdDict] = []
        for line in lines:
            clean: str = clean_line(line)
            if not clean:
                continue
            command: mt.Cmd = parse_command(clean)
            if not command[0]:
                logging.error(f'Bad command "{clean}"')
                continue
            self.command_dicts.append(parse_command_dict(clean))

        self.get_preferences()
        self.volumes = self.get_all_volumes()
        self.voices: mv.Voices = self.get_all_voices()
        self.tunes = self.get_all_tunes()
        self.rhythms = self.get_all_rhythms()
        self.get_all_chords()

    def get_composition(self, name: str='') -> mi.Composition:
        """Get the list of items between named composition & the next one.
        
        However, if no name is supplied, return all items. This is done so
        that a beginner does not have to deal with composition syntax.
        """
        composition: mi.Composition = mi.Composition()
        in_composition = False
        found_composition = False
        for cmd in self.command_dicts:
            item: mt.Verb = cmd['command']
            assert item, 'Empty item'

            # Skip all definition commands. Some definition commands and
            # performance commands have the same verb (rhythm, for instance),
            # and this avoids parsing failures.
            if item != 'composition':
                if item == 'preferences':
                    continue
                if cmd.get('name'):
                    continue

            if item == 'composition':
                found_composition = True
                expect(cmd, ['name'])
                if in_composition:
                    # We've come to the end of the composition, so exit.
                    break
                if not name:
                    # If a name is not supplied, use any composition.
                    in_composition = True
                elif cmd.get('name') == name:
                    # If this composition matches the supplied name, use it.
                    in_composition = True
                continue

            if name == '' and not found_composition:
                # If no name has been supplied and there was no composition
                # command before finding performance commands (bar etc),
                # then start one.
                in_composition = True

            # Avoid adding composition commands until we are in a composition.
            if not in_composition:
                continue

            if item == 'bar':
                expect(cmd, ['chords', 'repeat', 'clip'])
                chords: list[mc.BarChord] = []
                repeat = 1
                clip = True
                if value := cmd.get('chords'):
                    tick = 0
                    for chord in value.split(','):
                        duration, bar  = mc.get_barchord(chord)
                        if duration:
                            bar.start = tick
                            chords.append(bar)
                            tick += duration
                        else:
                            logging.error(f'Bad bar chord "{chord}"')
                if value := cmd.get('repeat'):
                    repeat2 = utils.get_int(value)
                    if repeat2 is None:
                        logging.warning(f'Bad repeat in command: "{cmd[_ln]}"')
                    else:
                        repeat = repeat2
                if value := cmd.get('clip'):
                    new_clip = utils.truth(value)
                    if new_clip is not None:
                        clip = new_clip
                if chords:
                    composition += mi.Bar(chords, repeat, clip)

            elif item == 'effects':
                expect(cmd, ['voices', 'staccato', 'overhang', 'clip', 'octave', 'rate'])
                voices = self.get_voices(cmd)
                staccato: int | float | None = None
                overhang: int | float | None = None
                clip = True
                octave = None
                rate = 0
                if value := cmd.get('staccato'):
                    staccato = get_effect(value, 0.0, 1.0)
                if value := cmd.get('overhang'):
                    overhang = get_effect(value, 1.0, 8.01)
                if value := cmd.get('clip'):
                    clip = utils.truth(value)
                if value := cmd.get('octave'):
                    octave = utils.get_int(value, 0, 10)
                if value := cmd.get('rate'):
                    rate = mn.str_to_duration(value)
                if staccato and overhang:
                    logging.warning(f'Cannot use both staccato and overhang together; staccato takes preference')
                    overhang = None
                composition += mi.Effects(voices, staccato, overhang, clip, octave, rate)

            elif item == 'hear':
                expect(cmd, ['voices'])
                voices = self.get_voices(cmd)
                composition += mi.Hear(voices)

            elif item == 'loop':
                expect(cmd, [])
                composition += mi.Loop()

            elif item == 'mute':
                expect(cmd, ['voices'])
                voices = self.get_voices(cmd)
                composition += mi.Mute(voices)

            elif item == 'play':
                expect(cmd, ['voice', 'tunes', 'transpose'])
                voice: mv.Voice | None = None
                tunes: mt.Tunes = []
                trans: int | None = 0
                if value := cmd.get('voice'):
                    voice = self.get_voice(value)
                if value := cmd.get('tunes'):
                    tunes = self.get_tunes(value)
                if value := cmd.get('transpose'):
                    trans = utils.get_signed_int(value)
                if tunes and voice and trans is not None:
                    composition += mi.Play(voice, tunes, trans)
                else:
                    logging.warning(f'Bad play command: "{cmd[_ln]}"')

            elif item == 'rhythm':
                # Creates a Beat() instance, not a Rhythm() instance!
                expect(cmd, ['voices', 'rhythms'])
                voices = self.get_voices(cmd)
                rhythms: mt.Rhythms = []
                if value := cmd.get('rhythms'):
                    rhythms = self.get_rhythms(value)
                if value := cmd.get('name'):
                    # Not an error, but not a good .ini layout.
                    logging.warning('Rhythm definition found within composition')
                    continue
                if voices and rhythms:
                    composition += mi.Beat(voices, rhythms)

            elif item == 'repeat':
                expect(cmd, ['count'])
                repeat = 2
                if value := cmd.get('count'):
                    count = utils.get_int(value, 2, 100)
                    if count is not None:
                        repeat = count
                    else:
                        logging.error(f'Bad parameter in "{cmd[_ln]}"')
                composition += mi.Repeat(repeat)

            elif item == 'tempo':
                expect(cmd, ['bpm'])
                if value := cmd.get('bpm'):
                    if value.isdigit():
                        composition += mi.Tempo(int(value))
                        continue
                logging.warning(f'Bad tempo in "{cmd[_ln]}"')

            elif item == 'timesig':
                expect(cmd, ['value'])
                if value := cmd.get('value'):
                    match = re_timesig.match(value)
                    if match:
                        top = int(match.group(1))
                        bottom = int(match.group(2))
                        if bottom.bit_count() == 1:
                            composition += mi.TimeSig(top, bottom)
                            continue
                logging.warning(f'Bad timesig in "{cmd[_ln]}"')

            elif item == 'volume':
                expect(cmd, ['voices', 'level', 'rate'])
                voices = self.get_voices(cmd)
                if voices:
                    vol = mi.Volume(0, 0, 0, voices)
                    if value := cmd.get('level'):
                        # Might be a previously-defined volume name
                        if value in self.volumes:
                            vol.level = self.volumes[value]
                            continue
                        # 'level' without a sign is an absolute value;
                        # with a sign it is a delta.
                        sign = value[0]
                        if sign in '+-':
                            value = value[1:]
                        if value.isdigit():
                            level = int(value)
                            if sign == '+':
                                vol.delta = level
                            elif sign == '-':
                                vol.delta = -level
                            else:
                                vol.level = level
                        else:
                            logging.warning(f'Bad level in "{cmd[_ln]}"')
                    if value := cmd.get('rate'):
                        if value.isdigit():
                            vol.rate = int(value)
                    if vol.delta or vol.level:
                        composition += vol
                    else:
                        logging.warning(f'No level in "{cmd[_ln]}"')

        return composition

    def get_opus(self, name: str) -> str:
        """Get parts of the named opus."""
        for cmd in self.command_dicts:
            if cmd['command'] == 'opus':
                expect(cmd, ['name', 'parts'])
                name2: str = cmd.get('name', '')
                parts = cmd.get('parts', '')
                if name == name2:
                    return parts
        return ''

    def get_all_chords(self):
        """Read and set up non-standard chords."""
        for cmd in self.command_dicts:
            if cmd['command'] == 'chord':
                expect(cmd, ['name', 'notes'])
                name: str = cmd.get('name', '')
                notes = cmd.get('notes', '')
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
                            logging.error(f'Bad note in chord "{cmd[_ln]}"')
                            break
                    mc.chords[name] = offsets
                else:
                    logging.error(f'Bad format for command "{cmd[_ln]}"')

    def get_all_rhythms(self) -> mt.RhythmDict:
        """Construct Rhythm dictionary from the list of commands."""
        rhythms: mt.RhythmDict = {}
        for cmd in self.command_dicts:
            if cmd['command'] == 'rhythm':
                expect(cmd, ['name', 'voices', 'rhythms', 'seed', 'silence', 'repeat', 'durations'])
                rhythm: mt.Rhythm = mt.Rhythm()
                name: str = cmd.get('name', '')
                seed = get_signed_int(cmd, 'seed', -1)
                silence = get_float(cmd, 'silence', 0.0, 1.0, prefs.rhythm_silence)
                repeat = get_float(cmd, 'repeat', 0.0, 1.0, prefs.rhythm_repeat)
                durations = cmd.get('durations', '')
                if name and seed >= 0:
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
                    random = rando.Rando(int(seed))
                    tick = 0
                    end = mn.Duration.doublenote
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
                    rhythm = mn.str_to_durations(durations)
                    rhythms[name] = rhythm
                    total = sum(rhythm)
                    logging.debug(f'rhythm named {name} has duration {total} ticks = {total/mn.Duration.quarter} beats')
                elif name:
                    logging.error(f'Bad rhythm command "{cmd[_ln]}"')
                else:
                    # This is a composition rhythm command. We are too lazy
                    # to check that it actually lives within a composition.
                    pass
        return rhythms

    def get_all_tunes(self) -> mt.TuneDict:
        """Construct Tune dictionary from the list of commands."""
        tunes: mt.TuneDict = {}
        for cmd in self.command_dicts:
            if cmd['command'] == 'tune':
                expect(cmd, ['name', 'notes'])
                name: str = cmd.get('name', '')
                notes = cmd.get('notes', '')
                tune: mt.Tune = []

                if name and notes:
                    tune = mn.str_to_notes(notes)
                    if name in tunes:
                        logging.error(f'Tune "{name}" already used')
                    else:
                        tunes[name] = tune
                        total = sum(note.duration for note in tune)
                        logging.debug(f'Tune {name} has duration {total:5}')

        return tunes

    def get_all_voices(self) -> mv.Voices:
        """Construct Voice() instances from the list of commands."""
        voices: mv.Voices = []
        next_voice_channel = 1
        next_perc_channel = 1
        for cmd in self.command_dicts:
            if cmd['command'] != 'voice':
                continue

            expect(cmd, ['name', 'style', 'voice', 'min_pitch', 'max_pitch'])
            # Set up default values
            name: str = ''
            channel: Channel = Channel.none
            voice: int = 0
            style: str = ''
            min_pitch: int = 0
            max_pitch: int = 127

            if 'name' in cmd:
                name = cmd['name']

            if 'min_pitch' in cmd:
                value = utils.get_int(cmd['min_pitch'])
                if value is None:
                    logging.warning(f'Bad min_pitch in "{cmd[_ln]}"')
                else:
                    min_pitch = value

            if 'max_pitch' in cmd:
                value = utils.get_int(cmd['max_pitch'])
                if value is None:
                    logging.warning(f'Bad max_pitch in "{cmd[_ln]}"')
                else:
                    if value < min_pitch:
                        logging.warning(f'max_pitch less than min_pitch in "{cmd[_ln]}"')
                        min_pitch = 0
                    else:
                        max_pitch = value

            if 'style' in cmd:
                value = cmd['style']
                if value in mv.styles:
                    style = value
                else:
                    style = 'bass'
                    logging.warning(f'Bad style in "{cmd[_ln]}", using {style}')

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
                        logging.warning(f'Bad voice in "{cmd[_ln]}"')
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
                        if not 1 <= voice <= 128:
                            logging.warning(f'voice {voice} is not a valid voice number')
                            continue
                    else:
                        logging.warning(f'Bad voice in "{cmd[_ln]}"')
                        continue
                    if next_voice_channel >= 16:
                        logging.warning(f'Too many voice channels')
                        continue
                    channel = str_to_channel(f'ch{next_voice_channel}')
                    next_voice_channel += 1

            if channel == Channel.none:
                logging.warning(f'No channel in "{cmd[_ln]}"')
                continue
            voices.append(mv.Voice(name, channel, voice - 1, style, min_pitch, max_pitch))
            midi_volume.set_volume(channel, 0, self.volumes[style], 0, 0)
        return voices

    def get_all_volumes(self):
        """Get a dictionary of all volume names and values."""
        volumes: dict[str, int] = {'default': prefs.default_volume}
        # prime the volumes with defaults
        for name, level in mv.volume.items():
            volumes[name] = level
        for cmd in self.command_dicts:
            if cmd['command'] == 'volume':
                if 'name' in cmd and 'level' in cmd:
                    expect(cmd, ['name', 'level'])
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
        for cmd in self.command_dicts:
            if cmd['command'] == 'preferences':
                for key, value in cmd.items():
                    if key in ('command', _ln):
                        continue
                    if key in prefs_dict:
                        pref_type = type(prefs_dict[key])
                        if pref_type == float:
                            result = utils.get_float(value, 1.0)
                            if result is None:
                                logging.warning(f'Preference out of range: "{key}={value}"')
                            else:
                                prefs_dict[key] = result
                        elif pref_type == int:
                            result = utils.get_int(value, 0, 4000)
                            if result is None:
                                logging.warning(f'Preference is not a number: "{key}={value}"')
                            else:
                                prefs_dict[key] = result
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

    def get_voice(self, name: str) -> mv.Voice | None:
        """Return the named voice."""
        for voice in self.voices:
            if voice.name == name:
                return voice
        else:
            logging.error(f'mv.Voice {name} does not exist')

    def get_voices(self, cmd: mt.CmdDict) -> mv.Voices:
        """Return a list of all the voices supplied in cmd."""
        voices: mv.Voices = []
        if 'voices' in cmd:
            voice_names = cmd['voices'].split(',')
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
                    logging.error(f'mv.Voice {voice_name} does not exist')
        return voices
