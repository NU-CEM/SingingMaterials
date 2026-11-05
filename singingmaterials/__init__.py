__version__ = "0.1.0"

# 1 cm^-1 expressed in THz (= speed of light in cm/s divided by 1e12).
# This is the default bin width for the dos when read from phonopy yaml 
_CM_INV_IN_THZ = 2.99792458e10 / 1e12  # ≈ 0.0299792458 THz
 
# Conversion factor THz -> Hz.
_THZ_TO_HZ = 1.0e12

def __getattr__(name):
    # imported on demand, so that the data and statistics modules can be used without Strauss installed.
    if name == "PhononDOSSonifier":
        from singingmaterials.phonon_dos_sonifier import PhononDOSSonifier
        return PhononDOSSonifier
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
