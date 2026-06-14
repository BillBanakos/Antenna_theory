"""
Οπτικοποιητής Εννοιών Πολλαπλής Επιλογής (MCQ Concept Gallery).
Υλοποιεί ως σχήματα τις «καθοριστικές διακρίσεις & παγίδες» που ελέγχουν
οι ερωτήσεις πολλαπλής επιλογής κάθε κεφαλαίου (Κεφ. 1, 2, 4, 6, 14).
Κάθε «κάρτα» ζωγραφίζει το κανονικό σχήμα + σύντομη επεξήγηση/παγίδα.
"""

import numpy as np
import matplotlib.patches as mpatches
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar
from ..core import theme
from ..core import formulas as F


# ----------------------------------------------------------------------
# Βοηθητικά σχεδίασης κανονικών διαγραμμάτων
# ----------------------------------------------------------------------
def _polar(ax, th, r, color=theme.ACCENT, fill=True):
    th_full = np.concatenate([th, th + np.pi])
    r = r / max(r.max(), 1e-9)
    data = np.concatenate([r, r[::-1]])
    ax.plot(th_full, data, color=color, lw=2)
    if fill:
        ax.fill(th_full, data, color=color, alpha=0.2)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.tick_params(colors=theme.TEXT_DIM)
    ax.grid(color=theme.GRID)


# === ΚΕΦ. 1 ===
def c1_current(fig):
    ax = fig.add_subplot(111)
    lengths = [(0.1, "l≪λ: ~τριγωνικό"), (0.5, "l=λ/2: μέγιστο στο κέντρο"),
               (1.0, "l=λ: μηδέν στο κέντρο"), (1.5, "l=3λ/2: 3 τμήματα")]
    z = np.linspace(-0.5, 0.5, 400)
    for i, (L, lab) in enumerate(lengths):
        off = i * 2.4
        # ημιτονοειδής κατανομή I(z')=sin[k(l/2-|z'|)], z' σε λ
        k = 2 * np.pi
        zz = z * L
        I = np.abs(np.sin(k * (L / 2 - np.abs(zz))))
        ax.plot(off + I, z, color=theme.ACCENT, lw=2)
        ax.plot([off, off], [-0.5, 0.5], color=theme.TEXT_DIM, lw=3, alpha=0.5)
        ax.text(off, 0.62, lab, color=theme.ACCENT2, ha="center", fontsize=8)
    ax.set_xlim(-0.6, 9.5); ax.set_ylim(-0.7, 0.8)
    ax.set_title("Κατανομή ρεύματος I(z')=I₀·sin[k(l/2−|z'|)]",
                 color=theme.TEXT, fontsize=11)
    ax.set_yticks([]); ax.set_xticks([])


# === ΚΕΦ. 2 ===
def c2_regions(fig):
    ax = fig.add_subplot(111)
    ax.add_patch(mpatches.Circle((0, 0), 1, color=theme.ACCENT3, alpha=0.35))
    ax.add_patch(mpatches.Circle((0, 0), 2.4, fill=False, ec=theme.ACCENT2, lw=2))
    ax.add_patch(mpatches.Circle((0, 0), 4.2, fill=False, ec=theme.ACCENT, lw=2))
    ax.text(0, 0, "Αντιδραστική\nR<0.62√(D³/λ)", ha="center", va="center",
            color=theme.TEXT, fontsize=8)
    ax.text(0, 1.7, "Fresnel\n(ακτινοβ. εγγύς)", ha="center", color=theme.ACCENT2, fontsize=8)
    ax.text(0, 3.3, "Fraunhofer (far-field)\nR≥2D²/λ", ha="center",
            color=theme.ACCENT, fontsize=8)
    ax.set_xlim(-4.5, 4.5); ax.set_ylim(-4.5, 4.5); ax.set_aspect("equal")
    ax.set_title("Πεδιακές περιοχές", color=theme.TEXT, fontsize=11)
    ax.axis("off")


