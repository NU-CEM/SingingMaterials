import numpy as np

from phonon_sonification import utilities


def test_process_imaginary_removes_non_positive():
    result = utilities.process_imaginary([-2.0, -1.0, 0.0, 1.0, 2.0])
    np.testing.assert_array_equal(result, [1.0, 2.0])


def test_process_imaginary_dos_keeps_densities_aligned():
    raw_frequencies = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
    densities = np.array([10, 20, 30, 40, 50, 60])
    frequencies = utilities.process_imaginary(raw_frequencies)
    cleaned = utilities.process_imaginary_dos(densities, raw_frequencies)
    np.testing.assert_array_equal(frequencies, [1.0, 2.0, 3.0])
    np.testing.assert_array_equal(cleaned, [40, 50, 60])


def test_format_duration_for_strauss():
    assert utilities.format_duration_for_strauss(75) == "1m 15s"
    assert utilities.format_duration_for_strauss(10.0) == "0m 10s"
