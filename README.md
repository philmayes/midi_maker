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
* `style` is one of 
  - `perc` A percussion voice
  - `rhythm` Plays entire chord
  - `bass` Plays tonic
  - `arpeggio` Plays choard as arpeggio. Can take extra parameter ` rate=q`.
  - `improv` Improvises based on the chord. Can take extra parameters ` min_pitch=40 max_pitch=60`.
  - `lead` Plays a supplied note list
* `voice` is the General Midi name. If the style is `perc`, the voice should be a percussion name.
* `volume` is TODO

Each voice is assigned to a separate MIDI channel for a maximum 15 voices
and an additional 10 `perc`[ussion] styles.

### chord
Format: `chord name=cname notes=C,E,G,Bb`

midi_maker recognizes major, minor, augmented, diminished, 7th and 9th chord names,
but you may want to make your own, e.g `chord name=sus4 notes=C,F,G`. The notes are taken to apply to the key of C.

### rhythm
This can take either of two formats:

* Format1: `rhythm rname=rname values=d1,d2,d3,...`
* Format2: `rhythm name=rname seed=integer silence=float repeat=float notes=n1,n2,n3...`

Rhythms are of two sorts: values are supplied or random using seed, silence, repeat, notes.

Use these rhythms in compositions with `rhythm voice=vname rhythms=rname1,rname2...`

### tune
Format: `tune name=tname notes=note1,note2...`

Use tunes with the `play' command.

## Performance Commands
These generate the actual MIDI output using the definitions that have been created.

### bar
Format: `bar chords=chord1,chord2...`

### mute
The voices created with the `voice` command are initially all audible. Turn one or more voices off with `mute voices=voice1,voice2...`. Turn all voices off with `mute voices=all`.The inverse of `mute` is `hear`. 

### hear
If voices have been previously muted, turn one or more on with `hear voices=voice1,voice2...`. Turn all voices on with `hear voices=all`.

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
* `duration` is a note abbreviation such as `c` for quarter (a quarter-note). It can be dotted to make it 50% longer. A duration can be assembled from multiple notes, e.g. `q.+n` is 5½ beats.
* `note` is A-G with possible # or b e.g. `Eb`.
* `octave` is 1-10.
When supplying multiple notes, the duration and octave can be omitted if they match the previous note. e.g. a scale of G is `cG5,A,B,C6,D,E,F#,G`. Note that the `C` must be declared in octave 6, otherwise the C below G5 will play.

For example, `q.F#4` will play a dotted quarter-note F# in the 4th octave.

### chords
### names of notes
midi_maker uses the English names because their initial letters are (almost) unique. `sixteenth` is the exception; think of `h` as `half`.

| note name | 1/3 note | 2/3 note | abbrs |
| --------- | -------- | -------- | ----- |
| thirtysecondth | t_thirtysecondth | d_thirtysecondth | t, tt, dt |
| sixteenth | t_sixteenth | d_sixteenth | s, ts, ds |
| eighth | t_eighth | d_eighth | e, te, de |
| quarter | t_quarter | d_quarter | q, tq, dq |
| half | t_half | d_half | h, th, dh |
| note | t_note | d_note | n, tn dn |
| doublenote | t_doublenote | d_doublenote | d, td, dd |
