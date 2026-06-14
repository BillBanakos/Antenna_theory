"""
Κεφ. 2 — Πεδιακές περιοχές (§2.2 & §4.9): αντιδραστική εγγύς, ακτινοβολούσα
εγγύς (Fresnel), μακρινή (Fraunhofer). Όρια R1, R2 ως προς D, λ, και σφάλμα φάσης δ.
"""

import numpy as np
import matplotlib.patches as mpatches
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter2Regions(ModulePage):
    TITLE = "Κεφ. 2 · Πεδιακές Περιοχές (Reactive / Fresnel / Fraunhofer)"
    SUBTITLE = ("R₁ = 0.62·√(D³/λ) (όριο αντιδραστικής)  και  R₂ = 2D²/λ (όριο far-field). "
                "Γενικευμένο όριο για σφάλμα φάσης δ.")

    DELTAS = {
        "δ = π/8  (22.5°) → 2D²/λ": np.pi / 8,
        "δ = π/16 (11.25°) → 4D²/λ": np.pi / 16,
        "δ = π/4  (45°)   → D²/λ": np.pi / 4,
        "δ = 15°": np.radians(15),
    }

    def build_controls(self, form):
        self.D_slider, _ = labeled_slider(
            form, "Μέγ. διάσταση D:", 10, 500, 100, scale=0.01, fmt="{:.2f}", suffix=" m",
            on_change=lambda v: self.update_plot())
        self.lam_slider, _ = labeled_slider(
            form, "Μήκος κύματος λ:", 1, 100, 10, scale=0.01, fmt="{:.2f}", suffix=" m",
            on_change=lambda v: self.update_plot())

        self.delta = QComboBox()
        self.delta.addItems(list(self.DELTAS.keys()))
        self.delta.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Κριτήριο σφάλματος φάσης:"), self.delta)

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"color:{theme.ACCENT}; font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "<b>Αντιδραστική:</b> E⊥H σε 90° φάση ⇒ αποθηκευμένη ενέργεια.<br>"
            "<b>Fresnel:</b> σχήμα διαγράμματος εξαρτάται από R.<br>"
            "<b>Fraunhofer:</b> σχήμα ανεξάρτητο R, κυριαρχεί πραγματική ισχύς.")

    def build_canvas(self):
        self.canvas = MplCanvas(figsize=(7.0, 6.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        D = self.D_slider.value() / 100.0
        lam = self.lam_slider.value() / 100.0
        delta = self.DELTAS[self.delta.currentText()]

        R1 = F.fresnel_inner(D, lam, delta)
        R2 = F.far_field_distance(D, lam, delta)

        ax = self.canvas.ax
        ax.clear()
        ax.set_aspect("equal")

        rmax = R2 * 1.4
        # δακτύλιοι περιοχών
        far = mpatches.Circle((0, 0), rmax, color=theme.ACCENT, alpha=0.10)
        fresnel = mpatches.Circle((0, 0), R2, color=theme.ACCENT2, alpha=0.16)
        reactive = mpatches.Circle((0, 0), R1, color=theme.ACCENT3, alpha=0.30)
        for p in (far, fresnel, reactive):
            ax.add_patch(p)
        for R, col in [(R1, theme.ACCENT3), (R2, theme.ACCENT2)]:
            ax.add_patch(mpatches.Circle((0, 0), R, fill=False, ec=col, lw=2, ls="--"))

        # κεραία στο κέντρο
        ax.plot([0, 0], [-D / 2, D / 2], color=theme.TEXT, lw=5, solid_capstyle="round")
        ax.plot(0, 0, "o", color=theme.ACCENT, ms=8)

        # ετικέτες
        ax.text(0, R1 * 0.5, "Αντιδραστική\nεγγύς", color=theme.TEXT, ha="center",
                va="center", fontsize=10, fontweight="bold")
        ax.text(0, (R1 + R2) / 2, "Fresnel\n(ακτιν. εγγύς)", color=theme.TEXT, ha="center",
                va="center", fontsize=10)
        ax.text(0, (R2 + rmax) / 2, "Fraunhofer\n(far-field)", color=theme.TEXT, ha="center",
                va="center", fontsize=10)

        # βελάκια ακτίνων
        ax.annotate("", xy=(R1, 0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=theme.ACCENT3, lw=1.6))
        ax.annotate(f"R₁={R1:.2f} m", (R1 * 0.5, -rmax * 0.08), color=theme.ACCENT3, fontsize=9)
        ax.annotate("", xy=(R2 * 0.707, R2 * 0.707), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=theme.ACCENT2, lw=1.6))
        ax.annotate(f"R₂={R2:.2f} m", (R2 * 0.4, R2 * 0.5), color=theme.ACCENT2, fontsize=9)

        ax.set_xlim(-rmax, rmax)
        ax.set_ylim(-rmax, rmax)
        ax.set_xlabel("απόσταση (m)")
        ax.set_title("Πεδιακές περιοχές γύρω από την κεραία")
        ax.grid(color=theme.GRID, alpha=0.3)
        self.canvas.refresh()

        self.readout.setText(
            f"<b>D = {D:.2f} m, λ = {lam:.2f} m, D/λ = {D/lam:.2f}</b><br>"
            f"R₁ (αντιδραστική→Fresnel) = <b>{R1:.3f} m</b><br>"
            f"R₂ (Fresnel→far-field) = <b>{R2:.3f} m</b><br>"
            f"Για δ=π/8: R₁=0.62√(D³/λ)={0.62*np.sqrt(D**3/lam):.3f},  "
            f"R₂=2D²/λ={2*D**2/lam:.3f} m")
