# Midi Maker
## Overview
`midi_maker` interprets a text file (by convention using a .ini extension) and generates a midi file from it with the same filename in the same directory.
### Syntax
The text file syntax is a list of commands with the format: `command param1=value1 param2=value2...`. Values are case-sensitive. 
By convention, a param name is plural when it can take multiple values separated by commas.

Comments start with`;`.

## Definition Commands
These create the building blocks of a composition. They can occur in any order.

### voice
Format: `voice name=vname style=perc voice=high_tom volume=percussion`
* `name` is arbitrary.
* `style` is one of `perc, rhythm, bass, arpeggio, improv, lead`.
* `voice` is the General Midi name. If the style is perc, the voice should be a percussion name.
* `volume` is TODO
Each voice is assigned to a separate MIDI channel for a maximum 15 voices
and an additional 10 `perc`[ussion] styles.

### chord
Format: `chord name=cname notes=C,E,G,Bb`

midi_maker recognizes major, minor, augmented, diminished, 7th and 9th chord names,
but you may want to make your own, e.g `chord name=sus4 notes=C,F,G`. The notes are taken to apply to the key of C.

### rhythm
Format: `rhythm name=rname values=d1,d2,d3,...`

OR: `rhythm name=rname seed=integer silence=float repeat=float notes=n1,n2,n3...`
Rhythms are of two sorts: values are supplied or random using seed, silence, repeat, notes.

Use these rhythms in compositions with `rhythm voice=vname rhythms=rname1,rname2...`

### tune
Format: `tune name=tname notes=note1,note2...`

Use tunes with the `play' command.

## Performance Commands
These generate the actual MIDI output using the definitions that have been created.

### bar
Format: `bar chords=chord1,chord2...`

### hear
The voices created with the `voice` command are initially muted. Turn one or more on with `hear voices=voice1,voice2...`

### mute
The inverse of `hear` is `mute`. Turn one or more voices off with `mute voices=voice1,voice2...`

### tune
Format: `play voice=vname tunes=tune1,tune2...`

Use tune commands with 


### composition
Format: `composition name=cname`

You can have one or more compositions in a file. By naming the composition on the command line, only that composition will be played.

### opus
Format: `opus name=oname parts=cname1,cname2...`

### tempo
Format: `tempo bpm=96` or any other value for beats per minute.

### timesig
Format: `timesig value=3/4` or any other time signature.

## Data Formats
These describe the format of the values supplied to commands.

### notes
Format: `duration note octave`.
* `duration` is a note abbreviation such as `c` for crotchet (a quarter-note). It can be dotted to make it 50% longer. A duration can use multiple notes, e.g. `c.+s` is 5½ beats.
* `note` is A-G with possible # or b e.g. `eb`.
* `octave` is 1-10.
When supplying multiple notes, the duration and octave can be omitted if they match the previous note. e.g. a scale of G is `cG5,A,B,C6,D,E,F#,G`. Note that the `C` must be declared in the next octave.

### Names of notes
midi_maker uses the English names because their initial letters are (almost) unique. `semiquaver` is the exception; think of `h` as `half`.

| note name | 1/3 note | 2/3 note | abbrs |
| --------- | -------- | -------- | ----- |
| demisemiquaver | t_demisemiquaver | d_demisemiquaver | d, td, dd |
| semiquaver | t_semiquaver | d_semiquaver | h, th, dh |
| quaver | t_quaver | d_quaver | q, tq, dq |
| crotchet | t_crotchet | d_crotchet | c, tc, dc |
| minim | t_minim | d_minim | m, tm, dm |
| semibreve | t_semibreve | d_semibreve | s, ts, ds |
| breve | t_breve | d_breve | b, tb, db |
