""" References
https://medium.com/@stevehiehn/how-to-generate-music-with-python-the-basics-62e8ea9b99a5
Documentation:
https://bspaans.github.io/python-mingus/
https://midiutil.readthedocs.io/en/1.2.1/
https://csound.com/get-started.html
https://en.wikipedia.org/wiki/General_MIDI
https://www.fluidsynth.org          # plays MIDI files
https://www.polyphone.io/en/home    # sf2 editor
"""
""" Music theory
semibreve= whole note
minim    = half    (1/2) note
crotchet = quarter (1/4) note ♩
quaver   = eighth  (1/8) note ♪
Time signature:
The bottom number tells what sort of notes each bar is going to contain,
The top one tells how many of them there will be (or equivalent).
e.g. for 6/8, each bar contains 6 quavers
"""
import argparse
from collections import namedtuple
import logging
import os
import random
import subprocess

from midiutil import MIDIFile

from midi_channels import Channel, is_midi
from midi_chords import chord_to_intervals, chord_to_pitches
from midi_items import *
from midi_notes import Note as n
import midi_parse
from midi_percussion import percussion as p
from midi_types import *
from midi_voice import Voice
from midi_voices import voices as v
from midi_volumes import volumes

player = "E:\\devtools\\FluidSynth\\bin\\fluidsynth.exe"
sound_file = "E:\\devtools\\MIDISoundFiles\\FluidR3 GM.sf2"
default_log_level = 'WARNING'

#             C  D  E  F  G  A  B
major_ints = [0, 2, 4, 5, 7, 9, 11,]
#             A  B  C  D  E  F  G
minor_ints = [0, 2, 3, 5, 7, 8, 10,]

tempo = 120   # In BPM

# Rhythms represent the timing of events within a bar.
# Negative values represent a silence.
# A zero value extends the event to the end of the bar.
rhythms: dict[str, Rhythm] = {}
default_rhythm = [n.crotchet, n.crotchet, n.crotchet, n.crotchet,]

# Durations are lists from which to pick a random duration.
# Used by make_improv_bar().
durations1 = [n.minim, n.crotchet, n.quaver, -n.quaver]
durations2 = [n.minim, n.crotchet, n.quaver, n.quaver, n.quaver, n.quaver, n.quaver, n.quaver, -n.quaver]

Note = namedtuple('Note', 'pitch time duration volume',
                  defaults=(40, 0, n.crotchet, volumes['default']))

class BarInfo:
    """Class that holds info for the current bar."""
    def __init__(self, midi_file: MIDIFile):
        self.midi_file = midi_file
        self.timesig: TimeSig = TimeSig(4, 4)
        self.bar: Bar = Bar('Cmaj')
        self.start = 0

    def bar_end(self) -> int:
        return self.start + self.timesig.ticks_per_bar

class ChannelInfo:
    """Holds all info for a channel (which includes percussion)
    that can be adjusted dynamically.
    """
    def __init__(self):
        self.active = False
        self.voice = Voice(Channel.none, 0, 0, 0, 0)
        self.volume = volumes['default']
        self.rhythm = default_rhythm

def add_start_error(value: int) -> int:
    err = value + random.choice(start_error)
    return max(err, 0)

def get_logging_level(args:argparse.Namespace) -> str:
    # get the logging level: can be partial word, case-insensitive
    short_level = args.log.upper()
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    for log_level in log_levels:
        if log_level.startswith(short_level):
            return log_level
    print(f"Invalid log level '{short_level}'. Defaulting to '{default_log_level}'.")
    return default_log_level

def make_arpeggio_bar(bar_info: BarInfo, channel_info: ChannelInfo):
    start = bar_info.start
    bar_end = bar_info.bar_end()
    duration = n.crotchet
    for pitch in chord_to_pitches(bar_info.bar.chord, 4):
        if start >= bar_end:
            break
        bar_info.midi_file.addNote(0,
                                   channel_info.voice.channel,
                                   pitch,
                                   add_start_error(start),
                                   duration,
                                   channel_info.volume)
        start += duration

