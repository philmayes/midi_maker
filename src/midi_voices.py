"""Names of the General MIDI (GM 1) voices."""

voices: dict[str, int] = {
    # General MIDI (GM 1) voices
    #_Piano
    'acoustic_grand_piano': 1,
    'bright_acoustic_piano': 2,
    'electric_grand_piano': 3   , # (usually modeled after Yamaha CP-70)
    'honky_tonk_piano': 4,
    'electric_piano_1': 5       , # (usually a Rhodes or Wurlitzer piano)
    'electric_piano_2': 6       , # (usually an FM piano patch, often chorused)
    'harpsichord': 7            , # (often with a fixed velocity level)
    'clavinet': 8,

    # Chromatic_percussion
    'celesta': 9,
    'glockenspiel': 10,
    'music_box': 11,
    'vibraphone': 12,
    'marimba': 13,
    'xylophone': 14,
    'tubular_bells': 15,
    'dulcimer_or_santoor': 16,

    # Organ
    'drawbar_organ': 17,
    'percussive_organ': 18,
    'rock_organ': 19,
    'church_organ': 20,
    'reed_organ': 21,
    'accordion': 22,
    'harmonica': 23,
    'bandoneon_or_tango_accordion': 24,

    # Guitar
    # In most synthesizer interpretations, guitar and bass sounds are set
    # an octave lower than other instruments.
    'acoustic_guitar_nylon': 25,
    'acoustic_guitar_steel': 26,
    'electric_guitar_jazz': 27,
    'electric_guitar_clean': 28 , # (clean, often chorused, resembling a Stratocaster run through a Roland Jazz Chorus amplifier)
    'electric_guitar_muted': 29,
    'electric_guitar_overdrive': 30,
    'electric_guitar_distortion': 31,
    'electric_guitar_harmonics': 32,

    # Bass
    'acoustic_bass': 33,
    'electric_bass_finger': 34,
    'electric_bass_picked': 35,
    'electric_bass_fretless': 36,
    'slap_bass_1': 37,
    'slap_bass_2': 38,
    'synth_bass_1': 39,
    'synth_bass_2': 40,

    # Strings
    'violin': 41,
    'viola': 42,
    'cello': 43,
    'contrabass': 44,
    'tremolo_strings': 45,
    'pizzicato_strings': 46,
    'orchestral_harp': 47,
    'timpani': 48,

    # Ensemble
    'string_ensemble_1': 49 , # (often in marcato)
    'string_ensemble_2': 50 , # (slower attack than String Ensemble 1)
    'synth_strings_1': 51,
    'synth_strings_2': 52,
    'choir_aahs': 53,
    'voice_oohs': 54        , # (or Doos)
    'synth_voice': 55,
    'orchestra_hit': 56,

    # Brass
    'trumpet': 57,
    'trombone': 58,
    'tuba': 59,
    'muted_trumpet': 60,
    'french_horn': 61,
    'brass_section': 62,
    'synth_brass_1': 63,
    'synth_brass_2': 64,

    # Reed
    'soprano_sax': 65,
    'alto_sax': 66,
    'tenor_sax': 67,
    'baritone_sax': 68,
    'oboe': 69,
    'english_horn': 70,
    'bassoon': 71,
    'clarinet': 72,

    # Pipe
    'piccolo': 73,
    'flute': 74,
    'recorder': 75,
    'pan_flute': 76,
    'blown_bottle': 77,
    'shakuhachi': 78,
    'whistle': 79,
    'ocarina': 80,

    # Synth_lead
    'synthlead_1_square': 81    , # (square, often chorused)
    'synthlead_2_sawtooth': 82  , # (sawtooth or saw, often chorused)
    'synthlead_3_calliope': 83  , # (calliope, usually resembling a woodwind)
    'synthlead_4_chiff': 84,
    'synthlead_5_charang': 85   , # (charang, a guitar-like lead)
    'synthlead_6_voice': 86     , # (voice, derived from "synth voice" with faster attack)
    'synthlead_7_fifths': 87,
    'synthlead_8_bass': 88      , # (bass and lead or solo lead or sometimes mistakenly called "brass and lead")

    # Synth_pad
    'synthpad_1_new_age': 89    , # (new age, pad stacked with a bell, often derived from "Fantasia" patch from Roland D-50)
    'synthpad_2_warm': 90       , # (warm, a mellower pad with slow attack)
    'synthpad_3_polysynth': 91  , # (polysynth or poly, a saw-like percussive pad resembling an early 1980s polyphonic synthesizer)
    'synthpad_4_choi': 92       , # (choir, identical to "synth voice" with longer decay)
    'synthpad_5_bowed_glass': 93, # (bowed glass or bowed, a sound resembling a glass harmonica)
    'synthpad_6_metallic': 94   , # (metallic, often created from a piano or guitar sample played with the attack removed)
    'synthpad_7_halo': 95       , # (halo, choir-like pad, often with a filter effect)
    'synthpad_8_sweep': 96      , # (sweep, pad with a pronounced "wah" filter effect)

    # Synth_effects
    'synth_1_rain': 97          , # (rain, a bright pluck with echoing pulses that decreases in pitch)
    'synth_2_soundtrack': 98    , # (soundtrack, a bright perfect fifth pad)
    'synth_3_crystal': 99       , # (crystal, a synthesized bell sound)
    'synth_4_atmosphere': 100   , # (atmosphere, usually a classical guitar-like sound)
    'synth_5_brightness': 101   , # (brightness, bright pad stacked with choir or bell)
    'synth_6_goblins': 102      , # (goblins, a slow-attack pad with chirping or murmuring sounds)
    'synth_7_echoes': 103       , # (echoes or echo drops, similar to "rain")
    'synth_8_sci_fi': 104       , # (sci-fi or star theme, usually an electric guitar-like pad)

    # Ethnic
    'sitar': 105,
    'banjo': 106,
    'shamisen': 107,
    'koto': 108,
    'kalimba': 109,
    'bag_pipe': 110,
    'fiddle': 111,
    'shanai': 112,

    # Percussive
    'tinkle_bell': 113,
    'agogo_or_cowbell': 114,
    'steel_drums': 115,
    'woodblock': 116,
    'taiko_drum_or_surdo': 117,
    'melodic_tom': 118,
    'synth_drum': 119       , # (a synthesized tom-tom derived from Simmons electronic drum)
    'reverse_cymbal': 120,

     # Sound_effects
    'guitar_fret_noise': 121,
    'breath_noise': 122,
    'seashore': 123,
    'bird_tweet': 124,
    'telephone_ring': 125,
    'helicopter': 126,
    'applause': 127,
    'gunshot': 128,
}
