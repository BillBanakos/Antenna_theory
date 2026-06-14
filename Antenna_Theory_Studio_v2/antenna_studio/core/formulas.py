"""
core/formulas.py
================
Κεντρική βιβλιοθήκη με ΟΛΟΥΣ τους τύπους του βοηθήματος (δομή Balanis).
Κάθε συνάρτηση είναι "καθαρή" (numpy in -> numpy out) ώστε να δοκιμάζεται
ανεξάρτητα από το GUI. Οι αναφορές §x.y παραπέμπουν στο PDF θεωρίας.

Περιεχόμενα:
  - Σταθερές
  - Κεφ. 2 : Διαγράμματα, κατευθυντικότητα, beamwidth, πόλωση/PLF, Friis, RCS
  - Κεφ. 4 : Δίπολα (απειροστό/πεπερασμένο/λ/2), Rr, Zin, image theory, folded
  - Κεφ. 6 : Array factor (2 & N στοιχείων), binomial, Dolph–Tschebyscheff, planar
  - Κεφ. 14: Microstrip patch (transmission-line + cavity), inset feed, circular patch
"""

import numpy as np
from scipy.special import sici  # Si, Ci ολοκληρωτικά ημίτονο/συνημίτονο

# Συμβατότητα numpy (το np.trapz καταργήθηκε στη numpy 2.x)
_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")

# ----------------------------------------------------------------------------
#  Σταθερές
# ----------------------------------------------------------------------------
C0 = 2.99792458e8          # ταχύτητα φωτός [m/s]
ETA0 = 119.9169832 * np.pi  # ≈ 376.73 Ω, κυματική αντίσταση κενού (≈377 Ω)
EULER_C = 0.5772156649     # σταθερά Euler–Mascheroni
EPS = 1e-12


def db10(x):
    """10·log10 με προστασία από log(0)."""
    return 10.0 * np.log10(np.maximum(np.asarray(x, dtype=float), EPS))


def db20(x):
    return 20.0 * np.log10(np.maximum(np.abs(np.asarray(x, dtype=float)), EPS))


def normalize(u):
    u = np.asarray(u, dtype=float)
    m = np.max(np.abs(u))
    return u / m if m > 0 else u


# ============================================================================
#  ΚΕΦΑΛΑΙΟ 2 — ΘΕΜΕΛΙΩΔΕΙΣ ΠΑΡΑΜΕΤΡΟΙ
# ============================================================================

def field_regions(D, lam):
    """§2.2 Όρια πεδιακών περιοχών.

    Returns (R1, R2): R1 = όριο αντιδραστικής/Fresnel, R2 = όριο far-field.
    R1 = 0.62*sqrt(D^3/λ),  R2 = 2*D^2/λ.
    """
    R1 = 0.62 * np.sqrt(D ** 3 / lam)
    R2 = 2.0 * D ** 2 / lam
    return R1, R2


def far_field_distance(D, lam, delta=np.pi / 8):
    """§4.9 Γενικευμένο όριο far-field για μέγιστο σφάλμα φάσης δ.

    R2 = (π / (4δ)) * D^2/λ.  Για δ=π/8 -> 2D^2/λ· για δ=π/16 -> 4D^2/λ.
    """
    return (np.pi / (4.0 * delta)) * D ** 2 / lam


def fresnel_inner(D, lam, delta=np.pi / 8):
    """§4.9 Εσωτερικό όριο Fresnel: R1 = sqrt(0.1512/δ)*sqrt(D^3/λ)."""
    return np.sqrt(0.1512 / delta) * np.sqrt(D ** 3 / lam)


# ---- Προσεγγιστικοί τύποι κατευθυντικότητας (HPBW σε μοίρες) ----------------

def directivity_kraus(hpbw1_deg, hpbw2_deg):
    """§2.5 Kraus (δέσμη-μολύβι, ένας λοβός)."""
    return 41253.0 / (hpbw1_deg * hpbw2_deg)


def directivity_tai_pereira(hpbw1_deg, hpbw2_deg):
    """§2.5 Tai & Pereira (ευρύτερες δέσμες)."""
    return 72815.0 / (hpbw1_deg ** 2 + hpbw2_deg ** 2)


def directivity_mcdonald(hpbw_deg):
    """McDonald (παντοκατευθυντικά)."""
    return 101.0 / (hpbw_deg - 0.0027 * hpbw_deg ** 2)


