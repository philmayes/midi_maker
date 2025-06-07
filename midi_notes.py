
class Note:
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

def str_to_note(name: str) -> int:
    """Returns the note duration described by the string."""
    d = Note.__dict__
    if name in d:
        return d[name]
    return 0
