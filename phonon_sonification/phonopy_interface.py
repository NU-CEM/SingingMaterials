import phonopy
import numpy as np
from phonon_sonification import _CM_INV_IN_THZ, _THZ_TO_HZ, utilities

def get_dos_raw_phonopy(
    yaml_path: str,
    mp_id: str | None = None,
    mesh: tuple[int, int, int] | int = (24, 24, 24),
    freq_pitch_thz: float = _CM_INV_IN_THZ,
) -> dict:
    """Load a phonopy_params.yaml file and return projected DOS as a dict.
 
    Parameters
    ----------
    yaml_path
        Path to a phonopy summary YAML; force constants must be present.
    mesh
        q-point mesh for sampling the Brillouin zone. A scalar is broadcast
        to all three directions by phonopy.
    freq_pitch_thz
        Frequency-bin spacing in THz. Default is 1 cm^-1
        (~0.02998 THz), so ``bin_width`` is ~2.998e10 Hz in the output.
 
    Returns
    -------
    dict matching the schema above.
    """    
    phonon = phonopy.load(yaml_path)
 
    # Projected DOS needs eigenvectors and the full (non-symmetry-reduced) mesh.
    phonon.run_mesh(mesh, with_eigenvectors=True, is_mesh_symmetry=False)
    phonon.run_projected_dos(
        freq_pitch=freq_pitch_thz
    )
 
    pdos = phonon.projected_dos
    freq_thz = np.asarray(pdos.frequency_points)   # (n_freq,)
    projected = np.asarray(pdos.projected_dos)     # (n_atoms_primitive, n_freq)
 
    # Phonopy works in THz; convert to Hz for consistency with mp.
    frequencies = freq_thz * _THZ_TO_HZ
    frequencies = utilities.process_imaginary(frequencies)  
    bin_width = np.float64(frequencies[1] - frequencies[0])
 
    # Per-atom labels: count occurrences of each species in the primitive cell.
    symbols = list(phonon.primitive.symbols)
    counters: dict[str, int] = {}
    labels: list[str] = []
    for sym in symbols:
        counters[sym] = counters.get(sym, 0) + 1
        labels.append(f"{sym}_{counters[sym]}")

    # Apply imaginary-mode cleanup per atom, then rebuild total from the
    # cleaned per-atom densities so total == sum-of-atoms still holds.
    cleaned = np.stack([
        utilities.process_imaginary_dos(density, frequencies)
        for density in projected
    ])
    total_density = cleaned.sum(axis=0)

    projection: dict[str, dict[str, np.ndarray]] = {
        "total": {"densities": total_density, "frequencies": frequencies},
    }
    for label, density in zip(labels, cleaned):
        projection[label] = {"densities": density, "frequencies": frequencies}
 
    dos_dict = {
        "metadata": {"mp_id": mp_id, "bin_width": bin_width},
        "projection": projection,
    }
        
    return dos_dict