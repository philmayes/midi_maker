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
from collections import namedtuple
import os
import random
import subprocess

from midiutil import MIDIFile

from midi_channels import Channel
from midi_chords import chord_to_intervals, chord_to_pitches
from midi_items import *
import midi_parse
from midi_percussion import percussion as p
from midi_voice import Voice
from midi_voices import voices as v

in_dir = "E:\\tmp"
out_dir = "E:\\tmp"
in_file = "phil.txt"
out_file = "phil.mid"
player = "E:\\devtools\\FluidSynth\\bin\\fluidsynth.exe"
sound_file = "E:\\devtools\\MIDISoundFiles\\FluidR3 GM.sf2"

#             C  D  E  F  G  A  B
major_ints = [0, 2, 4, 5, 7, 9, 11,]
#             A  B  C  D  E  F  G
minor_ints = [0, 2, 3, 5, 7, 8, 10,]

# note durations
demisemiquaver = 120    # thirtysecond note
semiquaver = 2 * demisemiquaver # sixteenth note
quaver = 2 * semiquaver # eighth note
crotchet = 2 * quaver   # quarter note
minim = 2 * crotchet    # half note
semibreve = 2 * minim   # whole note
breve = 2 * semibreve   # double whole note
# triplets
t_demisemiquaver = demisemiquaver // 3
t_semiquaver = 2 * t_demisemiquaver
t_quaver = 2 * t_semiquaver
t_crotchet = 2 * t_quaver
t_minim = 2 * t_crotchet
t_semibreve = 2 * t_minim
t_breve = 2 * t_semibreve
# doublets, i.e. 2 x triplets, so triplet + doublet = note
d_demisemiquaver = 2 * t_demisemiquaver
d_semiquaver = 2 * d_demisemiquaver
d_quaver = 2 * d_semiquaver
d_crotchet = 2 * d_quaver
d_minim = 2 * d_crotchet
d_semibreve = 2 * d_minim
d_breve = 2 * d_semibreve

tempo = 120   # In BPM
# volumes are 0-127, as per the MIDI standard
volume_arpeggio = 60
volume_bass = 100
volume_chord = 60
volume_lead = 120
volume_percussion = 60
volume_default = 100

# Type aliases
Notes = list[str]
Pitches = list[int]
Rhythm = list[int]

# Rhythms represent the timing of events within a bar.
# Negative values represent a silence.
# A zero value extends the event to the end of the bar.
rhythms: dict[str, Rhythm] = {
    'rhythm1': [-crotchet, quaver, quaver, crotchet, quaver, quaver,],
    'rhythm2': [t_quaver, d_quaver, quaver, crotchet, quaver, quaver, crotchet,],
    'rhythm3': [0,],
    'rhythm4': [crotchet, crotchet, crotchet, crotchet,],
    'rhythm5': [d_crotchet, t_crotchet, d_crotchet, t_crotchet, d_crotchet, t_crotchet, crotchet,],
}
# Durations are lists from which to pick a random duration.
# Used by make_improv_bar().
durations1 = [minim, crotchet, quaver, -quaver]
durations2 = [minim, crotchet, quaver, quaver, quaver, quaver, quaver, quaver, -quaver]

# Voices are created by midi_parse from a configuration file.
voices: dict[Channel, Voice] = {}

Note = namedtuple('Note', 'pitch time duration volume',
                  defaults=(40, 0, crotchet, volume_default))

def add_start_error(value: int) -> int:
    err = value + random.choice(start_error)
    return max(err, 0)

def make_arpeggio_bar(midi_file: MIDIFile,
                    voice: Voice,
                    timesig: TimeSig,
                    bar: Bar,
                    start: int):
    bar_end = start + timesig.ticks_per_bar
    duration = crotchet
    for pitch in chord_to_pitches(bar.chord, 4):
        if start >= bar_end:
            break
        midi_file.addNote(0,
                          voice.channel,
                          pitch,
                          add_start_error(start),
                          duration,
                          voice.volume)
        start += duration

