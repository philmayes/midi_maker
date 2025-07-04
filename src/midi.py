"""This module generates a .mid file from a text description.

See README.md for details."""

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
note    = whole note
half    = half    (1/2) note
quarter = quarter (1/4) note ♩
eighth  = eighth  (1/8) note ♪
See midi_notes.Duration for full list.
Time signature:
The bottom number tells what sort of notes each bar is going to contain,
The top one tells how many of them there will be (or equivalent).
e.g. for 6/8, each bar contains 6 eighth notes
"""
import logging
import random

from midiutil import MIDIFile

from midi_channels import Channel
from midi_chords import chord_to_pitches
import midi_items as mi
from midi_notes import Duration as n, note_to_interval
import midi_parse
import midi_types as mt
from midi_voice import Voice, Voices
import midi_volume as mv
from preferences import prefs
import utils

#             C  D  E  F  G  A  B
major_ints = [0, 2, 4, 5, 7, 9, 11,]
#             A  B  C  D  E  F  G
minor_ints = [0, 2, 3, 5, 7, 8, 10,]

default_tempo = 120   # In BPM

# Rhythms represent the timing of events within a bar.
# Negative values represent a silence.
# A zero value extends the event to the end of the bar.
rhythms: dict[str, mt.Rhythm] = {}

# Durations are lists from which to pick a random duration.
# Used by make_improv_bar().
durations1 = [n.half, n.quarter, n.eighth, -n.eighth]
durations2 = [n.half, n.quarter, n.eighth, n.eighth, n.eighth, n.eighth, n.eighth, n.eighth, -n.eighth]

class BarInfo:
    """Class that holds info for the current bar."""
    def __init__(self, midi_file: MIDIFile):
        self.midi_file = midi_file
        self.timesig: mi.TimeSig = mi.TimeSig(4, 4)
        self.bar: mi.Bar = mi.Bar([])
        self.start = 0
        self.position = 0

    def adjust_note_time(self, voice: Voice, duration: int) -> int:
        """Adjust how much time the note takes in the bar."""
        remaining = self.bar_end() - self.position
        # A negative note length is a silence; the called should handle it.
        assert duration >= 0, 'adjust_note_time does not handle neg duration'
        if duration == 0:
            # A zero note length extends note to the end of the bar.
            # extend note to end of bar
            return remaining

        clip = self.clip(voice)
        if clip:
            # Don't allow notes to extend beyond the bar.
            if duration > remaining:
                duration = remaining
        return duration

    def adjust_play_time(self, voice: Voice, duration: int) -> int:
        """Adjust how much time the note plays for."""
        remaining = self.bar_end() - self.position
        assert remaining >= 0, 'neg remaining'
        if duration == 0:
            # A zero note length extends note to the end of the bar.
            # extend note to end of bar
            return remaining

        clip = self.clip(voice)
        if clip:
            # Don't allow notes to extend beyond the bar.
            if duration > remaining:
                duration = remaining
        return duration

    def bar_end(self) -> int:
        """Returns the time at the end of the bar in ticks."""
        return self.start + self.timesig.ticks_per_bar

    def bar_ended(self) -> bool:
        """Returns TODO."""
        return self.position >= self.bar_end()

    def clip(self, voice: Voice) -> bool:
        """Return True if note should be clipped to the end of the bar."""
        return self.bar.clip and voice.clip

    def get_chord(self) -> str:
        """Returns the chord at current time within the bar."""
        return self.bar.get_chord(self.position)

    def get_tonic(self) -> str:
        """Returns the tonic at current time within the bar."""
        return self.bar.get_tonic(self.position)

    def get_tonic_offset(self) -> int:
        """Returns the tonic offset (0-11) at current time within the bar."""
        return note_to_interval[self.get_tonic()]

    def in_bar(self) -> bool:
        return not self.bar_ended()

def add_start_error(value: int) -> int:
    err = value + random.choice(start_error)
    return max(err, 0)

def get_work(commands: midi_parse.Commands, name: str) -> mi.Composition:
    """Assembles the components (compositions) of a work."""
    composition = mi.Composition()
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
    if not composition.items:
        logging.error(f'Composition "{name}" is empty or missing')
    return composition

def make_arpeggio_bar(bar_info: BarInfo, voice: Voice):
    bar_info.position = bar_info.start
    bar_end = bar_info.bar_end()
    duration = voice.rate
    old_chord = 'none'
    pitch_index: int = 0
    step: int = -1
    while bar_info.in_bar():
        new_chord = bar_info.get_chord()
        if new_chord != old_chord:
            pitches = chord_to_pitches(new_chord, 4)
            old_chord = new_chord
            pitch_index: int = 0
            step: int = -1
        volume = mv.get_volume(voice.channel, bar_info.position)
        duration = bar_info.adjust_note_time(voice, duration)
        play_time = bar_info.adjust_play_time(voice, duration)
        bar_info.midi_file.addNote(0,
                                   voice.channel,
                                   pitches[pitch_index],
                                   add_start_error(bar_info.position),
                                   play_time,
                                   volume)
        if pitch_index == 0 or pitch_index == len(pitches) - 1:
            step = -step
        pitch_index += step
        bar_info.position += duration

def make_bass_bar(bar_info: BarInfo, voice: Voice):
    bar_info.position = bar_info.start
    rhythm = voice.get_rhythm()
    for duration in rhythm:
        tonic: str = bar_info.get_tonic()
        pitch = note_to_interval[tonic] + 36
        if bar_info.bar_ended():
            break
        if duration < 0:
            # A negative note length is a silence.
            bar_info.position -= duration
            continue
        volume = mv.get_volume(voice.channel, bar_info.position)
        duration = bar_info.adjust_note_time(voice, duration)
        play_time = bar_info.adjust_play_time(voice, duration)
        bar_info.midi_file.addNote(0,
                                   voice.channel,
                                   pitch,
                                   add_start_error(bar_info.position),
                                   play_time,
                                   volume)
        bar_info.position += duration

def make_chord(bar_info: BarInfo, voice: Voice,
                    # voice: Voice,
                    pitches: mt.Pitches,
                    start: int,
                    duration: int):
    start = add_start_error(start)
    for pitch in pitches:
        volume = mv.get_volume(voice.channel, start)
        bar_info.midi_file.addNote(0,
                                   voice.channel,
                                   pitch,
                                   start,
                                   duration,
                                   volume)

def make_improv_bar(bar_info: BarInfo, voice: Voice):
    bar_end = bar_info.bar_end()
    # If the last note in the previous bar extended beyond the bar,
    # start at that point.
    bar_info.position = bar_info.start + voice.overlap
    voice.overlap = 0
    old_chord = 'none'

    while bar_info.in_bar():
        # Get the name of the chord at this point in the bar.
        new_chord = bar_info.get_chord()
        if new_chord != old_chord:
            # Get the tonic and scale
            tonic_pitch = bar_info.get_tonic_offset()
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
                for n, prev in enumerate(pitches):
                    if prev > prev_pitch:
                        index = n
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
        if voice.prev_duration and random.random() < prefs.improv_repeat:
            duration = voice.prev_duration
        else:
            duration = random.choice(durations1)
            if duration < 0:
                # A negative note length is a silence.
                bar_info.position -= duration
                continue
        voice.prev_duration = duration

        remaining = bar_end - bar_info.position
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
        volume = mv.get_volume(voice.channel, bar_info.position)
        play_time = voice.adjust_duration(duration)
        bar_info.midi_file.addNote(0,
                                   voice.channel,
                                   pitch,
                                   add_start_error(bar_info.position),
                                   play_time,
                                   volume)
        bar_info.position += duration

def make_percussion_bar(bar_info: BarInfo, voice: Voice):
    # bar_end = bar_info.bar_end()
    bar_info.position = bar_info.start
    rhythm = voice.get_rhythm()
    for duration in rhythm:
        # if bar_info.position >= bar_end:
        if bar_info.bar_ended():
            break
        if duration < 0:
            # A negative note length is a silence.
            bar_info.position -= duration
            continue
        volume = mv.get_volume(voice.channel, bar_info.position)
        duration = bar_info.adjust_note_time(voice, duration)
        play_time = bar_info.adjust_play_time(voice, duration)
        bar_info.midi_file.addNote(0,
                                   Channel.percussion,
                                   voice.voice,
                                   add_start_error(bar_info.position),
                                   play_time,
                                   volume)
        bar_info.position += duration

def make_rhythm_bar(bar_info: BarInfo, voice: Voice):
    bar_info.position = bar_info.start
    # bar_end = bar_info.bar_end()
    rhythm = voice.get_rhythm()
    for duration in rhythm:
        if bar_info.bar_ended():
            break
        if duration < 0:
            # A negative note length is a silence.
            bar_info.position -= duration
            continue
        pitches = chord_to_pitches(bar_info.get_chord(), voice.octave)
        duration = bar_info.adjust_note_time(voice, duration)
        play_time = bar_info.adjust_play_time(voice, duration)
        make_chord(bar_info,
                   voice,
                   pitches,
                   bar_info.position,
                   play_time,
                   )
        bar_info.position += duration

def make_midi(in_file: str, out_file: str, create: str):
    with open(in_file, "r") as f_in:
        lines = f_in.readlines()
    commands = midi_parse.Commands(lines)
    voices: Voices = commands.voices

    random.seed(1)
    global start_error
    start_error = utils.make_error_table(10)
    global error7
    error7 = utils.make_error_table(7)

    # MIDIFile channel count does not include percussion voices as they are
    # pseudo-channels that map to track in the percussion channel.
    midi_channel_count = len([k for k in voices if k.style != 'perc'])
    # Always request at least 1 channel, otherwise MIDIFile freaks out.
    midi_file = MIDIFile(max(midi_channel_count, 1),
                         ticks_per_quarternote=n.quarter,
                         eventtime_is_ticks=True)
    midi_file.addTempo(0, 0, default_tempo)

    # Populate channel_info with voice info and set the voice up in MIDI.
    for voice in voices:
        if voice.style != 'perc':
            midi_file.addProgramChange(0, voice.channel, 0, voice.voice)

    # Create an object to hold dynamic info about the current bar.
    bar_info: BarInfo = BarInfo(midi_file)

    # Get a composition and process all the commands in it.
    # composition = commands.get_composition(args.play)
    composition = get_work(commands, create)
    loop_stack: list[mi.LoopItem] = []
    item_number = 0
    while item_number < len(composition.items):
        item = composition.items[item_number]
        if isinstance(item, mi.Bar):
            bar_info.bar = item
            for _ in range(item.repeat):
                logging.debug(item.chords)
                for voice in voices:
                    if voice.style == 'perc' and voice.active:
                        make_percussion_bar(bar_info, voice)
                    elif voice.style == 'bass' and voice.active:
                        make_bass_bar(bar_info, voice)
                    elif voice.style == 'rhythm' and voice.active:
                        make_rhythm_bar(bar_info, voice)
                    elif voice.style == 'arpeggio' and voice.active:
                        make_arpeggio_bar(bar_info, voice)
                    elif voice.style == 'improv' and voice.active:
                        make_improv_bar(bar_info, voice)
                bar_info.start += bar_info.timesig.ticks_per_bar

        elif isinstance(item, mi.Beat):
            for voice in item.voices:
                voice.rhythms = item.rhythms

        elif isinstance(item, mi.Effects):
            for voice in item.voices:
                voice.staccato = item.staccato
                voice.overhang = item.overhang
                if item.clip is not None:
                    voice.clip = item.clip
                if item.octave is not None:
                    voice.octave = item.octave
                if item.rate is not None:
                    voice.rate = item.rate

        elif isinstance(item, mi.Hear):
            for voice in item.voices:
                if voice.channel is not Channel.none:
                    voice.active = True

        elif isinstance(item, mi.Loop):
                # This is the beginning of a loop. Save the location
                # and mark the loop as not started.
                loop_stack.append(mi.LoopItem(item_number, -1))

        elif isinstance(item, mi.Mute):
            for voice in item.voices:
                if voice.channel is not Channel.none:
                    voice.active = False

        elif isinstance(item, mi.Play):
            voice = item.voice
            if voice.active:
                position = start = bar_info.start
                for tune in item.tunes:
                    for note in tune:
                        # A pitch < 0 requests a period of silence.
                        if note.pitch >= 0:
                            pitch = utils.make_in_range(note.pitch + item.trans,
                                                        128,
                                                        'Play note')
                            volume = mv.get_volume(voice.channel, position)
                            position = start + note.start
                            midi_file.addNote(0,
                                            voice.channel,
                                            pitch,
                                            add_start_error(position),
                                            note.duration,
                                            volume)
                    # At the end of a tune, update start in case another tune
                    # is following.
                    start = position + tune[-1].duration

        elif isinstance(item, mi.Repeat):
            if not loop_stack:
                logging.warning('Loop stack underflow')
            else:
                loop_item: mi.LoopItem = loop_stack[-1]
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

        elif isinstance(item, mi.Tempo):
            midi_file.addTempo(0, bar_info.start, item.tempo)

        elif isinstance(item, mi.TimeSig):
            bar_info.timesig = item

        elif isinstance(item, mi.Volume):
            # midi_parse is responsible for ensuring the following.
            assert item.level or item.delta, 'Volume has no level or delta'
            # The volume in the voice is not set directly because it may
            # change over a period of time. Instead, mv.set_volume()
            # is called on all supplied voices and mv.get_volume() is
            # called whenever a midi note is generated.
            for voice in item.voices:
                mv.set_volume(voice.channel,
                              bar_info.start,
                              item.level,
                              item.delta,
                              item.rate)

        else:
            logging.error(f'Unrecognized item {item}')

        # After processing the item, step to the next one.
        item_number += 1

    with open(out_file, "wb") as f_out:
        midi_file.writeFile(f_out)