def make_bass_bar(bar_info: BarInfo, channel_info: ChannelInfo):
    start = bar_info.start
    bar_end = bar_info.bar_end()
    pitch = chord_to_pitches(bar_info.bar.chord, 3)[0]
    for note_length in channel_info.rhythm:
        remaining = bar_end - start
        if remaining <= 0:
            break
        if note_length < 0:
            # A negative note length is a silence.
            start -= note_length
            continue
        if note_length == 0:
            # A zero note length extends note to the end of the bar.
            note_length = remaining
        # Don't allow notes to extend beyond the bar.
        if note_length > remaining:
            note_length = remaining
        # logging.debug(f'Bass {pitch} = {notes.int_to_note(pitch % 12):2} for chord {bar.chord}, duration {note_length}')
        bar_info.midi_file.addNote(0,
                                   channel_info.voice.channel,
                                   pitch,
                                   add_start_error(start),
                                   note_length,
                                   channel_info.volume)
        start += note_length

def make_chord(bar_info: BarInfo, channel_info: ChannelInfo,
                    # channel_info: ChannelInfo,
                    pitches: Pitches,
                    start: int,
                    duration: int):
    start = add_start_error(start)
    for pitch in pitches:
        bar_info.midi_file.addNote(0,
                                   channel_info.voice.channel,
                                   pitch,
                                   start,
                                   duration,
                                   channel_info.volume)

def make_error_table(amount: int) -> list[int]:
    """Makes an error table
    Maximum error == ±<amount>.
    Smaller errors are more probable.
    """
    table = []
    for err in range(amount + 1):
        for no in range(-err, err + 1):
            table.append(no)
    amount //= 2
    if amount > 0:
        table.extend(make_error_table(amount))
    return table

def make_improv_bar(bar_info: BarInfo, channel_info: ChannelInfo):
    bar_end = bar_info.bar_end()
    voice: Voice = channel_info.voice
    # If the last note in the previous bar extended beyond the bar,
    # start at that point.
    start = bar_info.start + voice.overlap
    voice.overlap = 0

    # Get the chord, tonic and scale
    chord: list[int] = chord_to_intervals(bar_info.bar.chord)
    tonic_pitch = chord[0]
    intervals = minor_ints if 'min' in bar_info.bar.chord else major_ints
    # Construct a dozen octaves of the pitches in this scale.
    # Some of these pitches will be outside the MIDI spec of 0-127,
    # but they will be corralled by voice.constrain_pitch().
    pitches: list[int] = []
    for octave in range(-1, 11):
        pitches.extend([octave * 12 + tonic_pitch + i for i in intervals])

    while start < bar_end:
        # Choose a pitch based on the previous one.
        prev_pitch = voice.prev_pitch
        if prev_pitch >= 0 and prev_pitch in pitches:
            # find where the previous note was in the scale
            index = pitches.index(prev_pitch)
        else:
            if prev_pitch == -1:
                # There is no previous note, so start on the tonic
                index = tonic_pitch + 36
            else:
                # Previous note is not in this scale, probably because of
                # chord change, so find a note near it.
                for prev in pitches:
                    if prev > prev_pitch:
                        index = prev
                        break
                else:
                    assert 0, f'prev_pitch ouside range?!'
                    index = tonic_pitch + 36
        # Pick a new pitch not far from the previous one.
        pick = random.choice(error7)
        pitch = pitches[index + pick]

        # Keep the pitch within a reasonable range.
        pitch = voice.constrain_pitch(pitch)
        voice.prev_pitch = pitch

        # Choose a duration
        if voice.prev_duration and random.random() < 0.3:
            duration = voice.prev_duration
        else:
            duration = random.choice(durations1)
            if duration < 0:
                # A negative note length is a silence.
                start -= duration
                continue
        voice.prev_duration = duration

        remaining = bar_end - start
        if duration == 0:
            # A zero note length extends note to the end of the bar.
            duration = remaining
        if duration > remaining:
            if bar_info.bar.clip:
                # Don't allow notes to extend beyond the bar.
                duration = remaining
            else:
                # Make a note for the next bar
                voice.overlap = duration - remaining
        # logging.debug(f'Playing {pitch} = {notes.int_to_note(pitch % 12):2} for chord {bar.chord} = {chord}, duration {duration}')
        bar_info.midi_file.addNote(0,
                                   channel_info.voice.channel,
                                   pitch,
                                   add_start_error(start),
                                   duration,
                                   channel_info.volume)
        start += duration

