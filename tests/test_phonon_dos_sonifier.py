import pytest

pytest.importorskip("strauss")

from phonon_sonification.phonon_dos_sonifier import PhononDOSSonifier

from conftest import THZ


@pytest.fixture
def sonifier(patch_mp):
    return PhononDOSSonifier(mp_id="mp-test", temperatures=[300], duration=1.0)


def test_phonon_range_taken_from_data(sonifier):
    assert sonifier.fmin_phonon == pytest.approx(0.1 * THZ)
    assert sonifier.fmax_phonon == pytest.approx(20 * THZ)


def test_user_phonon_range_overrides_data(patch_mp):
    s = PhononDOSSonifier(mp_id="mp-test", duration=1.0, fmin_phonon=1e12, fmax_phonon=3e13)
    assert (s.fmin_phonon, s.fmax_phonon) == (1e12, 3e13)


def test_map_phonon_to_audible_scalar_and_endpoints(sonifier):
    result = sonifier.map_phonon_to_audible_linlin(sonifier.fmax_phonon)
    assert isinstance(result, float)
    assert result == pytest.approx(sonifier.fmax_audible)


def test_print_available_sites_shows_quantiles(sonifier, capsys):
    sonifier.print_available_sites(temperature=300)
    out = capsys.readouterr().out
    stats = sonifier.get_site_stats("A_1", 300)
    assert f"Q25:          {stats['quantile_25']:.2e} Hz" in out
    assert f"Q75:          {stats['quantile_75']:.2e} Hz" in out
    assert "(300K)" in out


def test_get_site_stats_errors(sonifier):
    with pytest.raises(ValueError, match="not found"):
        sonifier.get_site_stats("Zz_9")
    with pytest.raises(ValueError):
        sonifier.get_site_stats("A_1", temperature=1000)


def test_single_site_default_output_path(sonifier, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sonifier.sonify_single_site("A_1", mode="spectral")
    assert [p.name for p in tmp_path.glob("*.wav")] == ["phonon_mp-test_athermal_spectral__A_1.wav"]


@pytest.mark.parametrize("mode", ["spectral", "synth"])
def test_single_site_explicit_output(sonifier, tmp_path, mode):
    out = tmp_path / f"{mode}.wav"
    sonifier.sonify_single_site("B_1", temperature=300, mode=mode, output_path=str(out))
    assert out.stat().st_size > 0


def test_multi_site_synth_with_lfo(sonifier, tmp_path):
    out = tmp_path / "multi.wav"
    sonifier.sonify_multi_site([{"site": "A_1"}, {"site": "B_1"}], mode="synth", use_lfo=True,
                               lfo_target="volume", output_path=str(out))
    assert out.stat().st_size > 0


def test_all_sites_excludes_total(sonifier, tmp_path, monkeypatch):
    sonified = []
    monkeypatch.setattr(sonifier, "sonify_multi_site",
                        lambda site_configs, **kwargs: sonified.extend(c["site"] for c in site_configs))
    sonifier.sonify_all_sites()
    assert sonified == ["A_1", "B_1"]


def test_choral_missing_samples_raises(sonifier, tmp_path):
    with pytest.raises(FileNotFoundError, match="Choral samples not found"):
        sonifier.sonify_site_choral("A_1", sample_path=tmp_path / "missing")


def test_unknown_mode_raises(sonifier):
    with pytest.raises(AssertionError, match="mode not recognised"):
        sonifier.sonify_single_site("A_1", mode="kazoo")
