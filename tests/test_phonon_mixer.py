import pytest

from phonon_sonification import phonon_mixer

OUTPUTS = {"one": "one.wav", "two": "two.wav", "three": "three.wav"}
JOB_ORDER = ["one", "two", "three"]
SPEC = {"jobs": [{"name": n} for n in JOB_ORDER]}


def input_files(cmd):
    return [cmd[i + 1] for i, arg in enumerate(cmd) if arg == "-i"]


def test_superposition_with_weights():
    cmd = phonon_mixer.superposition(OUTPUTS, {"output": "mix.wav", "weights": {"one": 0.5}})
    assert input_files(cmd) == ["one.wav", "two.wav", "three.wav"]
    assert "amix=inputs=3:weights=0.5 1.0 1.0:normalize=1" in cmd
    assert cmd[-1] == "mix.wav"


def test_concatenation_default_order():
    cmd = phonon_mixer.concatenation(OUTPUTS, JOB_ORDER, {"output": "mix.wav"}, SPEC)
    assert input_files(cmd) == ["one.wav", "two.wav", "three.wav"]
    assert cmd[cmd.index("-map") + 1] == "[x2]"


def test_concatenation_explicit_order():
    cmd = phonon_mixer.concatenation(OUTPUTS, JOB_ORDER, {"output": "mix.wav", "order": ["three", "one"]}, SPEC)
    assert input_files(cmd) == ["three.wav", "one.wav"]


def test_concatenation_unknown_job_raises():
    with pytest.raises(ValueError):
        phonon_mixer.concatenation(OUTPUTS, JOB_ORDER, {"output": "mix.wav", "order": ["four"]}, SPEC)


def test_concatenation_random_order():
    cmd = phonon_mixer.concatenation(OUTPUTS, JOB_ORDER, {"output": "mix.wav", "order": "random 5"}, SPEC)
    files = input_files(cmd)
    assert len(files) == 5
    assert set(files) <= set(OUTPUTS.values())


def test_start_mixing_runs_ffmpeg(monkeypatch):
    calls = []
    monkeypatch.setattr(phonon_mixer.subprocess, "run", lambda cmd, check: calls.append(cmd))
    spec = dict(SPEC, mix={"mode": "super", "output": "mix.wav", "overwrite": True, "quiet": True})
    phonon_mixer.start_mixing(OUTPUTS, JOB_ORDER, spec)
    assert calls[0][:4] == ["ffmpeg", "-loglevel", "error", "-y"]


def test_start_mixing_unknown_mode_raises(monkeypatch):
    monkeypatch.setattr(phonon_mixer.subprocess, "run", lambda cmd, check: pytest.fail("ffmpeg should not run"))
    with pytest.raises(ValueError):
        phonon_mixer.start_mixing(OUTPUTS, JOB_ORDER, dict(SPEC, mix={"mode": "nope", "output": "mix.wav"}))
