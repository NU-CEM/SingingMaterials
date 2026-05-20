import math

# standard practice is to use sharps only.
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]

def phonon_to_audible_linlin(
    f_phonon,
    fmin_phonon,
    fmax_phonon,
    fmin_audio,
    fmax_audio
):
    """
    Linear mapping from phonon_frequency to audio_frequency.
    Preserves relative linear position within the phonon range, so fmin_phonon -> fmin_audio
    and fmax_phonon -> fmax_audio.
    Equal increments in phonon frequency map to equal increments in audio frequency.
    The (significant) trade-off for the mapping simplicity is that perceived pitch intervals are distorted: features at the
    top of the audio range sound compressed and features at the bottom sound stretched,
    since human pitch perception is approximately logarithmic in frequency.
    Frequencies can be in any units (e.g. THz), as long as they are consistent.
    """
    if f_phonon <= 0:
        raise ValueError("Phonon frequency must be positive")

    x = (f_phonon - fmin_phonon) / (fmax_phonon - fmin_phonon)
    return fmin_audio + x*(fmax_audio - fmin_audio)
  
def phonon_to_audible_linlog(
    f_phonon,
    fmin_phonon,
    fmax_phonon,
    fmin_audio,
    fmax_audio
):
    """
    Linear mapping from phonon_frequency to log(audio_frequency).
    Preserves relative linear position within the phonon range, so fmin_phonon -> fmin_audio
    and fmax_phonon -> fmax_audio.
    Equal increments in phonon frequency map to equal pitch
    intervals (equal ratios in audible frequency), regardless of where they sit
    in the spectrum. 
    Low-frequency features are spread out and high-frequency
    features are compressed in pitch, relative to a log-log mapping.
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
    Linear mapping from log(phonon_frequency) to log(audio_frequency).
    Preserves relative log position within the phonon range, so fmin_phonon -> fmin_audio
    and fmax_phonon -> fmax_audio. 
    Equal ratios in phonon frequency map to equal pitch intervals, so the relative spacing of spectral features is preserved.
    Octaves are stretched or compressed by the ratio
    log(fmax_audio/fmin_audio) / log(fmax_phonon/fmin_phonon).
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
        f_audio = phonon_to_audible_linlog(
            f_phonon,
            fmin_phonon,
            fmax_phonon,
            fmin_audio,
            fmax_audio
        )
    elif mapping=="linearscaling":
        f_audio = phonon_to_audible_linlin(
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
