# Midi Maker
## Overview
`midi_maker` interprets a text file (by convention using a .ini extension) and generates a midi file from it with the same filename in the same directory.
### Syntax
The text file syntax is a list of commands with the format: `command param1=value1 param2=value2,value3...`. Values are case-sensitive. 
By convention, a parameter name is plural when it can take multiple values separated by commas.
Parameter names can be abbreviated, e.g. `bar chords=C` can be `bar ch=C`.
Comments start with`;`.

Commands fall into two categories: **definitions** and **performance**.
Some command names like `volume` or `rhythm` are used twice; e.g. to define a rhythm, and to perform a rhythm. They are distinguished by the syntax. 

### Examples
There are examples of input files in the `data/` directory.

### Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install midi_maker..

```
pip install midi_maker
```

## Definition Commands
These create the building blocks of a composition.
With the exception of `preferences`, all **definition** commands all have a `name=xxxxx` parameter, and this name is used by the **performance** commands.
They can occur in any order.

### voice
Format: `voice name=vname style=perc voice=high_tom`

The `voice` command is used to specify both instruments and percussion.
* `name` is arbitrary.
* `style` is how the voice performs. It is one of 
  - `perc` A percussion voice
  - `rhythm` Plays entire chord
  - `bass` Plays tonic
  - `arpeggio` Plays chord as arpeggio.
  - `improv` Improvises based on the chord. Can take extra parameters `min_pitch=# max_pitch=#`.
  - `lead` Plays a supplied note list
