import copy

import numpy as np
import pytest

THZ = 1e12

# Gaussian site DOS, so the expected statistics are known analytically.
SITE_PARAMS = {
    "A_1": {"centre": 5 * THZ, "sigma": 1 * THZ, "weight": 1.0},
    "B_1": {"centre": 12 * THZ, "sigma": 1.5 * THZ, "weight": 2.0},
}


def gaussian(f, centre, sigma, weight):
    return weight * np.exp(-0.5 * ((f - centre) / sigma) ** 2)


def make_dos_dict(mp_id="mp-test"):
    frequencies = np.linspace(0.1 * THZ, 20 * THZ, 2000)
    projection = {}
    for site, p in SITE_PARAMS.items():
        projection[site] = {"densities": gaussian(frequencies, **p), "frequencies": frequencies}
    projection["total"] = {
        "densities": sum(v["densities"] for v in projection.values()),
        "frequencies": frequencies,
    }
    return {
        "metadata": {"mp_id": mp_id, "bin_width": frequencies[1] - frequencies[0]},
        "projection": projection,
    }


@pytest.fixture
def raw_dos_dict():
    """Raw DOS dict as returned by the mp/phonopy interfaces (no stats yet)."""
    return make_dos_dict()


@pytest.fixture
def patch_mp(monkeypatch):
    """Make dos_stats read the synthetic DOS instead of the Materials Project."""
    from phonon_sonification import mp_interface

    raw = make_dos_dict()
    monkeypatch.setattr(mp_interface, "get_dos_raw_mp", lambda mp_id: copy.deepcopy(raw))
    return raw