def c2_polarization(fig):
    axes = [fig.add_subplot(1, 3, i + 1) for i in range(3)]
    t = np.linspace(0, 2 * np.pi, 300)
    cases = [("Γραμμική\nΔφ=0", 1, 1, 0),
             ("Κυκλική\nEx=Ey, Δφ=90°", 1, 1, np.pi / 2),
             ("Ελλειπτική\nΔφ=45°", 1, 0.6, np.pi / 4)]
    for ax, (lab, ex, ey, dphi) in zip(axes, cases):
        ax.plot(ex * np.cos(t), ey * np.cos(t + dphi), color=theme.ACCENT, lw=2)
        ax.set_title(lab, color=theme.ACCENT2, fontsize=9)
        ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_aspect("equal")
        ax.axhline(0, color=theme.GRID, lw=0.6); ax.axvline(0, color=theme.GRID, lw=0.6)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Ταξινόμηση πόλωσης (αιχμή του E)", color=theme.TEXT, fontsize=11)


def c2_directivity_domains(fig):
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2, projection="polar")
    th = np.linspace(0, np.pi, 400)
    _polar(ax1, th, np.abs(np.cos(th)) ** 6, color=theme.ACCENT)
    ax1.set_title("Δέσμη-μολύβι\n→ Kraus / Tai–Pereira", color=theme.ACCENT2, fontsize=9)
    _polar(ax2, th, np.abs(np.sin(th)) ** 1.5, color=theme.ACCENT3)
    ax2.set_title("Παντοκατευθυντικό\n→ McDonald / Pozar", color=theme.ACCENT2, fontsize=9)
    fig.suptitle("Ποιος προσεγγιστικός τύπος D₀; (παγίδα!)", color=theme.TEXT, fontsize=11)


# === ΚΕΦ. 4 ===
def c4_dipole_by_length(fig):
    Ls = [0.5, 1.0, 1.25, 1.5]
    axes = [fig.add_subplot(1, 4, i + 1, projection="polar") for i in range(4)]
    th = np.linspace(1e-3, np.pi - 1e-3, 800)
    for ax, L in zip(axes, Ls):
        patt = F.finite_dipole_pattern(th, L)
        _polar(ax, th, patt)
        ax.set_title(f"l={L:g}λ", color=theme.ACCENT2, fontsize=9)
        ax.set_xticklabels([])
    fig.suptitle("Διάγραμμα διπόλου & μεταβλητότητα με το μήκος "
                 "(>1.25λ: διάσπαση λοβού)", color=theme.TEXT, fontsize=11)


def c4_image_theory(fig):
    ax = fig.add_subplot(111)
    ax.axhline(0, color=theme.ACCENT2, lw=3)  # έδαφος
    ax.text(2.6, 0.06, "PEC έδαφος", color=theme.ACCENT2, fontsize=9)
    # κατακόρυφο: +1
    ax.annotate("", xy=(-1.6, 1.2), xytext=(-1.6, 0.2),
                arrowprops=dict(arrowstyle="-|>", color=theme.ACCENT, lw=3))
    ax.annotate("", xy=(-1.6, -1.2), xytext=(-1.6, -0.2),
                arrowprops=dict(arrowstyle="-|>", color=theme.ACCENT, lw=3))
    ax.text(-1.6, 1.4, "κατακόρυφο\nείδωλο +1", ha="center", color=theme.ACCENT, fontsize=8)
    # οριζόντιο: -1
    ax.annotate("", xy=(1.0, 0.9), xytext=(2.2, 0.9),
                arrowprops=dict(arrowstyle="-|>", color=theme.ACCENT3, lw=3))
    ax.annotate("", xy=(2.2, -0.9), xytext=(1.0, -0.9),
                arrowprops=dict(arrowstyle="-|>", color=theme.ACCENT3, lw=3))
    ax.text(1.6, 1.15, "οριζόντιο\nείδωλο −1", ha="center", color=theme.ACCENT3, fontsize=8)
    ax.set_xlim(-3, 3.5); ax.set_ylim(-1.8, 1.9); ax.set_aspect("equal")
    ax.set_title("Θεωρία ειδώλων (παγίδα προσήμων): PEC → κατακόρυφο +1, οριζόντιο −1",
                 color=theme.TEXT, fontsize=10)
    ax.axis("off")


