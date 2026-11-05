# Singing Materials

`SingingMaterials` is a Python package which reads first-principles phonon data, analyses it, and uses [Strauss](https://www.audiouniverse.org/research/strauss) to turn it into sound; *to hear how materials sing*.

This repository holds the package only. For examples of how it has been used, including scripts, input files and sound examples, see the [SingingMaterials_Dissemination](https://github.com/lucydot/SingingMaterials_Dissemination) repository.

## What is this?

- The package focuses on phonon density of states (DOS) data, which is read in from the [Materials Project](https://next-gen.materialsproject.org/) or [phonondb](https://github.com/atztogo/phonondb/blob/main/mdr/phonondb/README.md) databases.
- It calculates statistics for each site in a material, such as the phonon band centre, the inter-quartile range and the Shannon entropy, optionally weighted by temperature. This part of the package can be used without producing any sound.
- Three sonification types are supported: spectral, synth and choral. These can be mixed together in different ways (superimpose, concatenate or a mixture of the two). Mixing is implemented through `ffmpeg`.
- Users are encouraged to use `.yml` files rather than the command line interface to create and mix sonifications. The command line interface does not allow mixing.
- The package is designed to be extendable, so that new types of phonon data, new data interfaces, and new sonifications can all be considered.
- This package will eventually power a Singing Materials web app.

This is alpha-release software: it has been tested, but there are likely still bugs - please use with caution! If you spot any issues please raise this on the [Issues page](https://github.com/NU-CEM/SingingMaterials/issues).

## Installation

```bash
pip install "SingingMaterials[all]"
```

This installs everything. The package is then imported in Python as `singingmaterials`. To leave out dependencies you don't need, choose from these options instead:

| Option | Needed to | Installs |
|---|---|---|
| `sound` | create sonifications | [Strauss](https://www.audiouniverse.org/research/strauss) |
| `mp` | read data from the Materials Project | [mp-api](https://docs.materialsproject.org/downloading-data/using-the-api/getting-started) |
| `phonopy` | read phonondb files | [phonopy](https://phonopy.github.io/phonopy/) |

For example, `pip install "SingingMaterials[mp]"` is enough to read Materials Project data and calculate statistics, without producing any sound. You need at least one of `mp` or `phonopy` to read in new data: with `pip install SingingMaterials` alone, only DOS data already cached in your working directory can be read. If you use a feature without its option installed, the error will say which one you need.

To read data from the Materials Project, [generate an API key](https://next-gen.materialsproject.org/api) and store it as `MP_API_KEY` in a `.env` file in your working directory (or one of its parents), or set it as an environment variable.

Mixing sonifications also needs [`ffmpeg`](https://ffmpeg.org/) on your path.

The choral sonification uses the Solitary Choir samples by [James Peacock](https://www.pianobook.co.uk/profile/jamespeacock42), which are not distributed with this package. Set `PHONON_CHORAL_SAMPLES` to the folder holding the sample `.wav` files, as an environment variable or in your `.env` file, or pass `sample_path` to `sonify_site_choral`.

To work on the package itself, clone this repository and run `pip install -e ".[all,test]"` from its root. The test suite is then run with `pytest`.

## Usage

### Creating sonifications

From the command line:

```bash
phonon-sonify mp-3953 --info --temp 300          # print the sites available for a material
phonon-sonify mp-3953 --temp 300 --all-sites     # sonify all sites (spectral mode by default)
phonon-sonify mp-3953 --site O_6 --mode synth --lfo
phonon-sonify-yaml my_spec.yml                   # create and mix sonifications from a spec file
```

See [`spec_example.yml`](https://github.com/NU-CEM/SingingMaterials/blob/main/singingmaterials/spec_example.yml) for the spec file format.

From Python:

```python
from singingmaterials import PhononDOSSonifier

sonifier = PhononDOSSonifier(mp_id="mp-3953", temperatures=[300], duration=10.0)
sonifier.print_available_sites(temperature=300)
sonifier.sonify_all_sites(temperature=300, output_path="mp-3953.wav")
```

### Data and statistics only

```python
from singingmaterials.dos_stats import dos_dict_to_dataframe, dos_stats_analysis

dos_dict = dos_stats_analysis(mp_id="mp-3953", temp=300)
print(dos_dict["projection"]["total"]["stats"]["thermal"]["300"]["band_centre"])  # in Hz
print(dos_dict_to_dataframe(dos_dict))
```

## Package structure

`mp_interface.py` : interface to the Materials Project database holding density of states data.

`phonopy_interface.py` : reads in data from a phonopy yml file, and generates density of states data for a given mesh. The phonopy files are distributed as part of [phonondb](https://github.com/atztogo/phonondb/blob/main/mdr/phonondb/README.md). This module requires phonopy to be installed.

`dos_stats.py` : this reads in density of states data via one of the interfaces and post-processes it ready for analysis or sonification.

`visualisation.py` : functions for plotting the density of states data. because seeing things is still useful.

`utilities.py` : small utility functions.

`frequency_mapping.py` : functions for mapping from phonon frequencies to audible frequencies.

`phonon_dos_sonifier.py`: takes the post-processed density of states data and sonifies it using Strauss. Three sonification strategies are implemented: spectral (using the Strauss spectraliser), synth (using the Strauss synth) and choral (using the strauss sampler and choral samples). This module requires Strauss to be installed.

`phonon_mixer.py` : takes the `.wav` files created by `phonon_dos_sonifier.py` and mixes them together with `ffmpeg`.

`cli.py` : command-line-interface for the `phonon_dos_sonifier` module. Allows the user to create `.wav` files for the spectral, synth or choral sonifications, but does not allow user to mix these together.

`run_from_yaml.py` : reads in a `.yml` spec file (see `spec_example.yml`) and uses it to create and mix sonifications.

`spec_example.yml` : example yml file which specifies how to create the sonifications and mix them together.

`mods.py` : dictionaries specifying mods to the Strauss synthesiser parameters.

## Citation

If you use this package please cite the following [pre-print](https://arxiv.org/abs/2603.29037), which will later be published as part of the [ICAD proceedings](https://interactive-sonification.org/icad2026/):

Whalley, L., Shepherd, R., Boehringer, J., Knotts, S., Vickers, P., Caselton, G., Harrison, C., Hogg, B., Ratliff, D., Davenport, C., & Portas, A. (2026). *Singing Materials: Initial experiments in applying sonification to phonon spectra.* arXiv:2603.29037 [cond-mat.mtrl-sci]

## Use of AI

From October 2026, AI was used to make changes to this repository. Commit `b11c2ef` ("Create LICENSE.md", 15 September 2026) is the last commit made before then. Every commit after it, starting with `6d034a0` ("Fix crashes and incorrect results in phonon_sonification"), was written using [Claude Code](https://claude.com/claude-code), an AI coding assistant, running Anthropic's Claude Opus 5.5 model. Most of these commits carry a `Co-Authored-By: Claude` line in their commit message, so they can be listed with `git log --grep="Co-Authored-By: Claude"`; those committed by the maintainer may not.

The repository maintainer asked for a review of the repository, chose which suggested changes to make, and directed the work. The AI assistant wrote the code, tests and text in these commits, including this statement. The changes were:

- fixing bugs in the package, including a bug that misaligned phonon densities and frequencies when imaginary modes were removed, and an incorrect sign in the Shannon entropy;
- packaging (`pyproject.toml`, command-line entry points), a `pytest` test suite and a GitHub Actions workflow;
- removing unused code, caching Materials Project data as JSON rather than pickle, tidying the READMEs and adding `CITATION.cff`;
- organising the `workshops` folder and correcting material IDs in the quartz, salt and graphite specs (these specs have since been removed from this repository);
- preparing the package for release on PyPI, including a publishing workflow, finding `.env` files and choral samples when the package is installed outside a clone, and exporting `PhononDOSSonifier` from the package;
- removing everything other than the package from this repository, following the move of the examples to [SingingMaterials_Dissemination](https://github.com/lucydot/SingingMaterials_Dissemination), making Strauss and mp-api optional dependencies, rewriting this README, and renaming the package from `phonon_sonification` to `SingingMaterials`.

The test suite passes in CI on Python 3.11 to 3.13. Some changes have not been checked against real data: choral sonification is untested because its samples are not in the repository, the graphite site labels (`C_1`, `C_2`) are unverified, and cached DOS files made before the misalignment fix still need regenerating. Commit hashes above refer to the `fix/phonon-sonification-bugs` branch and may change if that branch is rebased or squashed when merged.