def make_in_range(value: int, max_value: int, desc: str) -> int:
    """Coerces a value into range.
    
    Valid range is 0 <= value < max_value.
    """
    if value >= max_value:
        logging.warning(f'{desc} value {value} too high')
        value = max_value - 1
    elif value < 0:
        logging.warning(f'{desc} value {value} too low')
        value = 0
    return value

def make_percussion_bar(bar_info: BarInfo, channel_info: ChannelInfo):
    bar_end = bar_info.bar_end()
    start = bar_info.start
    for note_length in channel_info.rhythm:
        if start >= bar_end:
            break
        if note_length < 0:
            # A negative note length is a silence.
            start -= note_length
            continue
        if note_length == 0:
            # A zero note length is to be extended to the end of the bar
            note_length = bar_end - start
        bar_info.midi_file.addNote(0,
                                   Channel.percussion,
                                   channel_info.voice.voice,
                                   add_start_error(start),
                                   note_length,
                                   channel_info.volume)
        start += note_length

def make_rhythm_bar(bar_info: BarInfo,
                    channel_info: ChannelInfo,
                    duration: int):
    start = bar_info.start
    bar_end = bar_info.bar_end()
    pitches = chord_to_pitches(bar_info.bar.chord, 4)
    for note_length in channel_info.rhythm:
        if start >= bar_end:
            break
        if note_length < 0:
            # A negative note length is a silence.
            start -= note_length
            continue
        if note_length == 0:
            # A zero note length is to be extended to the end of the bar.
            # Ignore any duration that has been supplied.
            note_length = bar_end - start
            duration = 0
        play_time = duration if duration else note_length
        make_chord(bar_info,
                   channel_info,
                   pitches,
                   start,
                   play_time,
                   )
        start += note_length