def directivity_pozar(hpbw_deg):
    """Pozar (παντοκατευθυντικά)."""
    return -172.4 + 191.0 * np.sqrt(0.818 + 1.0 / hpbw_deg)


def directivity_numerical(U_theta, theta):
    """§2.7 Αριθμητική κατευθυντικότητα για αξονοσυμμετρικό διάγραμμα U(θ).

    D0 = 4π Umax / ∫∫ U sinθ dθ dφ = 2 Umax / ∫ U sinθ dθ.
    """
    U = np.asarray(U_theta, dtype=float)
    th = np.asarray(theta, dtype=float)
    prad_over_2pi = _trapz(U * np.sin(th), th)
    return 2.0 * np.max(U) / max(prad_over_2pi, EPS)


def hpbw_from_pattern(theta, U):
    """Επιστρέφει HPBW (rad) από το -3dB ενός διαγράμματος ισχύος U(θ)."""
    U = normalize(U)
    half = 0.5
    imax = int(np.argmax(U))
    th_max = theta[imax]
    # ψάξε εκατέρωθεν του μεγίστου για διέλευση 0.5
    def cross(side):
        idx = range(imax, len(theta)) if side > 0 else range(imax, -1, -1)
        prev = imax
        for i in idx:
            if U[i] <= half:
                # γραμμική παρεμβολή
                t0, t1 = theta[prev], theta[i]
                u0, u1 = U[prev], U[i]
                if u0 == u1:
                    return theta[i]
                return t0 + (half - u0) * (t1 - t0) / (u1 - u0)
            prev = i
        return None
    tr = cross(+1)
    tl = cross(-1)
    if tr is None or tl is None:
        return None
    return abs(tr - tl)


# ---- Πόλωση (§2.8) ---------------------------------------------------------

def axial_ratio(Ex0, Ey0, dphi):
    """§2.8 Λόγος αξόνων AR (≥1) από πλάτη & διαφορά φάσης Δφ (rad)."""
    Ex0, Ey0 = float(Ex0), float(Ey0)
    common = Ex0 ** 2 + Ey0 ** 2
    root = np.sqrt(max(Ex0 ** 4 + Ey0 ** 4 + 2 * Ex0 ** 2 * Ey0 ** 2 * np.cos(2 * dphi), 0.0))
    OA = np.sqrt(0.5 * (common + root))
    OB = np.sqrt(max(0.5 * (common - root), 0.0))
    if OB < EPS:
        return np.inf, OA, OB
    return OA / OB, OA, OB


def tilt_angle(Ex0, Ey0, dphi):
    """§2.8 Γωνία κλίσης τ (rad) του μεγάλου άξονα ως προς x."""
    Ex0, Ey0 = float(Ex0), float(Ey0)
    denom = Ex0 ** 2 - Ey0 ** 2
    if abs(denom) < EPS:
        return np.pi / 4.0
    return np.pi / 2.0 - 0.5 * np.arctan2(2 * Ex0 * Ey0 * np.cos(dphi), denom)


def classify_polarization(Ex0, Ey0, dphi):
    """Ταξινόμηση πόλωσης + φορά περιστροφής (σύμβαση Balanis/IEEE, διάδοση +z).

    Δφ = φy - φx.  Δφ>0 -> LH/CCW,  Δφ<0 -> RH/CW.
    """
    Ex0, Ey0 = float(Ex0), float(Ey0)
    d = ((dphi + np.pi) % (2 * np.pi)) - np.pi  # wrap σε (-π, π]
    if Ex0 < EPS or Ey0 < EPS or abs(np.sin(d)) < 1e-3:
        return "Γραμμική (Linear)", "—"
    sense = "LH / CCW" if d > 0 else "RH / CW"
    if abs(Ex0 - Ey0) < 1e-3 and abs(abs(d) - np.pi / 2) < 1e-3:
        return "Κυκλική (Circular)", sense
    return "Ελλειπτική (Elliptical)", sense


def plf(rho_w, rho_a):
    """§2.8 Παράγοντας απωλειών πόλωσης PLF = |ρ̂_w · ρ̂_a*|².

    rho_w, rho_a: μιγαδικά διανύσματα (np.array). Κανονικοποιούνται εσωτερικά.
    """
    rho_w = np.asarray(rho_w, dtype=complex)
    rho_a = np.asarray(rho_a, dtype=complex)
    rw = rho_w / np.linalg.norm(rho_w)
    ra = rho_a / np.linalg.norm(rho_a)
    val = np.abs(np.vdot(ra, rw)) ** 2   # vdot συζεύγνυει το πρώτο όρισμα
    return float(val)


