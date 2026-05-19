## What is this?

- This is a Python-based, [Strauss](https://www.audiouniverse.org/research/strauss)-powered package which sonifies first-principles phonon data. 
- At the moment the focus is on phonon density of states data, which is read in from the [Materials Project](https://next-gen.materialsproject.org/) or [phonondb](https://github.com/atztogo/phonondb/blob/main/mdr/phonondb/README.md) databases.
- Currently three sonification types are supported: spectral, synth and choral. These can be mixed together in different ways (superimpose, concatenate or a mixture of the two). Mixing is implemented through `ffmpeg`.
- Users are encouraged to use `.yml` files rather than the command line interface to create and mix sonifications. The command line interface does not allow mixing.
- The package is designed to by extendable, so that new types of phonon data, new data interfaces, and new sonifications can all be considered.
- This package will eventually power a Singing Materials web app.

## Important note

This is alpha-release software: it has been tested, but there are likely still bugs - please use with caution! If you spot any issues please raise this on the [Issues page](https://github.com/NU-CEM/Singing_Materials_Strauss/issues).

### Package structure:

`mp_interface.py` : interface to the Materials Project database holding density of states data.

`phonopy_interface.py` : reads in data from a phonopy yml file, and generates density of states data for a given mesh. The phonopy files are distributed as part of [phonondb](https://github.com/atztogo/phonondb/blob/main/mdr/phonondb/README.md). This module requires phonopy to be installed.

`dos_stats` : this reads in density of states data via one of the interfaces and post-processes it ready for sonification.

`phonon_dos_sonifier.py`: takes the post-processed density of states data and sonifies it using Strauss. Three sonification strategies are implemented: spectral (using the Strauss spectraliser), synth (using the Strauss synth) and choral (using the strauss sampler and choral samples).

`frequency_mapping.py` : functions for mapping from phonon frequencies to audible frequencies.

`phonon_mixer.py` : takes the `.wav` files created by `phonon_dos_sonifier.py` and mixes them together with `ffmpeg`.

`cli.py` : command-line-interface for the `phonon_dos_sonifier` module. Allows the user to create `.wav` files for the spectral, synth or choral sonifications, but does not allow user to mix these together.

`run_from_yaml.py` : reads in the `sonification_batch.yml` and uses these to create and mix sonifications. 

`spec_example.yml` : example yml file which specifies how to create the sonifications and mix them together.

`utilities.py` : small utility functions.

`visualisation.py` : functions for plotting the density of states data. because seeing things is still useful.

`mods.py` : dictionaries specifying mods to the Strauss synthesiser parameters.