def run(args:argparse.Namespace):
    in_file = args.ini
    if not os.path.exists(in_file):
        logging.critical(f'Input file "{in_file}" does not exist')
        return
    fname, _ = os.path.splitext(in_file)
    out_file =fname + '.mid'
    commands = midi_parse.Commands(in_file)
    voices: dict[Channel, Voice] = commands.get_voices()
    rhythms = commands.get_rhythms()

    random.seed(1)
    global start_error
    start_error = make_error_table(10)
    global error7
    error7 = make_error_table(7)

    # MIDIFile channel count does not include percussion channels
    # they are pseudo-channels that map to track in the percussion channel.)
    midi_channel_count = len([k for k in voices.keys() if is_midi(k)])
    midi_file = MIDIFile(midi_channel_count,
                         ticks_per_quarternote=n.crotchet,
                         eventtime_is_ticks=True)
    midi_file.addTempo(0, 0, tempo)

    # Array to hold all info for a channel (which includes percussion)
    # that can be adjusted dynamically.
    channel_info: list[ChannelInfo] = []
    for _ in range(Channel.max_channels):
        channel_info.append(ChannelInfo())

    # Populate channel_info with voice info and set the voice up in MIDI.
    for channel, voice in voices.items():
        # assert voice.channel == channel, 'Voice index must match channel'
        channel_info[voice.channel].voice = voice
        channel_info[voice.channel].volume = voice.volume
        midi_file.addProgramChange(0, voice.channel, 0, voice.voice)

    # Create an object to hold dynamic info about the current bar.
    bar_info: BarInfo = BarInfo(midi_file)

    # Get a composition and process all the commands in it.
    composition = commands.get_composition(args.comp)
    loop_stack: list[LoopItem] = []
    item_number = 0
    while item_number < len(composition.items):
        item = composition.items[item_number]
        if isinstance(item, Bar):
            bar_info.bar = item
            for _ in range(item.repeat):
                logging.debug(item.chord)
                for channel in range(Channel.perc0, Channel.max_channels):
                    if channel_info[Channel.perc1].active:
                        make_percussion_bar(bar_info, channel_info[channel])
                if channel_info[Channel.bass].active:
                    make_bass_bar(bar_info, channel_info[Channel.bass])
                if channel_info[Channel.rhythm].active:
                    make_rhythm_bar(bar_info, channel_info[Channel.rhythm], 200)
                if channel_info[Channel.arpeggio].active:
                    make_arpeggio_bar(bar_info, channel_info[Channel.arpeggio])
                if channel_info[Channel.improv1].active:
                    make_improv_bar(bar_info, channel_info[Channel.improv1])
                if channel_info[Channel.improv2].active:
                    make_improv_bar(bar_info, channel_info[Channel.improv2])
                bar_info.start += bar_info.timesig.ticks_per_bar

        elif isinstance(item, Beat):
            if item.rhythm in rhythms:
                for channel in item.channels:
                    if channel is not Channel.none:
                        assert 0 <= channel < Channel.max_channels, f'Channel {channel} out of range'
                        channel_info[channel].rhythm = rhythms[item.rhythm]
            else:
                logging.warning(f'Rhythm {item.rhythm} does not exist.')

        elif isinstance(item, Loop):
                # This is the beginning of a loop. Save the location
                # and mark the loop as not started.
                loop_stack.append(LoopItem(item_number, -1))

        elif isinstance(item, Mute):
            for channel in item.channels:
                if channel is not Channel.none:
                    assert 0 <= channel < Channel.max_channels, f'Channel {channel} out of range'
                    channel_info[channel].active = False

        elif isinstance(item, Play):
            for channel in item.channels:
                if channel is not Channel.none:
                    assert 0 <= channel < Channel.max_channels, f'Channel {channel} out of range'
                    channel_info[channel].active = True

        elif isinstance(item, Repeat):
            if not loop_stack:
                logging.warning('Loop stack underflow')
            else:
                loop_item: LoopItem = loop_stack[-1]
                if loop_item.count == 0:
                    loop_stack.pop()
                    logging.debug('repeat done')
                else:
                    if loop_item.count < 0:
                        # We're looping for the 1st time
                        loop_item.count = item.repeat
                    logging.debug(f'repeating {loop_item.count}')
                    loop_item.count -= 1
                    item_number = loop_item.item_no

        elif isinstance(item, Tempo):
            midi_file.addTempo(0, bar_info.start, item.tempo)

        elif isinstance(item, TimeSig):
            bar_info.timesig = item

        elif isinstance(item, Volume):
            for channel in item.channels:
                if channel is not Channel.none:
                    assert 0 <= channel < Channel.max_channels, f'Channel {channel} out of range'
                    new_volume = channel_info[channel].volume + item.delta
                    new_volume = make_in_range(new_volume, 128, 'Volume channel')
                    channel_info[channel].volume = new_volume

        else:
            logging.error(f'Unrecognized item {item}')

        # After processing the item, step to the next one.
        item_number += 1

    with open(out_file, "wb") as f_out:
        midi_file.writeFile(f_out)

    subprocess.run([player, '-n', '-i', sound_file, out_file])

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create MIDI file')
    parser.add_argument('ini', help=f'Data to create MIDI file (default: test.ini)')
    parser.add_argument('-l', '--log', default=default_log_level, help='logging level')
    parser.add_argument('-c', '--comp', default='', help='name of composition in data file')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=get_logging_level(args))

    try:
        run(args)
    except Exception as e:
        print(e)
