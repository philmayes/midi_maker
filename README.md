# Midi Maker
## Overview
`midi_maker` interprets a text file (by convention using a .ini extension) and generates a midi file from it with the same filename in the same directory.
### Dependencies
It uses [MIDIUtil](https://midiutil.readthedocs.io/) to create a MIDI file and [FluidSynth](https://www.fluidsynth.org/) if you want to listen to the generated file.
### Syntax
The text file syntax is a list of commands with the format: `command param1=value1 param2=value2,value3...`.
For example:
```
; Definitions
voice  name=perc1 style=perc     voice=high_mid_tom
voice  name=rick  style=rhythm   voice=acoustic_grand_piano
voice  name=dave  style=lead     voice=cello
rhythm name=perc1a durations=h,e,e,q
tune   name=tune1 notes=q,G,A,B,hC@6,h.C,qC,G@5,A,hB,h.B
; Performance
rhythm voices=perc1 rhythms=perc1a ; play high_mid_tom with rhythm perc1a
play   voice=dave tunes=tune1      ; play tune1 on cello
bar    chords=C
bar    chords=Am
bar    chords=D7
bar    chords=G
```
Full details in the [docs](DOCS.md) file.

### Examples
There are examples of input files in the `data/` directory.

## License
[MIT](LICENSE.txt)