def make_bass_bar(midi_file: MIDIFile,
                  voice: Voice,
                  rhythm: Rhythm,
                  timesig: TimeSig,
                  bar: Bar,
                  start: int):
    bar_end = start + timesig.ticks_per_bar
    pitch = chord_to_pitches(bar.chord, 3)[0]
    for note_length in rhythm:
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
        # print(f'Bass {pitch} = {notes.int_to_note(pitch % 12):2} for chord {bar.chord}, duration {note_length}')
        midi_file.addNote(0,
                          voice.channel,
                          pitch,
                          add_start_error(start),
                          note_length,
                          voice.volume)
        start += note_length

def make_chord(midi_file: MIDIFile,
                    voice: Voice,
                    pitches: Pitches,
                    start: int,
                    duration: int):
    start = add_start_error(start)
    for pitch in pitches:
        midi_file.addNote(0,
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
        for n in range(-err, err + 1):
            table.append(n)
    amount //= 2
    if amount > 0:
        table.extend(make_error_table(amount))
    return table

def make_improv_bar(midi_file: MIDIFile,
                    voice: Voice,
                    timesig: TimeSig,
                    bar: Bar,
                    bar_start: int):
    bar_end = bar_start + timesig.ticks_per_bar
    # If the last note in the previous bar extended beyond the bar,
    # start at that point.
    start = bar_start + voice.overlap
    voice.overlap = 0

    # Get the chord, tonic and scale
    chord: list[int] = chord_to_intervals(bar.chord)
    tonic_pitch = chord[0]
    intervals = minor_ints if 'min' in bar.chord else major_ints
    # Construct a dozen octaves of the pitches in this scale.
    # Some of these pitches will be outside the MIDI spec of 0-127,
    # but they will be corralled by voice.constrain_pitch().
    pitches: list[int] = []
    for octave in range(-1, 11):
        pitches.extend([octave * 12 + tonic_pitch + i for i in intervals])

    while start < bar_end:
        # Choose a pitch.
        if voice.prev_pitch >= 0 and voice.prev_pitch in pitches:
            # find where the previous note was in the scale
            index = pitches.index(voice.prev_pitch)
        else:
            # This error message also fires for the initial prev_pitch == -1
            # print(f'{voice.prev_pitch} not in {pitches}')
            index = tonic_pitch + 36
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
            if bar.clip:
                # Don't allow notes to extend beyond the bar.
                duration = remaining
            else:
                # Make a note for the next bar
                voice.overlap = duration - remaining
        # print(f'Playing {pitch} = {notes.int_to_note(pitch % 12):2} for chord {bar.chord} = {chord}, duration {duration}')
        midi_file.addNote(0,
                          voice.channel,
                          pitch,
                          add_start_error(start),
                          duration,
                          voice.volume)
        start += duration

def make_percussion_bar(midi_file: MIDIFile,
                        rhythm: Rhythm,
                        volume: int,
                        instrument: int,
                        timesig: TimeSig,
                        bar_start: int):
    bar_end = bar_start + timesig.ticks_per_bar
    start = bar_start
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
        midi_file.addNote(0,
                          Channel.percussion,
                          instrument, # for percussion channel, pitch == instrument
                          add_start_error(start),
                          note_length,
                          volume)
        start += note_length

def make_rhythm_bar(midi_file: MIDIFile,
                        voice: Voice,
                        rhythm: Rhythm,
                        duration: int,
                        timesig: TimeSig,
                        bar: Bar,
                        bar_start: int):
    bar_end = bar_start + timesig.ticks_per_bar
    start = bar_start
    pitches = chord_to_pitches(bar.chord, 4)
    for note_length in rhythm:
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
        make_chord(midi_file,
                    voice,
                    pitches,
                    start,
                    play_time,
                    )
        start += note_length

def run() -> None:
    commands = midi_parse.Commands(in_dir, in_file)
    voices = commands.get_voices()
    random.seed(1)
    global start_error
    start_error = make_error_table(10)
    global error7
    error7 = make_error_table(7)
    midi_file = MIDIFile(len(voices),
                         ticks_per_quarternote=crotchet,
                         eventtime_is_ticks=True)
    midi_file.addTempo(0, 0, tempo)

    for channel, voice in voices.items():
        assert voice.channel == channel, 'Voice index must match channel'
        midi_file.addProgramChange(0, voice.channel, 0, voice.voice)

    composition = commands.get_composition('one')
    bar_start = 0
    loop_stack: list[LoopItem] = []
    timesig = TimeSig(4, 4) # default
    # Array to indicate which channels and percussions are active (playing).
    # These are changed via the classes Mute and Play.
    # The first 16 are real channels; the rest are percussion tracks.
    active: list[bool] = [False] * Channel.max_channels
    # Array to hold percussion volumes. The first 16 are unused.
    volume: list[int] = [volume_percussion] * Channel.max_channels
    item_number = 0
    while item_number < len(composition.items):
        item = composition.items[item_number]
        if isinstance(item, TimeSig):
            timesig = item
        elif isinstance(item, Tempo):
            midi_file.addTempo(0, bar_start, item.tempo)
        elif isinstance(item, Bar):
            for _ in range(item.repeat):
                # print(item.chord)
                if active[Channel.perc0]:
                    make_percussion_bar(midi_file, rhythms['rhythm1'], volume[Channel.perc0], p['high_tom'], timesig, bar_start)
                if active[Channel.perc1]:
                    make_percussion_bar(midi_file, rhythms['rhythm2'], volume[Channel.perc1], p['cowbell'], timesig, bar_start)
                if active[Channel.perc2]:
                    make_percussion_bar(midi_file, rhythms['rhythm3'], volume[Channel.perc2], p['acoustic_bass_drum'], timesig, bar_start)
                if active[Channel.bass]:
                    make_bass_bar(midi_file, voices[Channel.bass], rhythms['rhythm3'], timesig, item, bar_start)
                if active[Channel.rhythm]:
                    make_rhythm_bar(midi_file, voices[Channel.rhythm], rhythms['rhythm4'], 200, timesig, item, bar_start)
                if active[Channel.arpeggio]:
                    make_arpeggio_bar(midi_file, voices[Channel.arpeggio], timesig, item, bar_start)
                if active[Channel.lead1]:
                    make_improv_bar(midi_file, voices[Channel.lead2], timesig, item, bar_start)
                bar_start += timesig.ticks_per_bar

        elif isinstance(item, Loop):
                # This is the beginning of a loop. Save the location
                # and mark the loop as not started.
                loop_stack.append(LoopItem(item_number, -1))

        elif isinstance(item, Repeat):
            if not loop_stack:
                print('Loop stack underflow')
            else:
                loop_item: LoopItem = loop_stack[-1]
                if loop_item.count == 0:
                    loop_stack.pop()
                    # print('repeat done')
                else:
                    if loop_item.count < 0:
                        # We're looping for the 1st time
                        loop_item.count = item.repeat
                    # print(f'repeating {loop_item.count}')
                    loop_item.count -= 1
                    item_number = loop_item.item_no

        elif isinstance(item, Mute):
            for channel in item.channels:
                if channel is not Channel.none:
                    assert 0 <= channel < Channel.max_channels
                    active[channel] = False

        elif isinstance(item, Play):
            for channel in item.channels:
                if channel is not Channel.none:
                    assert 0 <= channel < Channel.max_channels
                    active[channel] = True

        elif isinstance(item, Volume):
            for channel in item.channels:
                if channel is not Channel.none:
                    assert 0 <= channel < Channel.max_channels
                    if channel < 16:
                        # The volume for channels is held in the Voice instance.
                        assert channel < len(voices)
                        new_volume = voices[channel].volume + item.delta
                        assert 0 <= new_volume <= 127
                        voices[channel].volume = new_volume
                    else:
                        # The volume for percussion tracks is held in volumes[].
                        new_volume = volume[channel] + item.delta
                        assert 0 <= new_volume <= 127
                        volume[channel] = new_volume
        else:
            assert 0, f'Unrecognized item {item}'
        item_number += 1

    path = os.path.join(out_dir, out_file)
    with open(path, "wb") as output_file:
        midi_file.writeFile(output_file)

    subprocess.run([player, '-n', '-i', sound_file, path])

if __name__=='__main__':
    run()