# ---- Friis & ραντάρ (§2.11–2.12) ------------------------------------------

def friis_pr_pt(lam, R, Gt, Gr, plf=1.0, er_t=1.0, er_r=1.0):
    """§2.11 Λόγος Pr/Pt (γραμμικά κέρδη Gt, Gr)."""
    fsl = (lam / (4 * np.pi * R)) ** 2
    return er_t * er_r * fsl * Gt * Gr * plf


def free_space_loss_db(lam, R):
    return -db10((lam / (4 * np.pi * R)) ** 2)


def radar_pr_pt(lam, sigma, Dt, Dr, Rt, Rr, plf=1.0):
    """§2.12 Εξίσωση εμβέλειας ραντάρ."""
    return sigma * Dt * Dr / (4 * np.pi) * (lam / (4 * np.pi * Rt * Rr)) ** 2 * plf


# ============================================================================
#  ΚΕΦΑΛΑΙΟ 4 — ΓΡΑΜΜΙΚΕΣ ΣΥΡΜΑΤΙΝΕΣ ΚΕΡΑΙΕΣ
# ============================================================================

def finite_dipole_pattern(theta, L_over_lambda):
    """§4.3 Κανονικοποιημένο διάγραμμα πεδίου πεπερασμένου διπόλου.

    F(θ) = [cos(kl/2·cosθ) - cos(kl/2)] / sinθ.  (L_over_lambda = l/λ)
    """
    theta = np.asarray(theta, dtype=float)
    kl2 = np.pi * L_over_lambda  # k*l/2 = (2π/λ)(l/2) = π l/λ
    s = np.sin(theta)
    s = np.where(np.abs(s) < 1e-9, 1e-9, s)
    F = (np.cos(kl2 * np.cos(theta)) - np.cos(kl2)) / s
    return np.abs(F)


def infinitesimal_dipole_pattern(theta):
    """§4.1  U ∝ sin²θ  ->  πεδίο ∝ |sinθ|."""
    return np.abs(np.sin(np.asarray(theta, dtype=float)))


def Rr_infinitesimal(L_over_lambda):
    """§4.1 Αντίσταση ακτινοβολίας απειροστού διπόλου: 80π²(l/λ)²."""
    return 80.0 * np.pi ** 2 * L_over_lambda ** 2


def Rr_small_triangular(L_over_lambda):
    """§4.2 Μικρό δίπολο (τριγωνικό ρεύμα): 20π²(l/λ)²."""
    return 20.0 * np.pi ** 2 * L_over_lambda ** 2


def dipole_radiation_resistance(L_over_lambda):
    """§4.3 Γενικός τύπος Rr (αναφορά στο ρεύμα ΜΕΓΙΣΤΟΥ), μέσω Si/Ci.

    Rr = η/2π · [ C + ln(kl) - Ci(kl)
                 + 0.5 sin(kl)(Si(2kl) - 2 Si(kl))
                 + 0.5 cos(kl)(C + ln(kl/2) + Ci(2kl) - 2 Ci(kl)) ]
    """
    kl = 2 * np.pi * L_over_lambda
    Si_kl, Ci_kl = sici(kl)
    Si_2kl, Ci_2kl = sici(2 * kl)
    term = (EULER_C + np.log(kl) - Ci_kl
            + 0.5 * np.sin(kl) * (Si_2kl - 2 * Si_kl)
            + 0.5 * np.cos(kl) * (EULER_C + np.log(kl / 2.0) + Ci_2kl - 2 * Ci_kl))
    return ETA0 / (2 * np.pi) * term


def dipole_input_resistance(L_over_lambda):
    """§4.3 Αντίσταση ΕΙΣΟΔΟΥ συντονισμένου διπόλου (αναφορά στο ρεύμα εισόδου).

    R_in = R_r,max / sin²(kl/2).  Δίνει τις κλασικές τιμές του βοηθήματος:
    λ/4 → ≈13.7 Ω,  λ/2 → 73 Ω,  3λ/4 → ≈372 Ω,  λ → ∞.
    """
    s = np.sin(np.pi * L_over_lambda)  # sin(kl/2) με kl/2 = π l/λ
    if abs(s) < 1e-6:
        return np.inf
    return dipole_radiation_resistance(L_over_lambda) / s ** 2


