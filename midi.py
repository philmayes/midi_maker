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
See midi_notes.NoteDuration for full list.
Time signature:
The bottom number tells what sort of notes each bar is going to contain,
The top one tells how many of them there will be (or equivalent).
e.g. for 6/8, each bar contains 6 quavers
"""
import argparse
import logging
import os
import random

from midiutil import MIDIFile

from midi_channels import Channel, is_midi
from midi_chords import chord_to_intervals, chord_to_pitches
from midi_items import *
from midi_notes import NoteDuration as n, note_to_offset
import midi_parse
from midi_percussion import percussion as p
import midi_play
from midi_types import *
from midi_voice import Voice
from midi_voices import voices as v
import utils

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

# Durations are lists from which to pick a random duration.
# Used by make_improv_bar().
durations1 = [n.minim, n.crotchet, n.quaver, -n.quaver]
durations2 = [n.minim, n.crotchet, n.quaver, n.quaver, n.quaver, n.quaver, n.quaver, n.quaver, -n.quaver]

class BarInfo:
    """Class that holds info for the current bar."""
    def __init__(self, midi_file: MIDIFile):
        self.midi_file = midi_file
        self.timesig: TimeSig = TimeSig(4, 4)
        self.bar: Bar = Bar([])
        self.start = 0

    def bar_end(self) -> int:
        """Returns the time at the end of the bar in ticks."""
        return self.start + self.timesig.ticks_per_bar

    def get_chord(self, start: int) -> str:
        """Returns the chord at time <start> within the bar."""
        return self.bar.get_chord(start - self.start)

    def get_tonic(self, start: int) -> str:
        """Returns the tonic at time <start> within the bar."""
        return self.bar.get_tonic(start - self.start)

    def get_tonic_offset(self, start: int) -> int:
        """Returns the tonic offset (0-11) at time <start> within the bar."""
        return note_to_offset[self.get_tonic(start)]

def add_start_error(value: int) -> int:
    err = value + random.choice(start_error)
    return max(err, 0)

def adjust_volume(voice: Voice):
    """Is called for each bar to set volume, possibly dynamically."""
    # This cannot be made a member function of Voice because that
    # would create a circular import; midi_items uses Voice in its
    # Volume class. Same restriction applies to set_volume().
    old_vol = voice.volume
    new_vol = voice.volume_target
    delta = new_vol - old_vol
    if delta:   # Is a volume change required?
        if voice.volume_rate > 0:
            # The new volume is to be applied over time per bar.
            # Find out whether we are to increase or decrease.
            if delta > 0:
                # The volume is to be increased
                new_vol = min(old_vol + voice.volume_rate, new_vol)
            else:
                new_vol = max(old_vol - voice.volume_rate, new_vol)

        logging.debug(f'change volume channel:{voice.channel} level {voice.volume} -> {new_vol}')
        voice.volume = new_vol

def get_logging_level(args:argparse.Namespace) -> str:
    # get the logging level: can be partial word, case-insensitive
    short_level = args.log.upper()
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    for log_level in log_levels:
        if log_level.startswith(short_level):
            return log_level
    print(f"Invalid log level '{short_level}'. Defaulting to '{default_log_level}'.")
    return default_log_level

def get_work(commands: midi_parse.Commands, name: str) -> Composition:
    """Assembles the components (compositions) of a work."""
    composition = Composition()
    works = commands.get_opus(name)
    if works:
        for work in works.split(','):
            count = 1
            bits = work.split('*', 1)
            if len(bits) > 1:
                work = bits[0]
                if bits[1].isdigit():
                    count = int(bits[1])
                else:
                    logging.warning(f'Bad count in {works}')
            for _ in range(count):
                c2 = commands.get_composition(work)
                composition += c2.items
    else:
        composition = commands.get_composition(name)
    return composition

def make_arpeggio_bar(bar_info: BarInfo, voice: Voice):
    start = bar_info.start
    bar_end = bar_info.bar_end()
    duration = voice.rate
    old_chord = 'none'
    while start < bar_end:
        new_chord = bar_info.get_chord(start)
        if new_chord != old_chord:
            pitches = chord_to_pitches(new_chord, 4)
            old_chord = new_chord
            pitch_index = 0
        bar_info.midi_file.addNote(0,
                                   voice.channel,
                                   pitches[pitch_index],
                                   add_start_error(start),
                                   duration,
                                   voice.volume)
        pitch_index = (pitch_index + 1) % len(pitches)
        start += duration

def make_bass_bar(bar_info: BarInfo, voice: Voice):
    start = bar_info.start
    bar_end = bar_info.bar_end()
    rhythm = voice.get_rhythm()
    for note_length in rhythm:
        tonic: str = bar_info.get_tonic(start)
        pitch = note_to_offset[tonic] + 36
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
                                   voice.channel,
                                   pitch,
                                   add_start_error(start),
                                   note_length,
                                   voice.volume)
        start += note_length

def make_chord(bar_info: BarInfo, voice: Voice,
                    # voice: Voice,
                    pitches: Pitches,
                    start: int,
                    duration: int):
    start = add_start_error(start)
    for pitch in pitches:
        bar_info.midi_file.addNote(0,
                                   voice.channel,
                                   pitch,
                                   start,
                                   duration,
                                   voice.volume)

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

def make_improv_bar(bar_info: BarInfo, voice: Voice):
    bar_end = bar_info.bar_end()
    # If the last note in the previous bar extended beyond the bar,
    # start at that point.
    start = bar_info.start + voice.overlap
    voice.overlap = 0
    old_chord = 'none'

    while start < bar_end:
        # Get the name of the chord at this point in the bar.
        new_chord = bar_info.get_chord(start)
        if new_chord != old_chord:
            # Get the tonic and scale
            tonic_pitch = bar_info.get_tonic_offset(start)
            intervals = minor_ints if 'min' in new_chord else major_ints
            # Construct a dozen octaves of the pitches in this scale.
            # Some of these pitches will be outside the MIDI spec of 0-127,
            # but they will be corralled by voice.constrain_pitch().
            pitches: list[int] = []
            for octave in range(-1, 11):
                pitches.extend([octave * 12 + tonic_pitch + i for i in intervals])

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
                                   voice.channel,
                                   pitch,
                                   add_start_error(start),
                                   duration,
                                   voice.volume)
        start += duration

def make_percussion_bar(bar_info: BarInfo, voice: Voice):
    bar_end = bar_info.bar_end()
    start = bar_info.start
    rhythm = voice.get_rhythm()
    for note_length in rhythm:
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
                                   voice.voice,
                                   add_start_error(start),
                                   note_length,
                                   voice.volume)
        start += note_length

def make_rhythm_bar(bar_info: BarInfo,
                    voice: Voice,
                    duration: int):
    start = bar_info.start
    bar_end = bar_info.bar_end()
    rhythm = voice.get_rhythm()
    for note_length in rhythm:
        if start >= bar_end:
            break
        if note_length < 0:
            # A negative note length is a silence.
            start -= note_length
            continue
        pitches = chord_to_pitches(bar_info.get_chord(start), 4)
        if note_length == 0:
            # A zero note length is to be extended to the end of the bar.
            # Ignore any duration that has been supplied.
            note_length = bar_end - start
            duration = 0
        play_time = duration if duration else note_length
        make_chord(bar_info,
                   voice,
                   pitches,
                   start,
                   play_time,
                   )
        start += note_length

def set_volume(voice: Voice, item: Volume):
    """Adjust the volume of the voice in various ways.
    case  abs  delta   rate  set level  set rate
      1    Y     -      -     to abs       -
      2    -     Y      -     by delta     -
      3    -     Y      Y       -          Y
      4    Y     Y      Y     to abs       Y
    """
    assert item.abs or item.delta
    assert item.rate >= 0

    # First set the current volume
    old_vol = voice.volume
    if item.abs:
        new_vol = item.abs              # case 1 or 4
    elif item.delta and not item.rate:
        new_vol = old_vol + item.delta  # case 2
    else:
        new_vol = old_vol               # case 3
    new_vol = utils.make_in_range(new_vol, 128, 'Volume channel')
    voice.volume = new_vol

    # Then set up possible rate change
    if item.delta and item.rate:        # case 3 or 4
        new_vol += item.delta
        new_vol = utils.make_in_range(new_vol, 128, 'Volume channel')
        voice.volume_target = new_vol
        voice.volume_rate = item.rate

def run(args:argparse.Namespace):
    in_file = args.ini
    if not os.path.exists(in_file):
        logging.critical(f'Input file "{in_file}" does not exist')
        return
    fname, _ = os.path.splitext(in_file)
    out_file =fname + '.mid'
    commands = midi_parse.Commands(in_file)
    voices: list[Voice] = commands.voices

    random.seed(1)
    global start_error
    start_error = make_error_table(10)
    global error7
    error7 = make_error_table(7)

    # MIDIFile channel count does not include percussion voices as they are
    # pseudo-channels that map to track in the percussion channel.
    midi_channel_count = len([k for k in voices if k.style != 'perc'])
    midi_file = MIDIFile(midi_channel_count,
                         ticks_per_quarternote=n.crotchet,
                         eventtime_is_ticks=True)
    midi_file.addTempo(0, 0, tempo)

    # Populate channel_info with voice info and set the voice up in MIDI.
    for voice in voices:
        midi_file.addProgramChange(0, voice.channel, 0, voice.voice)

    # Create an object to hold dynamic info about the current bar.
    bar_info: BarInfo = BarInfo(midi_file)

    # Get a composition and process all the commands in it.
    # composition = commands.get_composition(args.play)
    composition = get_work(commands, args.create)
    loop_stack: list[LoopItem] = []
    item_number = 0
    while item_number < len(composition.items):
        item = composition.items[item_number]
        if isinstance(item, Bar):
            bar_info.bar = item
            # Handle volume changes.
            for voice in voices:
                if voice.channel != Channel.none:
                    adjust_volume(voice)
            for _ in range(item.repeat):
                logging.debug(item.chords)
                for voice in voices:
                    if voice.style == 'perc' and voice.active:
                        make_percussion_bar(bar_info, voice)
                    elif voice.style == 'bass' and voice.active:
                        make_bass_bar(bar_info, voice)
                    elif voice.style == 'rhythm' and voice.active:
                        make_rhythm_bar(bar_info, voice, 200)
                    elif voice.style == 'arpeggio' and voice.active:
                        make_arpeggio_bar(bar_info, voice)
                    elif voice.style == 'improv' and voice.active:
                        make_improv_bar(bar_info, voice)
                bar_info.start += bar_info.timesig.ticks_per_bar

        elif isinstance(item, Beat):
            if item.rhythms:
                item.voice.rhythms = item.rhythms
            else:
                logging.warning(f'Beat rhythms not supplied.')

        elif isinstance(item, Hear):
            for voice in item.voices:
                if voice.channel is not Channel.none:
                    voice.active = True

        elif isinstance(item, Loop):
                # This is the beginning of a loop. Save the location
                # and mark the loop as not started.
                loop_stack.append(LoopItem(item_number, -1))

        elif isinstance(item, Mute):
            for voice in item.voices:
                if voice.channel is not Channel.none:
                    voice.active = False

        elif isinstance(item, Play):
            start = bar_info.start
            for tune in item.tunes:
                for note in tune:
                    # A pitch < 0 requests a period of silence.
                    if note[1] >= 0:
                        midi_file.addNote(0,
                                        item.voice.channel,
                                        note[1],
                                        add_start_error(start),
                                        note[0],
                                        voice.volume)
                    start += note[0]

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
            # midi_parse is responsible for ensuring the following.
            assert item.abs or item.delta, 'Volume has no abs or delta'
            # The volume in the voice is not set directly because it may
            # change over a period of time. Instead, info.adjust_volume()
            # is called on all voices for every bar.
            for voice in item.voices:
                set_volume(voice, item)

        else:
            logging.error(f'Unrecognized item {item}')

        # After processing the item, step to the next one.
        item_number += 1

    with open(out_file, "wb") as f_out:
        midi_file.writeFile(f_out)

    if args.play:
        midi_play.play(out_file)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Create MIDI file')
    parser.add_argument('ini', nargs='?', default='example.ini', help=f'Data to create MIDI file (default: example.ini)')
    parser.add_argument('-l', '--log', default=default_log_level, help='logging level')
    parser.add_argument('-c', '--create', default='', help='create composition or opus')
    parser.add_argument('-p', '--play', action="store_true", default=False, help='play the generated midi file')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=get_logging_level(args))

    try:
        run(args)
    except Exception as e:
        print(e)
