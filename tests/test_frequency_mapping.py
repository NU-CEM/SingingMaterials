import math

import pytest

from phonon_sonification import frequency_mapping as fm

FMIN_PH, FMAX_PH = 1e12, 2e13
FMIN_AU, FMAX_AU = 98.0, 587.33

MAPPINGS = [fm.phonon_to_audible_linlin, fm.phonon_to_audible_linlog, fm.phonon_to_audible_loglog]


@pytest.mark.parametrize("mapping", MAPPINGS)
def test_endpoints_map_to_audible_range(mapping):
    assert mapping(FMIN_PH, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU) == pytest.approx(FMIN_AU)
    assert mapping(FMAX_PH, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU) == pytest.approx(FMAX_AU)


@pytest.mark.parametrize("mapping", MAPPINGS)
def test_non_positive_frequency_raises(mapping):
    with pytest.raises(ValueError):
        mapping(0, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU)
    with pytest.raises(ValueError):
        mapping(-1e12, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU)


def test_linlin_midpoint_is_arithmetic_mean():
    mid = (FMIN_PH + FMAX_PH) / 2
    assert fm.phonon_to_audible_linlin(mid, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU) == pytest.approx((FMIN_AU + FMAX_AU) / 2)


def test_linlog_midpoint_is_geometric_mean():
    mid = (FMIN_PH + FMAX_PH) / 2
    assert fm.phonon_to_audible_linlog(mid, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU) == pytest.approx(math.sqrt(FMIN_AU * FMAX_AU))


def test_loglog_preserves_frequency_ratios():
    def f(x):
        return fm.phonon_to_audible_loglog(x, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU)

    # equal phonon ratios give equal audio ratios
    assert f(4e12) / f(2e12) == pytest.approx(f(1.6e13) / f(8e12))


@pytest.mark.parametrize("freq, expected", [(440.0, ("A", 4)), (261.63, ("C", 4)), (98.0, ("G", 2)), (587.33, ("D", 5))])
def test_frequency_to_note(freq, expected):
    assert fm.frequency_to_note(freq) == expected


def test_frequency_to_note_non_positive():
    assert fm.frequency_to_note(0) is None


@pytest.mark.parametrize("note", fm.NOTE_NAMES)
@pytest.mark.parametrize("octave", [2, 4, 6])
def test_note_frequency_round_trip(note, octave):
    assert fm.frequency_to_note(fm.note_to_frequency(note, octave)) == (note, octave)


@pytest.mark.parametrize("mapping", ["linearscaling", "log", "loglog"])
def test_phonon_to_note_endpoints(mapping):
    low = fm.phonon_to_note(FMIN_PH, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU, mapping=mapping)
    high = fm.phonon_to_note(FMAX_PH, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU, mapping=mapping)
    assert low["note-octave"] == "G2"
    assert high["note-octave"] == "D5"
    assert low["audible_frequency"] == pytest.approx(FMIN_AU)


def test_phonon_to_note_unknown_mapping_raises():
    with pytest.raises(ValueError):
        fm.phonon_to_note(5e12, FMIN_PH, FMAX_PH, FMIN_AU, FMAX_AU, mapping="not-a-mapping")