def vswr_from_R(Rin, Z0=50.0):
    """Συντονισμένο δίπολο: VSWR = max(Rin/Z0, Z0/Rin)."""
    return max(Rin / Z0, Z0 / Rin)


def gamma_from_Z(ZL, Z0=50.0):
    """Συντελεστής ανάκλασης Γ = (ZL - Z0)/(ZL + Z0)  (μιγαδικός)."""
    ZL = complex(ZL)
    return (ZL - Z0) / (ZL + Z0)


def vswr_from_gamma(gamma):
    g = abs(gamma)
    return (1 + g) / (1 - g) if g < 1 else np.inf


def image_array_factor(theta, h_over_lambda, vertical=True):
    """§4.7 Παράγοντας διάταξης στοιχείου + ειδώλου πάνω από PEC.

    Κατακόρυφο (είδωλο +1): AF = 2cos(kh·cosθ)
    Οριζόντιο  (είδωλο -1): AF = 2|sin(kh·cosθ)|
    (θ από την κατακόρυφο.)
    """
    kh = 2 * np.pi * h_over_lambda
    arg = kh * np.cos(np.asarray(theta, dtype=float))
    return 2 * np.abs(np.cos(arg)) if vertical else 2 * np.abs(np.sin(arg))


def folded_dipole_impedance(Zdip=complex(73, 42.5)):
    """§4.8 Αναδιπλωμένο δίπολο: 4× εμπέδηση κανονικού λ/2."""
    return 4.0 * Zdip


# ============================================================================
#  ΚΕΦΑΛΑΙΟ 6 — ΣΤΟΙΧΕΙΟΚΕΡΑΙΕΣ
# ============================================================================

def array_factor_uniform(theta, N, d_over_lambda, beta_deg, taper=None):
    """§6.2 Κανονικοποιημένο |AF| ομοιόμορφης (ή με taper) γραμμικής στοιχειοκεραίας.

    ψ = k d cosθ + β.  Με taper (πλάτη a_n) χρησιμοποιείται γενικό άθροισμα.
    """
    theta = np.asarray(theta, dtype=float)
    kd = 2 * np.pi * d_over_lambda
    beta = np.radians(beta_deg)
    psi = kd * np.cos(theta) + beta
    if taper is None:
        with np.errstate(divide="ignore", invalid="ignore"):
            num = np.sin(N * psi / 2.0)
            den = N * np.sin(psi / 2.0)
            AF = np.where(np.abs(den) < 1e-9, 1.0, num / den)
        return np.abs(AF)
    # γενικό άθροισμα με δοσμένα πλάτη (συμμετρικά γύρω από το κέντρο)
    a = np.asarray(taper, dtype=float)
    n = np.arange(N)
    centered = (n - (N - 1) / 2.0)
    AF = np.zeros_like(theta, dtype=complex)
    for an, cn in zip(a, centered):
        AF += an * np.exp(1j * cn * psi)
    return normalize(np.abs(AF))


def array_factor_two(theta, d_over_lambda, beta_deg):
    """§6.1 Δύο στοιχεία: AF = 2cos(ψ/2)."""
    kd = 2 * np.pi * d_over_lambda
    beta = np.radians(beta_deg)
    psi = kd * np.cos(np.asarray(theta, dtype=float)) + beta
    return np.abs(2 * np.cos(psi / 2.0))


def beta_broadside():
    return 0.0


def beta_endfire(d_over_lambda, theta0_deg=0.0):
    """§6.4 β = -kd (max στο 0°) ή +kd (max στο 180°)."""
    kd = 2 * np.pi * d_over_lambda
    return np.degrees(-kd if theta0_deg == 0 else +kd)


def beta_hansen_woodyard(d_over_lambda, N, theta0_deg=0.0):
    """§6.5 β = ∓(kd + π/N)."""
    kd = 2 * np.pi * d_over_lambda
    extra = np.pi / N
    return np.degrees(-(kd + extra) if theta0_deg == 0 else +(kd + extra))


def binomial_coeffs(N):
    """§6.8 Διωνυμικοί συντελεστές (γραμμή N-1 του τριγώνου Pascal)."""
    from math import comb
    return np.array([comb(N - 1, k) for k in range(N)], dtype=float)


