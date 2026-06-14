"""
Κεφ. 14.5 — Σχεδιαστής ορθογώνιου patch (μοντέλο γραμμής μεταφοράς):
από fr, εr, h υπολογίζονται W, εreff, ΔL, L, G1, Rin, λg.
Σχεδίαση γεωμετρίας με τις δύο ακτινοβολούσες σχισμές + καμπύλη inset feed
Rin(y0)=Rin(0)·cos²(πy0/L).
"""

import numpy as np
import matplotlib.patches as mpatches
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


# Συνηθισμένα υποστρώματα (εr) — και ένα παράδειγμα του βοηθήματος (10.2)
SUBSTRATES = [
    ("RT/duroid 5880 (εr=2.2)", 2.2),
    ("FR-4 (εr=4.4)", 4.4),
    ("RO4350B (εr=3.66)", 3.66),
    ("Alumina (εr=9.8)", 9.8),
    ("RT/duroid 6010 (εr=10.2)", 10.2),
]


class Chapter14Patch(ModulePage):
    TITLE = "Κεφ. 14.5 · Σχεδιαστής Ορθογώνιου Patch"
    SUBTITLE = ("W = c/(2fr)·√(2/(εr+1)),  L = Leff − 2ΔL.  "
                "Δύο ακτινοβολούσες σχισμές σε απόσταση ≈λg/2.")

    def build_controls(self, form):
        self.fr_slider, _ = labeled_slider(
            form, "Συχνότητα fr:", 5, 200, 20, scale=0.1, fmt="{:.1f}", suffix=" GHz",
            on_change=lambda v: self.update_plot())

        self.sub = QComboBox()
        self.sub.addItems([s[0] for s in SUBSTRATES])
        self.sub.setCurrentIndex(4)  # 10.2 (παράδειγμα βοηθήματος)
        self.sub.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Υπόστρωμα:"), self.sub)

        self.h_slider, _ = labeled_slider(
            form, "Ύψος h:", 20, 320, 127, scale=0.01, fmt="{:.2f}", suffix=" mm",
            on_change=lambda v: self.update_plot())

        self.rtarget_slider, _ = labeled_slider(
            form, "Στόχος Rin (inset):", 30, 300, 150, fmt="{}", suffix=" Ω",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel(); self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "1 < εreff < εr (κροσσοί).<br>"
            "Rin μέγιστη στην ακμή, 0 στο κέντρο: Rin(y₀)=Rin(0)cos²(πy₀/L).<br>"
            "Έλεγχος βοηθήματος (2 GHz, εr=10.2): W≈3.17 cm, L≈2.34 cm.")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2, projection=[None, None],
                                figsize=(9.4, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        fr = self.fr_slider.value() * 0.1e9
        eps_r = SUBSTRATES[self.sub.currentIndex()][1]
        # slider→mm (val*0.01) → m
        h = self.h_slider.value() * 0.01 * 1e-3
        d = F.patch_design(fr, eps_r, h)
        W = d["W"]; L = d["L"]; Leff = d["Leff"]; dL = d["dL"]
        Rin0 = d["Rin"]

        # μετατροπή σε cm για εμφάνιση
        W_cm = W * 100; L_cm = L * 100

        # ---- 1) Γεωμετρία patch (κάτοψη) ----
        ax = self.canvas.axes[0]
        ax.clear()
        ax.add_patch(mpatches.Rectangle((0, 0), W_cm, L_cm,
                     facecolor=theme.ACCENT, alpha=0.25,
                     edgecolor=theme.ACCENT, lw=2))
        # δύο ακτινοβολούσες σχισμές (πάνω/κάτω ακμή, μήκος W)
        for yy in (0, L_cm):
            ax.plot([0, W_cm], [yy, yy], color=theme.ACCENT3, lw=4, zorder=5)
        ax.text(W_cm / 2, L_cm + L_cm * 0.06, "σχισμή #1 (ακτινοβολεί)",
                color=theme.ACCENT3, ha="center", fontsize=8)
        ax.text(W_cm / 2, -L_cm * 0.1, "σχισμή #2 (ακτινοβολεί)",
                color=theme.ACCENT3, ha="center", fontsize=8)
        # γραμμή τροφοδοσίας + inset
        y0 = F.inset_feed_position(Rin0, self.rtarget_slider.value(), L)
        y0_cm = y0 * 100
        feed_w = W_cm * 0.12
        ax.add_patch(mpatches.Rectangle((W_cm / 2 - feed_w / 2, -L_cm * 0.35),
                     feed_w, L_cm * 0.35 + y0_cm,
                     facecolor=theme.ACCENT2, alpha=0.7, edgecolor=theme.ACCENT2))
        ax.plot(W_cm / 2, y0_cm, "o", color=theme.TEXT, ms=7, zorder=6)
        ax.annotate(f"y₀={y0_cm:.2f} cm", (W_cm / 2 + feed_w, y0_cm),
                    color=theme.ACCENT2, fontsize=8, va="center")
        ax.set_xlim(-W_cm * 0.2, W_cm * 1.2)
        ax.set_ylim(-L_cm * 0.45, L_cm * 1.25)
        ax.set_aspect("equal")
        ax.set_xlabel("W (cm)"); ax.set_ylabel("L (cm)")
        ax.set_title("Γεωμετρία patch + inset feed", color=theme.TEXT, fontsize=10)
        ax.grid(color=theme.GRID, alpha=0.25)

        # ---- 2) Καμπύλη Rin(y0) ----
        ax2 = self.canvas.axes[1]
        ax2.clear()
        yv = np.linspace(0, L, 300)
        Rv = F.inset_resistance_curve(Rin0, L, yv)
        ax2.plot(yv * 100, Rv, color=theme.ACCENT, lw=2)
        ax2.axhline(self.rtarget_slider.value(), color=theme.ACCENT3, ls="--", lw=1.2,
                    label=f"στόχος {self.rtarget_slider.value()} Ω")
        ax2.axvline(y0_cm, color=theme.ACCENT2, ls=":", lw=1.2)
        ax2.plot(y0_cm, self.rtarget_slider.value(), "o", color=theme.TEXT, ms=7)
        ax2.set_xlabel("θέση εσοχής y₀ (cm)")
        ax2.set_ylabel("Rin (Ω)")
        ax2.set_title("Rin(y₀) = Rin(0)·cos²(πy₀/L)", color=theme.TEXT, fontsize=10)
        ax2.grid(color=theme.GRID, alpha=0.3)
        ax2.legend(facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
                   labelcolor=theme.TEXT, fontsize=8)
        self.canvas.refresh()

        self.readout.setText(
            f"<b>W:</b> {W_cm:.3f} cm &nbsp; <b>L:</b> {L_cm:.3f} cm<br>"
            f"<b>εreff:</b> {d['eps_reff']:.2f} &nbsp; <b>ΔL:</b> {dL*100:.4f} cm<br>"
            f"<b>Leff:</b> {Leff*100:.3f} cm &nbsp; <b>λg:</b> {d['lambda_g']*100:.2f} cm<br>"
            f"<b>G₁:</b> {d['G1']*1e3:.3f} mS &nbsp; <b>Rin(0):</b> {Rin0:.1f} Ω<br>"
            f"<b>Zc γραμμής:</b> {d['Zc']:.1f} Ω")
