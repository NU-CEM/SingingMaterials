import json
import subprocess
import sys


def run_without(modules, code, cwd=None):
    # a fresh interpreter, as this test session may already have imported the modules
    hide = "import sys\n" + "".join(f"sys.modules[{m!r}] = None\n" for m in modules)
    return subprocess.run([sys.executable, "-c", hide + code], capture_output=True, text=True, cwd=cwd)


def test_data_and_statistics_modules_import_without_optional_dependencies():
    result = run_without(
        ["strauss", "mp_api", "phonopy"],
        "import singingmaterials\n"
        "from singingmaterials import dos_stats, frequency_mapping, mp_interface, utilities, visualisation\n")
    assert result.returncode == 0, result.stderr


def test_sonifier_explains_how_to_install_strauss():
    result = run_without(["strauss"], "from singingmaterials import PhononDOSSonifier\n")
    assert result.returncode != 0
    assert "SingingMaterials[sound]" in result.stderr


def test_fetching_from_materials_project_explains_how_to_install_mp_api(tmp_path):
    result = run_without(
        ["mp_api"], "from singingmaterials import mp_interface\nmp_interface.get_dos_raw_mp('mp-test')\n", cwd=tmp_path)
    assert result.returncode != 0
    assert "SingingMaterials[mp]" in result.stderr


def test_cached_dos_read_without_mp_api(tmp_path):
    cached = {"metadata": {"mp_id": "mp-test"}, "projection": {}}
    (tmp_path / "mp-test_dos.json").write_text(json.dumps(cached))
    result = run_without(
        ["mp_api"], "from singingmaterials import mp_interface\nmp_interface.get_dos_raw_mp('mp-test')\n", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