def dolph_tschebyscheff_coeffs(N, sll_db):
    """§6.9 Συντελεστές διέγερσης Dolph–Tschebyscheff.

    Επιστρέφει (coeffs_normalized, x0, R0).  sll_db θετικός (π.χ. 30 για -30 dB).
    Υλοποίηση μέσω εξίσωσης AF = T_{N-1}(x0·cos u).
    """
    R0 = 10 ** (sll_db / 20.0)
    M = N - 1
    x0 = np.cosh(np.arccosh(R0) / M)

    # Πολυώνυμο Tschebyscheff T_M ως δυνάμεις του x (numpy.polynomial.chebyshev)
    from numpy.polynomial import chebyshev as Cheb
    # T_M(x): συντελεστές στη βάση Chebyshev = e_M
    cheb_basis = np.zeros(M + 1)
    cheb_basis[M] = 1.0
    poly_x = Cheb.cheb2poly(cheb_basis)        # T_M(x) σε δυνάμεις του x
    # Αντικατάσταση x -> x0 * t  (t = cos u):  T_M(x0 t) = Σ poly_x[k] (x0)^k t^k
    poly_t = np.array([poly_x[k] * x0 ** k for k in range(M + 1)])  # δυνάμεις του t=cos u

    # Εκφράζουμε το AF ως άθροισμα cos(m u) και ταυτίζουμε.
    # cos^k(u) -> γραμμικός συνδυασμός cos(j u).  Χτίζουμε πίνακα μετατροπής.
    # Χρησιμοποιούμε numpy για ανάπτυξη: cos^k = (1/2^k) Σ C(k,j) cos((k-2j)u)
    from math import comb
    cos_m = np.zeros(M + 1)  # συντελεστές για cos(m u), m=0..M
    for k in range(M + 1):
        ck = poly_t[k]
        if ck == 0:
            continue
        for j in range(k + 1):
            m = abs(k - 2 * j)
            coeff = comb(k, j) / (2 ** k)
            cos_m[m] += ck * coeff
    # Τα πλάτη των στοιχείων προκύπτουν από τους συντελεστές cos(m u):
    # AF(N στοιχείων) = Σ a_n cos((2n-1)u) ή cos(2(n-1)u). Εδώ απλοποιούμε:
    # για ομοιόμορφο spacing, τα μισά πλάτη ταυτίζονται με τους cos_m όρους.
    if N % 2 == 1:  # περιττά: όροι cos(0), cos(2u), cos(4u)...
        amps = []
        amps.append(cos_m[0])
        for m in range(2, M + 1, 2):
            amps.append(cos_m[m] / 2.0)
        half = np.array(amps[::-1])         # από κέντρο προς άκρο
        full = np.concatenate([half[:-1], half[::-1]])
    else:  # άρτια: όροι cos(u), cos(3u)...
        amps = []
        for m in range(1, M + 1, 2):
            amps.append(cos_m[m] / 2.0)
        half = np.array(amps[::-1])
        full = np.concatenate([half[::-1], half])
    full = np.abs(full)
    if full.max() > 0:
        full = full / full.min()  # κανονικοποίηση στα άκρα (=1)
    return full, x0, R0


def dolph_beam_broadening(R0):
    """§6.9 Παράγοντας διεύρυνσης δέσμης f."""
    inner = np.cosh(np.sqrt(np.arccosh(R0) ** 2 - np.pi ** 2))
    return 1.0 + 0.636 * (2.0 / R0 * inner) ** 2


def dolph_dmax(x0):
    """§6.9 Μέγιστη απόσταση χωρίς grating: d/λ = 1 - (1/π) cos⁻¹(1/x0)."""
    return 1.0 - (1.0 / np.pi) * np.arccos(1.0 / x0)


def uniform_directivity_broadside(N, d_over_lambda):
    """§6.6 D0 ≈ 2 N d/λ (broadside)."""
    return 2.0 * N * d_over_lambda


def uniform_directivity_endfire(N, d_over_lambda):
    """§6.6 D0 ≈ 4 N d/λ (μονοκατευθυντικό end-fire)."""
    return 4.0 * N * d_over_lambda


def sidelobe_level_db(theta, AF):
    """Στάθμη πρώτου πλευρικού λοβού (dB) από κανονικοποιημένο |AF|."""
    AF = normalize(AF)
    # βρες τοπικά μέγιστα
    peaks = []
    for i in range(1, len(AF) - 1):
        if AF[i] > AF[i - 1] and AF[i] >= AF[i + 1]:
            peaks.append(AF[i])
    peaks = sorted(peaks, reverse=True)
    if len(peaks) >= 2:
        return db20(peaks[1])
    return -np.inf


