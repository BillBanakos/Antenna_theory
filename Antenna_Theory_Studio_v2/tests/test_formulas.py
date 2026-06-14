"""
Σουίτα pytest για το core/formulas.py.
Κωδικοποιεί τους ελέγχους ορθότητας ως προς τις τιμές αναφοράς του βοηθήματος
(Balanis). Εκτέλεση:  pytest -q
"""

import numpy as np
import pytest

from antenna_studio.core import formulas as F


# ----------------- Κεφ. 4: Δίπολο -----------------
@pytest.mark.parametrize("L, expected, tol", [
    (0.25, 13.7, 0.6),
    (0.5, 73.1, 1.5),
    (0.75, 372.0, 8.0),
])
def test_dipole_input_resistance(L, expected, tol):
    assert F.dipole_input_resistance(L) == pytest.approx(expected, abs=tol)


def test_dipole_full_wave_infinite():
    assert not np.isfinite(F.dipole_input_resistance(1.0))


def test_rr_infinitesimal():
    # 80π²(l/λ)²  για l/λ=0.02
    assert F.Rr_infinitesimal(0.02) == pytest.approx(80 * np.pi**2 * 0.02**2, rel=1e-9)


# ----------------- Κεφ. 2: Κατευθυντικότητα / πόλωση -----------------
def test_directivity_sin_cubed():
    th = np.linspace(1e-4, np.pi, 4000)
    U = np.sin(th) ** 3
    assert F.directivity_numerical(U, th) == pytest.approx(1.6977, abs=0.01)


def test_plf_identical_linear():
    rw = np.array([1, 0], dtype=complex)
    assert F.plf(rw, rw) == pytest.approx(1.0, abs=1e-9)


def test_plf_orthogonal_linear():
    assert F.plf(np.array([1, 0j]), np.array([0, 1j])) == pytest.approx(0.0, abs=1e-9)


def test_plf_rhcp_lhcp_zero():
    rhcp = np.array([1, -1j]) / np.sqrt(2)
    lhcp = np.array([1, 1j]) / np.sqrt(2)
    assert F.plf(rhcp, lhcp) == pytest.approx(0.0, abs=1e-9)


def test_polarization_circular():
    typ, sense = F.classify_polarization(1.0, 1.0, np.pi / 2)
    assert "Κυκλική" in typ


# ----------------- Κεφ. 6: Στοιχειοκεραίες / σύνθεση -----------------
def test_binomial_coeffs():
    assert list(F.binomial_coeffs(5)) == [1, 4, 6, 4, 1]


def test_dolph_n5_30db():
    coeffs, x0, R0 = F.dolph_tschebyscheff_coeffs(5, 30)
    assert x0 == pytest.approx(1.5873, abs=0.01)
    assert coeffs[2] == pytest.approx(3.14, abs=0.05)
    assert F.dolph_beam_broadening(R0) == pytest.approx(1.144, abs=0.02)
    assert F.dolph_dmax(x0) == pytest.approx(0.717, abs=0.02)


def test_uniform_sidelobe_level():
    th = np.linspace(0, np.pi, 4000)
    AF = F.array_factor_uniform(th, 10, 0.5, 0.0)
    assert F.sidelobe_level_db(th, AF) == pytest.approx(-13.5, abs=0.6)


def test_beta_endfire():
    # β = -kd  σε μοίρες, για d=0.25λ -> -90°
    assert F.beta_endfire(0.25, 0.0) == pytest.approx(-90.0, abs=1e-6)


# ----------------- Κεφ. 14: Patch -----------------
def test_patch_design_reference():
    d = F.patch_design(2e9, 10.2, 0.127e-2)
    assert d["W"] * 100 == pytest.approx(3.167, abs=0.01)
    assert d["eps_reff"] == pytest.approx(9.38, abs=0.02)
    assert d["L"] * 100 == pytest.approx(2.338, abs=0.01)


def test_inset_feed_monotonic():
    # Rin(y0) μειώνεται από την ακμή προς το κέντρο
    assert F.inset_resistance_curve(100, 1.0, 0.0) > F.inset_resistance_curve(100, 1.0, 0.5)


def test_circular_patch_tm210():
    a = F.CIRCULAR_MODES["TM210"] * F.C0 / (2 * np.pi * 1.9e9 * np.sqrt(10.2))
    ae = F.circular_patch_effective_radius(a, 0.127e-2, 10.2)
    assert ae * 100 == pytest.approx(2.43, abs=0.03)
