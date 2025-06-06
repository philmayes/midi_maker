voices = {
    # General MIDI (GM 1) voices
    #_Piano
    'acoustic_grand_piano': 0,
    'bright_acoustic_piano': 1,
    'electric_grand_piano': 2   , # (usually modeled after Yamaha CP-70)
    'honky_tonk_piano': 3,
    'electric_piano_1': 4       , # (usually a Rhodes or Wurlitzer piano)
    'electric_piano_2': 5       , # (usually an FM piano patch, often chorused)
    'harpsichord': 6            , # (often with a fixed velocity level)
    'clavinet': 7,

    # Chromatic_percussion
    'celesta': 8,
    'glockenspiel': 9,
    'music_box': 10,
    'vibraphone': 11,
    'marimba': 12,
    'xylophone': 13,
    'tubular_bells': 14,
    'dulcimer_or_santoor': 15,

    # Organ
    'drawbar_organ': 16,
    'percussive_organ': 17,
    'rock_organ': 18,
    'church_organ': 19,
    'reed_organ': 20,
    'accordion': 21,
    'harmonica': 22,
    'bandoneon_or_tango_accordion': 23,

    # Guitar
    # In most synthesizer interpretations, guitar and bass sounds are set
    # an octave lower than other instruments.
    'acoustic_guitar_nylon': 24,
    'acoustic_guitar_steel': 25,
    'electric_guitar_jazz': 26,
    'electric_guitar_clean': 27 , # (clean, often chorused, resembling a Stratocaster run through a Roland Jazz Chorus amplifier)
    'electric_guitar_muted': 28,
    'electric_guitar_overdrive': 29,
    'electric_guitar_distortion': 30,
    'electric_guitar_harmonics': 31,

    # Bass
    'acoustic_bass': 32,
    'electric_bass_finger': 33,
    'electric_bass_picked': 34,
    'electric_bass_fretless': 35,
    'slap_bass_1': 36,
    'slap_bass_2': 37,
    'synth_bass_1': 38,
    'synth_bass_2': 39,

    # Strings
    'violin': 40,
    'viola': 41,
    'cello': 42,
    'contrabass': 43,
    'tremolo_strings': 44,
    'pizzicato_strings': 45,
    'orchestral_harp': 46,
    'timpani': 47,

    # Ensemble
    'string_ensemble_1': 48 , # (often in marcato)
    'string_ensemble_2': 49 , # (slower attack than String Ensemble 1)
    'synth_strings_1': 50,
    'synth_strings_2': 51,
    'choir_aahs': 52,
    'voice_oohs': 53        , # (or Doos)
    'synth_voice': 54,
    'orchestra_hit': 55,

    # Brass
    'trumpet': 56,
    'trombone': 57,
    'tuba': 58,
    'muted_trumpet': 59,
    'french_horn': 60,
    'brass_section': 61,
    'synth_brass_1': 62,
    'synth_brass_2': 63,

    # Reed
    'soprano_sax': 64,
    'alto_sax': 65,
    'tenor_sax': 66,
    'baritone_sax': 67,
    'oboe': 68,
    'english_horn': 69,
    'bassoon': 70,
    'clarinet': 71,

    # Pipe
    'piccolo': 72,
    'flute': 73,
    'recorder': 74,
    'pan_flute': 75,
    'blown_bottle': 76,
    'shakuhachi': 77,
    'whistle': 78,
    'ocarina': 79,

    # Synth_lead
    'synthlead_1_square': 80    , # (square, often chorused)
    'synthlead_2_sawtooth': 81  , # (sawtooth or saw, often chorused)
    'synthlead_3_calliope': 82  , # (calliope, usually resembling a woodwind)
    'synthlead_4_chiff': 83,
    'synthlead_5_charang': 84   , # (charang, a guitar-like lead)
    'synthlead_6_voice': 85     , # (voice, derived from "synth voice" with faster attack)
    'synthlead_7_fifths': 86,
    'synthlead_8_bass': 87      , # (bass and lead or solo lead or sometimes mistakenly called "brass and lead")

    # Synth_pad
    'synthpad_1_new_age': 88    , # (new age, pad stacked with a bell, often derived from "Fantasia" patch from Roland D-50)
    'synthpad_2_warm': 89       , # (warm, a mellower pad with slow attack)
    'synthpad_3_polysynth': 90  , # (polysynth or poly, a saw-like percussive pad resembling an early 1980s polyphonic synthesizer)
    'synthpad_4_choi': 91       , # (choir, identical to "synth voice" with longer decay)
    'synthpad_5_bowed_glass': 92, # (bowed glass or bowed, a sound resembling a glass harmonica)
    'synthpad_6_metallic': 93   , # (metallic, often created from a piano or guitar sample played with the attack removed)
    'synthpad_7_halo': 94       , # (halo, choir-like pad, often with a filter effect)
    'synthpad_8_sweep': 95      , # (sweep, pad with a pronounced "wah" filter effect)

    # Synth_effects
    'synth_1_rain': 96          , # (rain, a bright pluck with echoing pulses that decreases in pitch)
    'synth_2_soundtrack': 97    , # (soundtrack, a bright perfect fifth pad)
    'synth_3_crystal': 98       , # (crystal, a synthesized bell sound)
    'synth_4_atmosphere': 99    , # (atmosphere, usually a classical guitar-like sound)
    'synth_5_brightness': 100   , # (brightness, bright pad stacked with choir or bell)
    'synth_6_goblins': 101      , # (goblins, a slow-attack pad with chirping or murmuring sounds)
    'synth_7_echoes': 102       , # (echoes or echo drops, similar to "rain")
    'synth_8_sci_fi': 103       , # (sci-fi or star theme, usually an electric guitar-like pad)

    # Ethnic
    'sitar': 104,
    'banjo': 105,
    'shamisen': 106,
    'koto': 107,
    'kalimba': 108,
    'bag_pipe': 109,
    'fiddle': 110,
    'shanai': 111,

    # Percussive
    'tinkle_bell': 112,
    'agogô_or_cowbell': 113,
    'steel_drums': 114,
    'woodblock': 115,
    'taiko_drum_or_surdo': 116,
    'melodic_tom': 117,
    'synth_drum': 118       , # (a synthesized tom-tom derived from Simmons electronic drum)
    'reverse_cymbal': 119,

     # Sound_effects
    'guitar_fret_noise': 120,
    'breath_noise': 121,
    'seashore': 122,
    'bird_tweet': 123,
    'telephone_ring': 124,
    'helicopter': 125,
    'applause': 126,
    'gunshot': 127,
}
