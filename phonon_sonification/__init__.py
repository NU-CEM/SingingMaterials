__version__ = "0.1.0"

# 1 cm^-1 expressed in THz (= speed of light in cm/s divided by 1e12).
# This is the default bin width for the dos when read from phonopy yaml 
_CM_INV_IN_THZ = 2.99792458e10 / 1e12  # ≈ 0.0299792458 THz
 
# Conversion factor THz -> Hz.
_THZ_TO_HZ = 1.0e12

# imported after the constants above, as the submodules read them from this package.
from phonon_sonification.phonon_dos_sonifier import PhononDOSSonifier

__all__ = ["PhononDOSSonifier", "__version__"]