* `voice` is the [General MIDI](https://en.wikipedia.org/wiki/General_MIDI) name. If the style is `perc`, the voice should be a percussion name. You can find all names with`midi_maker.py help voices` or `midi_maker help percussion` or by looking in `midi_voices.py` and `midi_percussion.py`.\
The voice can also be supplied as an integer from 1-128 (or from 35-81 for percussion).

Voice encompasses both midi voices and midi percussion. 
Each voice is assigned to a separate MIDI channel. There can be a maximum of 15 voices
and an additional 10 `perc`[ussion] styles.

### volume
Format: `volume name=vname level=#`

A volume name is an easy way of supplying volume levels by name instead of by number.
For convenience, volume names corresponding to the various styles are pre-supplied, and also the common music dynamics *ppp, pp, p, mp, mf, f, ff,* and *fff*.
You can override or add to the existing volume names+values.

### chord
Format: `chord name=cname notes=C,E,G,Bb`

midi_maker recognizes major, minor, augmented, diminished, 7th and 9th chord names.
Use `midi_maker help chords` to see what is available.
You can create your own chord with a command in the .ini file like
`chord name=pairs notes=C,D,E,F#`.
The chord is taken to be in the key of C, thus you can create an inversion with
`chord name=inv notes=E,G,C`

### rhythm
This can take either of two formats:

* Format 1: `rhythm name=rname durations=d1,d2,d3,...`
* Format 2: `rhythm name=rname seed=integer rest=float repeat=float durations=d1,d2,d3...`

Rhythms are of two sorts: for format 1, durations are a list of note durations or integers. Integers are a duration in ticks. 960 ticks = a quarter note. The durations can be negative to indicate a rest. For example, `q.,q.,q` is a calypso rhythm; `-q,q,-q,q` is an offbeat rhythm.

Format 2 generates a random rhythm using:
* `seed`: different seed values produce different rhythms.
* `rest`: a decimal number less than 1; it is the chance of generating a rest rather than a note.
* `repeat`: a decimal number less than 1; the chance of repeating the previous note.
* `durations`: a list of durations from which to pick. Each duration is followed by an integer probability, e.g. `q4,h1` means a quarter note is 4 times more likely than a half note.

Use these rhythms in compositions with `rhythm voices=vname1,vname2... rhythms=rname1,rname2...`

### tune
Format: `tune name=tname notes=note1,note2...`

A tune is a list of notes and durations (which represent rests).
See **Data Formats** for the syntax of notes. More than one note can be played at once; for example, `hD5+F#+A` would play a D major chord for two beats. (The `h` indicates a half note).
Not all those notes have to play for the same time: `hD5+qF#+nA` will play `D5` for two beats, `F#` for one beat, and `A` for four beats.

Use tunes with the `play` command. An example: `tune name=song notes=hG4,h,qA,C5` is a half note of G (4th octave), a half note of rest, two quarter notes of A and C.

### preferences
Format: `preferences improv_repeat=p rhythm_repeat=p rhythm_rest=p default_volume=# reverb_damp=p reverb_level=p reverb_roomsize=p reverb_width=%`

Adjust various settings. `p`, the probability, is a decimal number less than 1.0. `reverb_width` is 0.0-100.0.

## Performance Commands
These generate the actual MIDI output using the **definition** commands that have been created.

### bar
Format: `bar chords=chord1,chord2... repeat=# clip=false`

The chords can be preceded by a duration; if not, a quarter note is assumed. For example, `bar chords=C` is a C major bar; `bar chords=hC,Am,F` has two beats of C major, one beat of A minor and one beat of F major.

Use `repeat` to play the bar more than once. See **Discussions: Clipping** for use of the `clip` parameter.

### composition
Format: `composition name=cname`

You can have one or more compositions in a file. By naming the composition on the command line, only that composition will be played.

### effects
Format: `effects voices=v1,v2... staccato=# overhang=# clip=no octave=# rate=dur vibrato=# reverb=# chorus=#`

This turns various effects on or off for the named voices. The `staccato` value can either be the number of ticks for which the note should be played or a decimal fraction like 0.5 meaning the note will be played for half its time. Use `staccato=0` to turn it off.

`overhang` takes a number of ticks or a decimal number greater than 1.0 to cause the note to play for that much longer. It will overlap any following note. For instance, an arpeggio with a large `overhang` will progressively play a chord.

See **Discussions: Clipping** for use of the `clip` parameter.

`rate` is how quickly an arpeggio is played. It takes either a duration or a number of ticks. The default is a quarter note.

`vibrato`, `reverb` and `chorus` are self-explanatory. Additional values for `reverb` (damp, level, roomsize and width) can be set in `preferences`.

Some of the effects only apply to particular styles:

| style | clip | octave | rate | vib/rev/ch |
| :---- | :--: | :----: | :--: | :--: |
| arpeggio | Y | Y | Y | Y |
| bass     | Y | Y | - | Y |
| improv   | - | - | _ | Y |
| lead     | - | - | _ | Y |
| perc     | Y | - | - | - |
| rhythm   | Y | Y | - | Y |

### loop
Format: `loop`.

Loop marks the start of a passage that is to be played more than once, see `repeat`.
It takes no parameters.

### mute and unmute
The voices created with the `voice` command are initially all audible. Turn one or more voices off with `mute voices=vname1,vname2...`. Turn all voices off with `mute voices=all`. To hear the voices again, use `unmute voices=vname1,vname2...`.

### pan
Format: `volume voices=vname1,vname2,... position=# rate=#`

Change the left-right position of one or more voices. The position ranges from left=0 to right=127. 64 is the center. For instance, use `position=80` to set the position to 80;
`position=+20` to increase the position by 20, and `position=-10` to decrease the position by 10.
Use `rate` to make the change happen over a period of time.
For example, `rate=2` will change the position by 2 per beat.

### opus
Format: `opus name=oname parts=cname1,cname2...`

### play
Format: `play voice=vname tunes=tune1,tune2... transpose=#`

Play one or more `tunes` in turn with the specified `voice`. If `transpose` is supplied, raise or lower the notes by that number of semitones.

### repeat
Format: `repeat count=#`

Repeat a section starting at the preceding `loop` command. `count` is optional; it is the total number of times the section will be played, i.e. a bare `loop` is the same as `loop count=2`. Loops can be nested, e.g. `loop A loop B repeat C repeat` will play `A B B C A B B C`.

### rhythm
Format: `rhythm voices=vname1,vname2... rhythms=rhythm1,rhythm2...`

Note that the `rhythm` command is used both to define a rhythm (see above) and (here) to invoke it.

If the voice style is `perc`, `bass` or `rhythm`, it will use the rhythm supplied and repeat it for each bar. If multiple rhythms are supplied, they will be used in turn, one per bar. When all rhythms have been played, the first one is used again.

### skip and unskip
Format: `skip` [other commands] `unskip`.

When making changes to a composition, you may want to skip some of the playback so you only hear what you are working on. Use `skip` and `unskip` to skip over a section you do not want to hear. Voice changes etc. in the skipped section will still be honored, but any `play` command will not.

### tempo
Format: `tempo bpm=#` supplies the number of beats per minute. If omitted, the default MIDI tempo of 120 bpm is used.

### timesig
Format: `timesig value=3/4` or any other time signature.

### volume
Format: `volume voices=vname1,vname2,... level=# rate=#`

Change the volume level of one or more voices. Use `level=80` to set the level to 80;
`level=+20` to increase the level by 20, and `level=-10` to decrease the level by 10.
Use `rate` to make the change happen over a period of time.
For example, `rate=2` will change the volume level by 2 per beat.

## Data Formats
These describe the format of the notes, chords and durations that are used in commands.
This table describes where each format can be used.

| format | `tune` | `rhythm` | `bar` | `chord` |
| :---- | :-- | :---- | :-- | :-- |
| notes     | Y `+` | - | - | Y |
| chords    | Y `+` | - | Y `+` | -  |
| durations | Y      | Y | - | -  |

Y = format is used in command\
`+` = format can take an extra duration prefix and/or an @octave suffix. if no octave is supplied, uses previous octave.
<!-- d = if no duration supplied, uses previous duration -->

### durations

These are used alone in the  `tune` and `rhythm` commands, and as prefixes for notes and chords.

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
Format: `duration note @octave`.
* `duration` is one of the above abbreviations such as `q` for quarter (a quarter note). It can be dotted to make it 50% longer. A duration can be assembled from multiple parts, e.g. `q.+n` is 5½ beats; `n-q` is 3 beats.
* `note` is A-G with possible # or b e.g. `Eb`.
* `octave` is 1-10.

When supplying multiple notes, the octave can be omitted if it matches the previous note. e.g. a scale of G is `qG@5,A,B,C@6,D,E,F#,G`. Note that the `C` must be declared as being in octave 6, otherwise the C below G5 will play.
If the duration is not supplied, it will be a quarter note.

For example, `q.F#@4` will play a dotted quarter F# note in the 4th octave.

### chords
Format: `[duration] key chord [@octave]`.

The chord can be one of `maj`,`min`,`m`,`dim`,`aug`,`maj7`,`min7`,`dom7`,`dim7`,`maj6`,`min6`,`maj9`,`min9`. `m` is a synomym for `min`, a minor chord. If the chord is omitted. `maj` is assumed.
When the chord is used in a `tune`, an @`octave` suffix can be appended.

Some examples: `Eb`: Eb major; `Am`: A minor; `qF#maj7`: F# major 7th played for a quarter note; `h.Gaug`: G augmented for 3 beats.

## Discussions
### Clipping
Normally for all styles except lead, notes are clipped at the end of the bar. For instance, using `rhythm name=half durations=q,q,q,h` in a 4/4 composition will normally clip the fourth half note to a quarter note.

To inhibit this behavior and allow the note or chord to play for its full duration, use `clip=no` (can also be n, 0, f, false) with either:
* a `bar` command, which will apply to all voices for one bar
* an `effects` command, which will apply to the named voices until countermanded.

### Playing
midi_maker can play the MIDI file it has just generated. Use `-p` on the command line. You will probably need to edit `midi_play.py` for this to work on your system.

## License
TBD