# ============================================================================
#  ΚΕΦΑΛΑΙΟ 14 — ΚΕΡΑΙΕΣ ΜΙΚΡΟΤΑΙΝΙΑΣ (PATCH)
# ============================================================================

def eps_reff(eps_r, W, h):
    """§14.4 Ενεργός διηλεκτρική σταθερά (W/h > 1)."""
    return (eps_r + 1) / 2.0 + (eps_r - 1) / 2.0 * (1 + 12 * h / W) ** -0.5


def delta_L(eps_reff_val, W, h):
    """§14.4 Επιμήκυνση ΔL λόγω κροσσών."""
    num = (eps_reff_val + 0.3) * (W / h + 0.264)
    den = (eps_reff_val - 0.258) * (W / h + 0.8)
    return 0.412 * h * num / den


def patch_design(fr_hz, eps_r, h_m):
    """§14.5 Πλήρης σχεδίαση ορθογώνιου patch.

    Returns dict: W, eps_reff, Leff, dL, L, Zc, lambda0, lambda_g, Rin, G1.
    """
    lam0 = C0 / fr_hz
    W = C0 / (2 * fr_hz) * np.sqrt(2.0 / (eps_r + 1))
    ereff = eps_reff(eps_r, W, h_m)
    Leff = C0 / (2 * fr_hz * np.sqrt(ereff))
    dL = delta_L(ereff, W, h_m)
    L = Leff - 2 * dL
    lam_g = lam0 / np.sqrt(ereff)
    # Αγωγιμότητα σχισμής (προσέγγιση W >> λ0 ή W << λ0)
    if W / lam0 < 0.35:
        G1 = (1.0 / 90.0) * (W / lam0) ** 2
    else:
        G1 = (1.0 / 120.0) * (W / lam0)
    Rin = 1.0 / (2.0 * G1)
    # Χαρακτηριστική εμπέδηση γραμμής (W/h≥1)
    if W / h_m >= 1:
        Zc = 120 * np.pi / (np.sqrt(ereff) * (W / h_m + 1.393 + 0.667 * np.log(W / h_m + 1.444)))
    else:
        Zc = 60 / np.sqrt(ereff) * np.log(8 * h_m / W + W / (4 * h_m))
    return dict(lambda0=lam0, W=W, eps_reff=ereff, Leff=Leff, dL=dL, L=L,
                lambda_g=lam_g, G1=G1, Rin=Rin, Zc=Zc)


def inset_feed_position(Rin0, R_target, L):
    """§14.5 Θέση εσοχής y0 ώστε Rin(y0)=R_target.

    Rin(y0) = Rin0·cos²(π y0 / L)  ->  y0 = (L/π) acos( sqrt(R_target/Rin0) ).
    """
    ratio = np.clip(R_target / Rin0, 0.0, 1.0)
    return L / np.pi * np.arccos(np.sqrt(ratio))


def inset_resistance_curve(Rin0, L, y0):
    """Καμπύλη Rin(y0) = Rin0·cos²(π y0/L)."""
    y0 = np.asarray(y0, dtype=float)
    return Rin0 * np.cos(np.pi * y0 / L) ** 2


def cavity_resonant_freq(eps_r, L, W, h, m=0, n=1, p=0):
    """§14.6 Συχνότητα συντονισμού ρυθμού TM_{mnp} (διαστάσεις h,L,W κατά x,y,z)."""
    k = np.sqrt((m * np.pi / h) ** 2 + (n * np.pi / L) ** 2 + (p * np.pi / W) ** 2)
    return C0 / (2 * np.pi * np.sqrt(eps_r)) * k


def circular_patch_effective_radius(a, h, eps_r):
    """§14.8 Ενεργός ακτίνα κυκλικού patch."""
    return a * np.sqrt(1 + 2 * h / (np.pi * a * eps_r) * (np.log(np.pi * a / (2 * h)) + 1.7726))


def circular_patch_freq(a_e, eps_r, chi_prime):
    """§14.8 Συχνότητα συντονισμού κυκλικού patch (ρυθμός με ρίζα χ'_mn)."""
    return chi_prime * C0 / (2 * np.pi * a_e * np.sqrt(eps_r))


# Ρίζες χ'_mn της J'_m (από το βοήθημα)
CIRCULAR_MODES = {
    "TM110": 1.8412,
    "TM210": 3.0542,
    "TM010": 3.8318,
    "TM310": 4.2012,
}