# === ΚΕΦ. 6 ===
def c6_phasing(fig):
    modes = [("Broadside β=0", 0, 0.5),
             ("End-fire β=−kd", "ef", 0.5),
             ("Hansen–Woodyard", "hw", 0.25)]
    axes = [fig.add_subplot(1, 3, i + 1, projection="polar") for i in range(3)]
    th = np.linspace(0, np.pi, 1500)
    N = 10
    for ax, (lab, mode, d) in zip(axes, modes):
        if mode == 0:
            beta = 0.0
        elif mode == "ef":
            beta = F.beta_endfire(d, 0.0)
        else:
            beta = F.beta_hansen_woodyard(d, N, 0.0)
        AF = F.array_factor_uniform(th, N, d, beta)
        _polar(ax, th, AF)
        ax.set_title(lab, color=theme.ACCENT2, fontsize=9)
        ax.set_xticklabels([])
    fig.suptitle(f"Phasing ομοιόμορφης (N={N}) — πού κοιτάζει ο λοβός",
                 color=theme.TEXT, fontsize=11)


def c6_distributions(fig):
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)
    th = np.linspace(0, np.pi, 2000)
    N, d = 7, 0.5
    AFu = F.array_factor_uniform(th, N, d, 0.0)
    AFb = F.array_factor_uniform(th, N, d, 0.0, taper=F.binomial_coeffs(N))
    coeffs, x0, R0 = F.dolph_tschebyscheff_coeffs(N, 30)
    AFd = F.array_factor_uniform(th, N, d, 0.0, taper=coeffs)
    for AF, c, lab in [(AFu, theme.ACCENT, "Ομοιόμορφη −13.5 dB"),
                       (AFb, theme.ACCENT3, "Διωνυμική −∞"),
                       (AFd, theme.ACCENT2, "Dolph −30 dB")]:
        AFn = AF / AF.max()
        AFdb = np.clip(20 * np.log10(np.maximum(AFn, 1e-4)), -50, 0) + 50
        th_full = np.concatenate([th, th + np.pi])
        data = np.concatenate([AFdb, AFdb[::-1]])
        ax1.plot(th_full, data, color=c, lw=1.8, label=lab)
    ax1.set_theta_zero_location("N"); ax1.set_theta_direction(-1)
    ax1.set_ylim(0, 50); ax1.tick_params(colors=theme.TEXT_DIM)
    ax1.grid(color=theme.GRID)
    ax1.set_title("Στάθμη πλευρικών (dB, offset+50)", color=theme.TEXT, fontsize=9)
    ax1.legend(facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
               labelcolor=theme.TEXT, fontsize=7, loc="lower center",
               bbox_to_anchor=(0.5, -0.32))
    # excitation amplitudes
    x = np.arange(N)
    w = 0.27
    ax2.bar(x - w, np.ones(N) / N, w, color=theme.ACCENT, label="Ομοιόμ.")
    ax2.bar(x, F.binomial_coeffs(N) / max(F.binomial_coeffs(N)), w,
            color=theme.ACCENT3, label="Διωνυμ.")
    ax2.bar(x + w, np.array(coeffs) / max(coeffs), w, color=theme.ACCENT2, label="Dolph")
    ax2.set_title("Πλάτη διέγερσης (tapering)", color=theme.TEXT, fontsize=9)
    ax2.set_xlabel("στοιχείο"); ax2.tick_params(colors=theme.TEXT_DIM)
    ax2.legend(facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
               labelcolor=theme.TEXT, fontsize=7)
    ax2.grid(color=theme.GRID, alpha=0.3)
    fig.suptitle("Ομοιόμορφη vs Διωνυμική vs Dolph–Tschebyscheff",
                 color=theme.TEXT, fontsize=11)


def c6_grating(fig):
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2, projection="polar")
    th = np.linspace(0, np.pi, 2000)
    N = 6
    _polar(ax1, th, F.array_factor_uniform(th, N, 0.5, 0.0), color=theme.ACCENT)
    ax1.set_title("d=λ/2: χωρίς grating", color=theme.GOOD, fontsize=9)
    ax1.set_xticklabels([])
    _polar(ax2, th, F.array_factor_uniform(th, N, 1.0, 0.0), color=theme.DANGER)
    ax2.set_title("d=λ: grating lobes!", color=theme.DANGER, fontsize=9)
    ax2.set_xticklabels([])
    fig.suptitle("Grating lobes όταν d≥λ (broadside + end-fire ταυτόχρονα)",
                 color=theme.TEXT, fontsize=11)


