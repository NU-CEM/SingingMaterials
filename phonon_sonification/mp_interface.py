from dotenv import load_dotenv
import mp_api
import os
from mp_api.client import MPRester
from phonon_sonification import utilities
from pathlib import Path
import pickle

load_dotenv () # use python-dotenv library for storing secrets in a .env file in project route (or at another path that is specified here)

def gamma_frequencies_from_mp_id(mp_id):
    """return phonon frequencies (in Hz) at gamma point from for a material hosted on the Materials Project.
    Material is identified using unique ID number. Note that to use this feature you need a Materials
    Project API key (https://materialsproject.org/api)."""


    with MPRester(os.getenv('MP_API_KEY')) as mpr:
        try:
            bs = mpr.get_phonon_bandstructure_by_material_id(mp_id)
        except:
            print("this materials project entry does not appear to have phonon data")
            pass
    print("extracting frequencies for qpoint {}".format(bs.qpoints[0].cart_coords))

    phonon_frequencies = list(bs.to_pmg.bands[:,0*1E12])   # convert from THz to Hz
    phonon_frequencies = utilities.process_imaginary(phonon_frequencies)
    print("phonon frequencies are (Hz):", phonon_frequencies)

    return phonon_frequencies

def dos_data_from_mp_id(mp_id):
    """return dos data obect. This is for a material hosted on the Materials Project.
    Material is identified using unique ID number. Note that to use this feature you need a Materials
    Project API key (https://materialsproject.org/api)."""

    with MPRester(os.getenv('MP_API_KEY')) as mpr:

        try: 
            dos = mpr.get_phonon_dos_by_material_id(mp_id)
        except:
            print("this materials project entry does not appear to have phonon data")
            pass

    return dos

def get_dos_raw_mp(mp_id):
    """get the full and projected densities. Return as a nested dictionary. Arg is the materials project ID. """

    filepath = Path(f"{mp_id}_dos.pickle")
    if filepath.is_file():
        print("Fetching from existing file...")
        with open(filepath, 'rb') as handle:
            dos_dict = pickle.load(handle)
    else:
        print("Fetching from Materials Project servers...")
        dos = dos_data_from_mp_id(mp_id)

        dos_dict = {}
        dos_dict['metadata'] = {'mp_id' : mp_id}
        dos_dict['projection'] = {}
    
        frequencies = np.array(dos.frequencies)*1E12 # convert from THz to Hz
        frequencies = utilities.process_imaginary(frequencies)  
        dos_dict['metadata']['bin_width'] = frequencies[1]-frequencies[0]
        print(f"bin width is {dos_dict['metadata']['bin_width']/1E12} THz")
        
        densities = utilities.process_imaginary_dos(dos.densities,frequencies) 
        dos_dict['projection']['total'] = {'densities': densities,
                                         'frequencies': frequencies}
                
        for i,site in enumerate(dos.structure.relabel_sites().sites):
            densities = utilities.process_imaginary_dos(dos.projected_densities[i],frequencies) 
            dos_dict['projection'][site.label] = {'densities': densities,
                                                            'frequencies': frequencies} 
    
        with open(filepath, 'wb') as handle:
            pickle.dump(dos_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    return dos_dict