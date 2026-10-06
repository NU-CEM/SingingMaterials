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


class FakeSonifier:
    """Records how run_spec drives the sonifier, writing an empty file for each job."""

    def __init__(self, **kwargs):
        FakeSonifier.init_kwargs = kwargs
        FakeSonifier.outputs = []

    def print_available_sites(self, temperature=None):
        pass

    def _record(self, output_path, **kwargs):
        FakeSonifier.outputs.append(output_path)
        open(output_path, "w").close()

    def sonify_all_sites(self, **kwargs):
        self._record(**kwargs)

    def sonify_single_site(self, site_name, **kwargs):
        self._record(**kwargs)


def run(tmp_path, monkeypatch, spec_text):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_from_yaml, "PhononDOSSonifier", FakeSonifier)
    (tmp_path / "spec.yml").write_text(spec_text)
    run_from_yaml.run_spec("spec.yml")


@pytest.mark.parametrize("spec_text", [
    "mp_id: mp-66\nglobals:\n  duration: 5.0\njobs:\n  - name: one\n    mode: synth\n    sites: all\n",
    "globals:\n  mp_id: mp-66\n  duration: 5.0\njobs:\n  - name: one\n    mode: synth\n    sites: all\n",
])
def test_mp_id_at_top_level_or_in_globals(tmp_path, monkeypatch, spec_text):
    run(tmp_path, monkeypatch, spec_text)
    assert FakeSonifier.init_kwargs["mp_id"] == "mp-66"
    assert FakeSonifier.init_kwargs["duration"] == 5.0


def test_globals_mp_id_takes_precedence(tmp_path, monkeypatch):
    run(tmp_path, monkeypatch, "mp_id: mp-1\nglobals:\n  mp_id: mp-2\njobs:\n  - name: one\n    mode: synth\n    sites: all\n")
    assert FakeSonifier.init_kwargs["mp_id"] == "mp-2"


def test_job_output_and_generated_names(tmp_path, monkeypatch):
    run(tmp_path, monkeypatch,
        "mp_id: mp-66\njobs:\n"
        "  - name: one\n    mode: choral\n    sites: all\n    output: custom.wav\n"
        "  - name: two\n    mode: synth\n    sites: C_1\n")
    assert FakeSonifier.outputs == ["custom.wav", "mode-synth_sites-C_1_mp_id-mp-66.wav"]
