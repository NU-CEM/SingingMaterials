import numpy as np
import pandas as pd
import math
import scipy
from scipy import constants
from phonon_sonification import mp_interface, phonopy_interface

def dos_stats_analysis(mp_id=None,phonopy_filename=None,temp=None):
    """for each entry in a dos_dict, calculate the integrated dos, the phonon band centre, the quantiles and the IQR and of the dos distribution in Hz (discounting any negative frequencies) and add these to the nested dicts. The dos is optionally weighted by Bose Einstein occupation at a specified temp. DOS can be gotten from the materials project (mp_id) or from a phonopy summary file from the phonondb database (phonopy_filename)."""
    
    if temp and 0 in temp:
        print ("cannot calculate stats for 0K")
        temp.remove(0)
    if mp_id:    
        dos_dict = mp_interface.get_dos_raw_mp(mp_id)
    elif phonopy_filename:
        dos_dict = phonopy_interface.get_dos_raw_phonopy(phonopy_filename)
    else:
        raise ValueError('You must specify a dos data source (mp_id or phonopy_filename)')
    for site in dos_dict['projection']:
        site_dict = dos_dict['projection'][site]
        site_dict['stats'] = {}
        site_dict['stats']['athermal'] = {}
        densities = site_dict['densities']
        f = site_dict['frequencies']
        site_dict['stats']['athermal']['band_centre'] = phonon_band_centre(f,densities)
        site_dict['stats']['athermal']['integrated_dos'] = integrated_dos(f,densities)
        site_dict['stats']['athermal']['quantile_25'] = weighted_quantile(f, densities, 0.25)
        site_dict['stats']['athermal']['quantile_75'] = weighted_quantile(f, densities, 0.75)
        site_dict['stats']['athermal']['IQR'] = phonon_dos_IQR(f,densities)
        site_dict['stats']['athermal']['shannon_entropy'] = phonon_shannon_entropy(f,densities)
        site_dict['stats']['athermal']['densities'] = densities
        
        if temp:
            site_dict['stats']['thermal'] = {}
            if not hasattr(temp, '__iter__'):
                temp = [temp]    # if single temp provided as scalar, convert it to iterable list
            for t in temp:
                densities_scaled = scale_by_occupation(densities, f, t)
                site_dict['stats']['thermal'][str(t)] = {}
                site_dict['stats']['thermal'][str(t)]['band_centre'] = phonon_band_centre(f,densities_scaled)
                site_dict['stats']['thermal'][str(t)]['integrated_dos'] = integrated_dos(f,densities_scaled)
                site_dict['stats']['thermal'][str(t)]['quantile_25'] = weighted_quantile(f, densities_scaled, 0.25)
                site_dict['stats']['thermal'][str(t)]['quantile_75'] = weighted_quantile(f, densities_scaled, 0.75)
                site_dict['stats']['thermal'][str(t)]['IQR'] = phonon_dos_IQR(f,densities_scaled)
                site_dict['stats']['thermal'][str(t)]['shannon_entropy'] = phonon_shannon_entropy(f,densities)
                site_dict['stats']['thermal'][str(t)]['densities'] = densities_scaled

    return dos_dict

def dos_dict_to_dataframe(dos_dict):
    """convert the nested dictionary to a pandas dataframe"""
    rows = []

    mp_id = dos_dict["metadata"]["mp_id"]

    for site, site_data in dos_dict["projection"].items():
        stats = site_data["stats"]

        # athermal row
        row_base = {
            "mp_id": mp_id,
            "site": site,
            "temperature": None
        }

        for key, value in stats["athermal"].items():
            row_base[key] = value

        rows.append(row_base)

        # thermal rows
        if "thermal" in stats:
            for T, values in stats["thermal"].items():
                row = {
                    "mp_id": mp_id,
                    "site": site,
                    "temperature": float(T)
                }
                row.update(values)
                rows.append(row)

    return pd.DataFrame(rows)

def phonon_shannon_entropy(f,dos):
    p = dos / np.sum(dos)  # normalise to give a probability distribution
    p_nonzero = p[p > 0]  # mask out zero probs. this is legit because they are zero in the summation anyhow
    return np.sum(p_nonzero*np.log(p_nonzero))
    
def phonon_band_centre(f,dos):
    """for each particular chemical species, get the phonon band centre in Hz (discounting any negative frequencies). Return as a dictionary with species string as key."""
    return scipy.integrate.simpson(dos*f,f)/scipy.integrate.simpson(dos,f)
    
def integrated_dos(f,dos):
    """for each particular chemical species, get the integrated dos (discounting any negative frequencies). Return as a dictionary with species string as key."""
    return scipy.integrate.simpson(dos,f)

def phonon_dos_IQR(f,dos):
    """return the inter-quartile range of the dos distribution"""    
    return weighted_quantile(f, dos, 0.75) - weighted_quantile(f, dos, 0.25)
    
def bose_einstien_distribution(energy,temperature):
    return 1 / (math.exp(energy/(constants.Boltzmann*temperature)) - 1)

def frequency_to_energy(frequency):
    """convert frequency in Hz to energy in joules"""
    energy = constants.h*frequency
    return energy

def scale_by_occupation(densities, phonon_frequencies, temperature):
    """Re-scale the density by the Bose Einstein occupation factor for a state with energy h*frequency at specified temperature."""
    BE_occupations = np.array([bose_einstien_distribution(frequency_to_energy(frequency),temperature) 
                           for frequency in phonon_frequencies])

    # scale by occupation expressed as a fraction of the total occupation
    scaled_densities = densities*BE_occupations

    return scaled_densities

def weighted_quantile(values, weights, quantile):
    """
    Compute a weighted quantile of discrete data.
    
    values   : array-like data points
    weights  : array-like weights (same length as values)
    quantile : float in [0,1] (e.g. 0.25, 0.75)
    """
    values = np.asarray(values)
    weights = np.asarray(weights)

    # sort by values
    sorter = np.argsort(values)
    values = values[sorter]
    weights = weights[sorter]

    # cumulative distribution
    cum_weights = np.cumsum(weights)
    cum_weights /= cum_weights[-1]

    return np.interp(quantile, cum_weights, values)

