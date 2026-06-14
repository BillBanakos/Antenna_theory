"""
Κεφ. 14.8 — Κυκλικό patch (μοντέλο κοιλότητας):
ρυθμοί TM_{mn0} μέσω ριζών χ'_mn της J'_m, ενεργός ακτίνα, συχνότητα συντονισμού.
Σκαρίφημα ρυθμού πεδίου (TM110 broadside, TM210 τύπου μονοπόλου με μηδέν στο ζενίθ).
"""

import numpy as np
import matplotlib.patches as mpatches
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


SUBSTRATES = [
    ("RT/duroid 6010 (εr=10.2)", 10.2),
    ("RT/duroid 5880 (εr=2.2)", 2.2),
    ("FR-4 (εr=4.4)", 4.4),
    ("Alumina (εr=9.8)", 9.8),
]

# (όνομα, χ', πλάθος αζιμουθιακών περιόδων m, σχόλιο)
MODE_INFO = {
    "TM110": (1.8412, 1, "κυρίαρχος — μέγιστο broadside"),
    "TM210": (3.0542, 2, "τύπου μονοπόλου — μηδέν στο ζενίθ"),
    "TM010": (3.8318, 0, "αξονοσυμμετρικός"),
    "TM310": (4.2012, 3, "ανώτερος ρυθμός"),
}


class Chapter14Circular(ModulePage):
    TITLE = "Κεφ. 14.8 · Κυκλικό Patch — Ρυθμοί TM"
    SUBTITLE = ("(fr)ₘₙ₀ = χ'ₘₙ·c / (2π·aₑ·√εr).  "
                "TM110 κυρίαρχος· TM210 δίνει διάγραμμα τύπου μονοπόλου.")

    def build_controls(self, form):
        self.mode = QComboBox()
        self.mode.addItems(list(MODE_INFO.keys()))
        self.mode.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Ρυθμός:"), self.mode)

        self.sub = QComboBox()
        self.sub.addItems([s[0] for s in SUBSTRATES])
        self.sub.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Υπόστρωμα:"), self.sub)

        self.h_slider, _ = labeled_slider(
            form, "Ύψος h:", 20, 320, 127, scale=0.01, fmt="{:.2f}", suffix=" mm",
            on_change=lambda v: self.update_plot())

        self.fr_slider, _ = labeled_slider(
            form, "Επιθυμητή fr:", 5, 60, 19, scale=0.1, fmt="{:.1f}", suffix=" GHz",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel(); self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "Cavity: PEC πάνω/κάτω, PMC περιφερειακά, ρυθμοί TM.<br>"
            "Ενεργός ακτίνα aₑ > a (κροσσοί).<br>"
            "Έλεγχος βοηθήματος (TM210, εr=10.2, 1.9 GHz): a≈2.40 cm, aₑ≈2.43 cm.")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2, projection=["polar", "polar"],
                                figsize=(9.4, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        mode = self.mode.currentText()
        chi, m, comment = MODE_INFO[mode]
        eps_r = SUBSTRATES[self.sub.currentIndex()][1]
        h = self.h_slider.value() * 0.01 * 1e-3
        fr = self.fr_slider.value() * 0.1e9

        # φυσική ακτίνα αγνοώντας κροσσούς (a=ae), μετά ενεργός & διορθωμένη fr
        a = chi * F.C0 / (2 * np.pi * fr * np.sqrt(eps_r))
        a_e = F.circular_patch_effective_radius(a, h, eps_r)
        fr_corr = F.circular_patch_freq(a_e, eps_r, chi)

        a_cm = a * 100; ae_cm = a_e * 100

        # ---- 1) Κάτοψη πεδίου Ez ∝ J_m(χ' ρ/a)·cos(mφ) ----
        ax = self.canvas.axes[0]
        ax.clear()
        rho = np.linspace(0, 1, 120)
        phi = np.linspace(0, 2 * np.pi, 240)
        R, P = np.meshgrid(rho, phi)
        from scipy.special import jv
        Ez = jv(m, chi * R) * np.cos(m * P)
        Ez = Ez / np.max(np.abs(Ez))
        pc = ax.pcolormesh(P, R, Ez, cmap="RdBu_r", shading="auto", vmin=-1, vmax=1)
        ax.set_title(f"Ez ρυθμού {mode} (κάτοψη)", color=theme.TEXT, fontsize=10)
        ax.set_yticklabels([])
        ax.tick_params(colors=theme.TEXT_DIM)

        # ---- 2) Διάγραμμα ακτινοβολίας (σκαρίφημα E-plane) ----
        ax2 = self.canvas.axes[1]
        ax2.clear()
        th = np.linspace(0, np.pi, 400)
        if m == 1:      # TM110 broadside
            patt = np.cos(th) ** 0  # ~ομοιόμορφο μπρος, χρησιμοποιούμε cosθ μορφή
            patt = np.abs(np.cos(0.9 * th))
        elif m == 2:    # TM210 μηδέν στο ζενίθ (τύπου μονοπόλου)
            patt = np.abs(np.sin(2 * th)) ** 0.5
        elif m == 0:
            patt = np.abs(np.cos(th))
        else:
            patt = np.abs(np.sin(m * th))
        patt = patt / max(patt.max(), 1e-9)
        th_full = np.concatenate([th, th + np.pi])
        data = np.concatenate([patt, patt[::-1]])
        ax2.plot(th_full, data, color=theme.ACCENT, lw=2)
        ax2.fill(th_full, data, color=theme.ACCENT, alpha=0.2)
        ax2.set_theta_zero_location("N")
        ax2.set_theta_direction(-1)
        ax2.set_title("Σκαρίφημα διαγράμματος (E-plane)", color=theme.TEXT, fontsize=10)
        ax2.tick_params(colors=theme.TEXT_DIM)
        ax2.grid(color=theme.GRID)
        self.canvas.refresh()

        zenith = "μηδέν στο ζενίθ (θ=0°)" if m >= 2 else "μέγιστο broadside"
        self.readout.setText(
            f"<b>Ρυθμός {mode}:</b> χ'={chi}<br>"
            f"<b>{comment}</b><br>"
            f"<b>Φυσική ακτίνα a:</b> {a_cm:.3f} cm<br>"
            f"<b>Ενεργός aₑ:</b> {ae_cm:.3f} cm<br>"
            f"<b>fr με κροσσούς:</b> {fr_corr/1e9:.3f} GHz<br>"
            f"<b>Διάγραμμα:</b> {zenith}")