# === ΚΕΦ. 14 ===
def c14_slots(fig):
    ax = fig.add_subplot(111)
    ax.add_patch(mpatches.Rectangle((0, 0), 3, 2, facecolor=theme.ACCENT,
                 alpha=0.25, edgecolor=theme.ACCENT, lw=2))
    for yy in (0, 2):
        ax.plot([0, 3], [yy, yy], color=theme.ACCENT3, lw=5)
    for xx in (0, 3):
        ax.plot([xx, xx], [0, 2], color=theme.TEXT_DIM, lw=2, ls="--")
    ax.text(1.5, 2.2, "ακτινοβολούσα σχισμή #1", ha="center", color=theme.ACCENT3, fontsize=9)
    ax.text(1.5, -0.3, "ακτινοβολούσα σχισμή #2", ha="center", color=theme.ACCENT3, fontsize=9)
    ax.text(3.25, 1, "μη-ακτινοβολούσες\n(ακυρώνονται)", color=theme.TEXT_DIM,
            fontsize=8, va="center")
    ax.annotate("", xy=(0, -0.7), xytext=(3, -0.7),
                arrowprops=dict(arrowstyle="<|-|>", color=theme.ACCENT2))
    ax.text(1.5, -0.95, "L ≈ λg/2", ha="center", color=theme.ACCENT2, fontsize=9)
    ax.set_xlim(-1, 5); ax.set_ylim(-1.3, 2.6); ax.set_aspect("equal")
    ax.set_title("Ορθογώνιο patch = 2 ακτινοβολούσες + 2 μη-ακτινοβολούσες σχισμές",
                 color=theme.TEXT, fontsize=10)
    ax.axis("off")


def c14_circular_modes(fig):
    from scipy.special import jv
    axes = [fig.add_subplot(1, 2, i + 1, projection="polar") for i in range(2)]
    info = [("TM110 (χ'=1.8412) κυρίαρχος", 1), ("TM210 (χ'=3.0542) μονόπολο", 2)]
    chis = [1.8412, 3.0542]
    rho = np.linspace(0, 1, 100); phi = np.linspace(0, 2 * np.pi, 200)
    R, P = np.meshgrid(rho, phi)
    for ax, (lab, m), chi in zip(axes, info, chis):
        Ez = jv(m, chi * R) * np.cos(m * P)
        ax.pcolormesh(P, R, Ez / np.max(np.abs(Ez)), cmap="RdBu_r", shading="auto")
        ax.set_title(lab, color=theme.ACCENT2, fontsize=9)
        ax.set_yticklabels([]); ax.tick_params(colors=theme.TEXT_DIM)
    fig.suptitle("Κυκλικό patch: TM110 (broadside) vs TM210 (μηδέν στο ζενίθ)",
                 color=theme.TEXT, fontsize=11)


