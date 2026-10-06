import pytest

pytest.importorskip("strauss")

from phonon_sonification import run_from_yaml


def test_expand_sweeps_is_cartesian_product():
    cases = list(run_from_yaml.expand_sweeps({"temp": [100, 300], "mode": ["synth", "choral"]}))
    assert len(cases) == 4
    assert {"temp": 300, "mode": "choral"} in cases


def test_expand_sweeps_empty():
    assert list(run_from_yaml.expand_sweeps({})) == [{}]


def test_merge_later_dicts_take_precedence():
    assert run_from_yaml.merge({"a": 1, "b": 1}, None, {"b": 2}) == {"a": 1, "b": 2}


def test_sanitise():
    assert run_from_yaml.sanitise(None) == "none"
    assert run_from_yaml.sanitise("O_6 Ca/1") == "O_6Ca1"


def test_build_filename():
    cfg = {"mode": "synth", "sites": "C_1", "temp": 300, "mp_id": "mp-66", "name": "ignored"}
    assert run_from_yaml.build_filename(cfg) == "mode-synth_sites-C_1_temp-300K_mp_id-mp-66.wav"


def test_run_job_rejects_invalid_sites():
    with pytest.raises(ValueError):
        run_from_yaml.run_job(sonifier=None, cfg={"mode": "synth", "sites": 3}, output="out.wav")
