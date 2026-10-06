import pickle
from types import SimpleNamespace

import numpy as np
import pytest

from phonon_sonification import mp_interface


def fake_mp_dos():
    """Stand-in for a pymatgen PhononDos with two sites and some imaginary modes (frequencies in THz)."""
    frequencies = np.array([-1.0, 0.0, 1.0, 2.0, 3.0])
    projected = [np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([10.0, 20.0, 30.0, 40.0, 50.0])]
    sites = [SimpleNamespace(label="Mg_1"), SimpleNamespace(label="O_1")]
    structure = SimpleNamespace(relabel_sites=lambda: SimpleNamespace(sites=sites))
    return SimpleNamespace(
        frequencies=frequencies,
        densities=projected[0] + projected[1],
        projected_densities=projected,
        structure=structure,
    )


def test_fetch_builds_aligned_dos_dict_and_caches(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mp_interface, "dos_data_from_mp_id", lambda mp_id: fake_mp_dos())

    d = mp_interface.get_dos_raw_mp("mp-test")

    np.testing.assert_allclose(d["projection"]["total"]["frequencies"], [1e12, 2e12, 3e12])
    np.testing.assert_array_equal(d["projection"]["total"]["densities"], [33.0, 44.0, 55.0])
    np.testing.assert_array_equal(d["projection"]["Mg_1"]["densities"], [3.0, 4.0, 5.0])
    np.testing.assert_array_equal(d["projection"]["O_1"]["densities"], [30.0, 40.0, 50.0])
    assert d["metadata"] == {"mp_id": "mp-test", "bin_width": pytest.approx(1e12)}
    assert (tmp_path / "mp-test_dos.pickle").is_file()


def test_reads_from_cache_without_network(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cached = {"metadata": {"mp_id": "mp-test"}, "projection": {}}
    with open(tmp_path / "mp-test_dos.pickle", "wb") as handle:
        pickle.dump(cached, handle)

    def no_network(mp_id):
        raise AssertionError("should not query the Materials Project when a cache exists")

    monkeypatch.setattr(mp_interface, "dos_data_from_mp_id", no_network)
    assert mp_interface.get_dos_raw_mp("mp-test") == cached


def test_missing_phonon_data_raises(monkeypatch):
    class FailingRester:
        def __init__(self, api_key):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_phonon_dos_by_material_id(self, mp_id):
            raise RuntimeError("no phonon data")

    monkeypatch.setattr(mp_interface, "MPRester", FailingRester)
    with pytest.raises(ValueError, match="mp-test"):
        mp_interface.dos_data_from_mp_id("mp-test")
