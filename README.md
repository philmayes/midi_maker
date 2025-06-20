## Overview
`midi_maker` interprets a text file and generates a midi file from it.
## Syntax
The text file syntax is a list of commands with the format: `command [param=value] [param=value] ...`. Values are case-sensitive. 
By convention, a param name is plural when it can take multiple values separated by commas.

Comments start with`;`.

## Definition Commands

### voice

### rythm
Rhythms are of two sorts: values are supplied or random using seed, silence, repeat, notes.

Use these rhythms in compositions with `rhythm voice=vvv rhythms=r1,r2,...`

### tune
Use tune commands with `play voice=vvv tunes=t1,t2,...`

## Performance Commands
### opus

### composition

### tempo

### hear

### bar


### Names of notes
midi_maker uses the English names because their initial letters are (almost) unique. `semiquaver` is the exception, think of `h` as `half`.

| note name | 1/3 note | 2/3 note | abbrs |
| --------- | -------- | -------- | ----- |
| demisemiquaver | t_demisemiquaver | d_demisemiquaver | d, td, dd |
| semiquaver | t_semiquaver | d_semiquaver | h, th, dh |
| quaver | t_quaver | d_quaver | q, tq, dq |
| crotchet | t_crotchet | d_crotchet | c, tc, dc |
| minim | t_minim | d_minim | m, tm, dm |
| semibreve | t_semibreve | d_semibreve | s, ts, ds |
| breve | t_breve | d_breve | b, tb, db |
