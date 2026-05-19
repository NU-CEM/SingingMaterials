import math

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]

def phonon_to_audible_linearscaling(
    f_phonon,
    fmin_phonon,
    fmax_phonon,
    fmin_audio,
    fmax_audio
):
    """
    Linearly compress phonon frequency to audible frequency.
    
    Frequencies can be in any units (e.g. THz), as long as they are consistent.
    """
    if f_phonon <= 0:
        raise ValueError("Phonon frequency must be positive")

    x = (f_phonon - fmin_phonon) / (fmax_phonon - fmin_phonon)
    return fmin_audio + x*(fmax_audio - fmin_audio)
  
def phonon_to_audible_log(
    f_phonon,
    fmin_phonon,
    fmax_phonon,
    fmin_audio,
    fmax_audio
):
    """
    Logarithmically map phonon frequency to audible frequency.
    
    Frequencies can be in any units (e.g. THz), as long as they are consistent.
    """
    if f_phonon <= 0:
        raise ValueError("Phonon frequency must be positive")

    x = (f_phonon - fmin_phonon) / (fmax_phonon - fmin_phonon)
    return fmin_audio * (fmax_audio / fmin_audio) ** x

def phonon_to_audible_loglog(
    f_phonon,
    fmin_phonon,
    fmax_phonon,
    fmin_audio,
    fmax_audio
):
    """
    Map phonon frequency -> audible frequency
    preserving octave relationships.

    Doubling phonon frequency -> doubling audible frequency.
    Frequencies can be in any units (e.g. THz), as long as they are consistent.
    """

    if f_phonon <= 0:
        raise ValueError("Phonon frequencies must be positive")

    # normalised position in log-frequency space
    x = math.log(f_phonon / fmin_phonon) / math.log(fmax_phonon / fmin_phonon)

    # logarithmic interpolation in audio space
    return fmin_audio * (fmax_audio / fmin_audio) ** x

def frequency_to_note(freq):
    """
    Convert frequency (Hz) to nearest musical note and octave.
    """
    if freq <= 0:
        return None

    n = round(12 * math.log2(freq / 440.0))
    note_index = (n + 9) % 12
    octave = 4 + (n + 9) // 12

    return NOTE_NAMES[note_index], octave

def note_to_frequency(note, octave):
    note_index = NOTE_NAMES.index(note)
    n = note_index - 9 + 12 * (octave - 4)
    return 440.0 * 2 ** (n / 12)

def phonon_to_note(
    f_phonon,
    fmin_phonon,
    fmax_phonon,    
    fmin_audio,
    fmax_audio,
    mapping="linearscaling"
):

    if mapping=="loglog":
        f_audio = phonon_to_audible_loglog(
            f_phonon,
            fmin_phonon,
            fmax_phonon,
            fmin_audio,
            fmax_audio
        )
    elif mapping=="log":
        f_audio = phonon_to_audible_log(
            f_phonon,
            fmin_phonon,
            fmax_phonon,
            fmin_audio,
            fmax_audio
        )
    elif mapping=="linearscaling":
        f_audio = phonon_to_audible_linearscaling(
            f_phonon,
            fmin_phonon,
            fmax_phonon,
            fmin_audio,
            fmax_audio
        )

    note, octave = frequency_to_note(f_audio)
    note_octave = note+str(octave)

    return {
        "phonon_frequency": f_phonon,
        "mapping type": mapping,
        "audible_frequency": f_audio,
        "note": note,
        "octave": octave,
        "note-octave": note_octave
    }
