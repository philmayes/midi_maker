# Midi Maker
## Overview
`midi_maker` interprets a text file (by convention using a .ini extension) and generates a midi file from it with the same filename in the same directory.
### Syntax
The text file syntax is a list of commands with the format: `command param1=value1 param2=value2,value3...`. Values are case-sensitive. 
By convention, a parameter name is plural when it can take multiple values separated by commas.
Comments start with`;`.

Commands fall into two categories: definitions and performance.
Some command names like `volume` or `rhythm` are used twice; e.g. to define a rhythm, and to perform a rhythm. They are distinguished by the syntax. 

## Definition Commands
These create the building blocks of a composition.
With the exception of `preferences`, all definition commands all have a `name=xxxxx` parameter, and this name is used by the performance commands.
They can occur in any order.

### voice
Format: `voice name=vname style=perc voice=high_tom`

The `voice` command is used to specify both instruments and percussion.
* `name` is arbitrary.
* `style` is how the voice performs. It is one of 
  - `perc` A percussion voice
  - `rhythm` Plays entire chord
  - `bass` Plays tonic
  - `arpeggio` Plays chord as arpeggio. Can take extra parameter `rate=q`.
  - `improv` Improvises based on the chord. Can take extra parameters `min_pitch=# max_pitch=#`.
  - `lead` Plays a supplied note list
* `voice` is the [General MIDI](https://en.wikipedia.org/wiki/General_MIDI) name. If the style is `perc`, the voice should be a percussion name. You can find all names with`midi_maker.py help voices` or `midi_maker help percussion` or by looking in `midi_voices.py` and `midi_percussion.py`.\
The voice can also be supplied as an integer. **NOTE** that it should be 0-based, not 1-based.

Voice encompasses both midi voices and midi percussion. 
Each voice is assigned to a separate MIDI channel. There can be a maximum of 15 voices
and an additional 10 `perc`[ussion] styles.

### volume
Format: `volume name=vname level=#`

### chord
Format: `chord name=cname notes=C,E,G,Bb`

midi_maker recognizes major, minor, augmented, diminished, 7th and 9th chord names,
but you may want to make your own, e.g `chord name=sus4 notes=C,F,G`. The notes are taken to apply to the key of C.

### rhythm
This can take either of two formats:

* Format 1: `rhythm name=rname durations=d1,d2,d3,...`
* Format 2: `rhythm name=rname seed=integer silence=float repeat=float durations=d1,d2,d3...`

Rhythms are of two sorts: for format 1, durations are a list of note durations or integers. Integers are a duration in ticks. 960 ticks = a quarter note. The durations can be negative to indicate a rest. For example, `q.,q.,q` is a calypso rhythm; `-q,q,-q,q` is an offbeat rhythm.

Format 2 generates a random rhythm using:
* `seed`: different seed values produce different rhythms.
* `silence`: a decimal number less than 1; it is the chance of generating silence rather than a note.
* `repeat`: a decimal number less than 1; the chance of repeating the previous note.
* `durations`: a list of durations from which to pick. Each duration is followed by an integer probability, e.g. `q4,h1` means a quarter note is 4 times more likely than a half note.

Use these rhythms in compositions with `rhythm voice=vname rhythms=rname1,rname2...`

### tune
Format: `tune name=tname notes=note1,note2...`

Use tunes with the `play' command.

### preferences
Format: `preferences improv_repeat=probability rhythm_repeat=probability rhythm_silence=probability default_volume=# ticks_per_beat=#`

Adjust various settings. Probability is a decimal number less than 1.0.


## Performance Commands
These generate the actual MIDI output using the definitions that have been created.

### bar
Format: `bar chords=chord1,chord2...`

### mute
The voices created with the `voice` command are initially all audible. Turn one or more voices off with `mute voices=vname1,vname2...`. Turn all voices off with `mute voices=all`.The inverse of `mute` is `hear`. 

### hear
If voices have been previously muted, turn one or more on with `hear voices=voice1,voice2...`. Turn all voices on with `hear voices=all`.

### volume
Format: `volume voices=vname1,vname2,... level=# delta=# rate=#`

Change the volume level of one or more voices. Use `level` to set an absolute level
or `delta` to make a change. (`level` takes precedence over `delta'.)
Use `rate` to make the change happen over a period of time.
For example, `rate=2` will change the volume level by 2 per beat.

### play
Format: `play voice=vname tunes=tune1,tune2... transcribe=#`

Play one or more `tunes` with the specified `voice`. If `transcribe` is supplied, raise or lower the notes by that number of semitones.

### rhythm
Format: `voice=vname rhythms=rhythm1,rhythm2...`

If the voice style is percussion, bass or rhythm, it will use the rhythm supplied and repeat it for each bar. If multiple rhythms are supplied, they will be used in turn, one per bar. When all rhythms have been played, the first one is used again.

### composition
Format: `composition name=cname`

You can have one or more compositions in a file. By naming the composition on the command line, only that composition will be played.

### opus
Format: `opus name=oname parts=cname1,cname2...`

### tempo
Format: `tempo bpm=#` supplies the number of beats per minute.

### timesig
Format: `timesig value=3/4` or any other time signature.

## Data Formats
These describe the format of the values supplied to commands.

### note durations

| duration | 1/3 duration | 2/3 duration | abbreviations |
| -------- | ------------ | ------------ | ------------- |
| thirtysecondth | t_thirtysecondth | d_thirtysecondth | t, tt, dt |
| sixteenth | t_sixteenth | d_sixteenth | s, ts, ds |
| eighth | t_eighth | d_eighth | e, te, de |
| quarter | t_quarter | d_quarter | q, tq, dq |
| half | t_half | d_half | h, th, dh |
| note | t_note | d_note | n, tn dn |
| doublenote | t_doublenote | d_doublenote | d, td, dd |

### notes
Format: `duration note octave`.
* `duration` is an abbreviation such as `q` for quarter (a quarter note). It can be dotted to make it 50% longer. A duration can be assembled from multiple parts, e.g. `q.+n` is 5½ beats.
* `note` is A-G with possible # or b e.g. `Eb`.
* `octave` is 1-10.

When supplying multiple notes, the duration and octave can be omitted if they match the previous note. e.g. a scale of G is `qG5,A,B,C6,D,E,F#,G`. Note that the `C` must be declared in octave 6, otherwise the C below G5 will play.

For example, `q.F#4` will play a dotted quarter note F# in the 4th octave.

### chords
Format: `[duration] key chord`.

The chord can be one of `maj`,`min`,`m`,`dim`,`aug`,`maj7`,`min7`,`dom7`,`dim7`,`maj6`,`min6`,`maj9`,`min9`. `m` is a sysnomym for `min`, a minor chord. If the chord is omitted. `maj` is assumed.

Some examples: `Eb`: Eb major; `Am`: A minor; `qF#maj7`: F# major 7th played for a quarter note; `h.Gaug`: G augmented for 3 beats.
