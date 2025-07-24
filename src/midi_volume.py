"""This module supplies default volumes for voices."""

dynamics: dict[str, int] = {
    # A dictionary that translates musical names to MIDI velocity aka volume.
    # It is copied and added to by midi_parse.get_all_volumes().
    # Eight musical names: https://en.wikipedia.org/wiki/Dynamics_(music)
    # Seven steps of 17: 8 + 7 * 17 == 127
    'ppp':  8,
    'pp':  25,
    'p':   42,
    'mp':  59,
    'mf':  76,
    'f':   93,
    'ff': 110,
    'fff':127,
}