# ----------------------------------------------------------------------
# Κατάλογος καρτών: (κεφάλαιο, τίτλος, render_fn, επεξήγηση/παγίδα HTML)
# ----------------------------------------------------------------------
CONCEPTS = [
    ("Κεφ.1", "Κατανομή ρεύματος ανά μήκος", c1_current,
     "Ρεύμα μέγιστο στο σημείο τροφοδοσίας ⇔ l=λ/2. Δεσμίδες φορτίου απέχουν λ/2."),
    ("Κεφ.2", "Πεδιακές περιοχές", c2_regions,
     "Αντιδραστική → Fresnel → Fraunhofer (R≥2D²/λ, σφάλμα φάσης π/8)."),
    ("Κεφ.2", "Ταξινόμηση πόλωσης", c2_polarization,
     "Ίσα πλάτη +90°⇒κυκλική· 0°/180°⇒γραμμική· οτιδήποτε άλλο⇒ελλειπτική."),
    ("Κεφ.2", "Ποιος τύπος κατευθυντικότητας;", c2_directivity_domains,
     "Παγίδα: Kraus/Tai–Pereira ΜΟΝΟ για δέσμη-μολύβι. Παντοκατευθυντικό⇒McDonald/Pozar."),
    ("Κεφ.4", "Διάγραμμα διπόλου ανά μήκος", c4_dipole_by_length,
     "Αύξηση μήκους⇒στενότερη δέσμη/μεγαλύτερη D₀. Πάνω από ~1.25λ ο λοβός διασπάται."),
    ("Κεφ.4", "Θεωρία ειδώλων (πρόσημα)", c4_image_theory,
     "PEC: κατακόρυφο +1, οριζόντιο −1. PMC αντίστροφα. Grazing⇒−1 και τα δύο."),
    ("Κεφ.6", "Phasing: πού κοιτάζει ο λοβός", c6_phasing,
     "broadside β=0· end-fire β=∓kd· Hansen–Woodyard β=∓(kd+π/N), d≈λ/4."),
    ("Κεφ.6", "Κατανομές & πλευρικοί λοβοί", c6_distributions,
     "Ομοιόμορφη −13.5 dB· διωνυμική καμία (−∞)· Dolph ίσοι στην επιλεγμένη στάθμη."),
    ("Κεφ.6", "Grating lobes", c6_grating,
     "d≥λ ⇒ εμφανίζονται grating lobes. Για πλήρη σάρωση χρειάζεται d<λ/2."),
    ("Κεφ.14", "Σχισμές ορθογώνιου patch", c14_slots,
     "2 ακτινοβολούσες σχισμές (≈λg/2) αθροίζουν broadside· οι 2 πλευρικές ακυρώνονται."),
    ("Κεφ.14", "Ρυθμοί κυκλικού patch", c14_circular_modes,
     "TM110 κυρίαρχος (broadside)· TM210 διάγραμμα τύπου μονοπόλου (μηδέν στο ζενίθ)."),
]


class MCQGallery(ModulePage):
    TITLE = "Πολλαπλής Επιλογής · Οπτικοποιητής Εννοιών & Σχημάτων"
    SUBTITLE = ("Υλοποιεί ως σχήματα τις «καθοριστικές διακρίσεις & παγίδες» "
                "που ελέγχουν οι ερωτήσεις κάθε κεφαλαίου. Επίλεξε έννοια.")

    def build_controls(self, form):
        self.picker = QComboBox()
        for ch, title, _fn, _desc in CONCEPTS:
            self.picker.addItem(f"[{ch}] {title}")
        self.picker.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Έννοια / σχήμα:"), self.picker)

        self.desc = QLabel(); self.desc.setWordWrap(True)
        self.desc.setStyleSheet(
            f"font-size:13px; color:{theme.TEXT}; background:{theme.BG_BASE};"
            f"border:1px solid {theme.ACCENT}; border-radius:6px; padding:10px; margin-top:8px;")
        form.addRow(self.desc)

        self.key = QLabel(); self.key.setWordWrap(True)
        self.key.setStyleSheet(f"font-size:11px; color:{theme.TEXT_DIM}; margin-top:10px;")
        self.key.setText(
            "<b>Πώς να το χρησιμοποιήσεις:</b><br>"
            "Κάθε κάρτα υλοποιεί ένα κανονικό σχήμα/διάκριση. Διάβασε το σκίτσο, "
            "σκέψου ποια ιδιότητα ελέγχει, και επιβεβαίωσε με τη σύντομη επεξήγηση.")
        form.addRow(self.key)

    def build_canvas(self):
        self.canvas = MplCanvas(figsize=(9.6, 6.0))
        # καθαρίζουμε τον προεπιλεγμένο άξονα — οι render_fn φτιάχνουν δικούς τους
        self.canvas.fig.clf()
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        idx = self.picker.currentIndex()
        ch, title, fn, desc = CONCEPTS[idx]
        self.canvas.fig.clf()
        try:
            fn(self.canvas.fig)
        except Exception as e:  # προστασία ώστε το GUI να μη «σπάει»
            ax = self.canvas.fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Σφάλμα σχεδίασης:\n{e}", ha="center", va="center",
                    color=theme.DANGER)
            ax.axis("off")
        # σκούρο φόντο σε όλους τους νέους άξονες
        for ax in self.canvas.fig.axes:
            ax.set_facecolor(theme.BG_BASE)
        self.canvas.fig.patch.set_facecolor(theme.BG)
        self.canvas.refresh()
        self.desc.setText(f"<b>[{ch}] {title}</b><br>{desc}")
