"""
Κεφ. 2 — Εξίσωση Friis & εμβέλεια ραντάρ (§2.11–2.12).
Διαδραστικός υπολογισμός Pr/Pt ως προς απόσταση, με free-space loss,
αναντιστοιχία, PLF και (για ραντάρ) RCS.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter2Friis(ModulePage):
    TITLE = "Κεφ. 2 · Εξίσωση Friis & Εμβέλεια Ραντάρ"
    SUBTITLE = ("Friis: Pr/Pt = (λ/4πR)²·G₀t·G₀r·PLF.  "
                "Ραντάρ: διπλή διαδρομή με ενεργό διατομή σ (RCS).")

    def build_controls(self, form):
        self.mode = QComboBox()
        self.mode.addItems(["Friis (απευθείας ζεύξη)", "Ραντάρ (με RCS)"])
        self.mode.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Λειτουργία:"), self.mode)

        self.freq, _ = labeled_slider(
            form, "Συχνότητα f:", 1, 60, 30, scale=0.1, fmt="{:.1f}", suffix=" GHz",
            on_change=lambda v: self.update_plot())
        self.gt, _ = labeled_slider(
            form, "Κέρδος Tx G₀t:", 0, 40, 10, fmt="{}", suffix=" dBi",
            on_change=lambda v: self.update_plot())
        self.gr, _ = labeled_slider(
            form, "Κέρδος Rx G₀r:", 0, 40, 10, fmt="{}", suffix=" dBi",
            on_change=lambda v: self.update_plot())
        self.plf_s, _ = labeled_slider(
            form, "PLF:", 0, 100, 100, scale=0.01, fmt="{:.2f}",
            on_change=lambda v: self.update_plot())
        self.rcs, _ = labeled_slider(
            form, "RCS σ:", 0, 100, 10, scale=0.1, fmt="{:.1f}", suffix=" m²",
            on_change=lambda v: self.update_plot())
        self.pt, _ = labeled_slider(
            form, "Ισχύς Tx P_t:", 0, 100, 10, fmt="{}", suffix=" W",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)
        self.add_theory(
            "Free-space loss = (λ/4πR)².  "
            "Στο ραντάρ η εξάρτηση γίνεται 1/R⁴ (διπλή διαδρομή).")

    def build_canvas(self):
        self.canvas = MplCanvas(figsize=(7.4, 5.6))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        f = self.freq.value() * 0.1e9
        lam = F.C0 / f
        Gt = 10 ** (self.gt.value() / 10)
        Gr = 10 ** (self.gr.value() / 10)
        plf = self.plf_s.value() / 100.0
        sigma = self.rcs.value() * 0.1
        Pt = self.pt.value()
        radar = self.mode.currentIndex() == 1

        R = np.linspace(1, 5000, 1000)
        if radar:
            ratio = F.radar_pr_pt(lam, sigma, Gt, Gr, R, R, plf)
        else:
            ratio = F.friis_pr_pt(lam, R, Gt, Gr, plf)
        Pr = Pt * ratio

        ax = self.canvas.ax
        ax.clear()
        ax.semilogy(R, Pr, color=theme.ACCENT, lw=2.2)
        ax.set_xlabel("Απόσταση R (m)")
        ax.set_ylabel("Λαμβανόμενη ισχύς P_r (W)")
        ax.set_title("Friis / Ραντάρ — P_r συναρτήσει της απόστασης")
        ax.grid(True, which="both", color=theme.GRID, alpha=0.35)

        # δείκτης στα 1000 m
        R0 = 1000.0
        if radar:
            p0 = Pt * F.radar_pr_pt(lam, sigma, Gt, Gr, R0, R0, plf)
        else:
            p0 = Pt * F.friis_pr_pt(lam, R0, Gt, Gr, plf)
        ax.plot(R0, p0, "o", color=theme.ACCENT3, ms=9)
        ax.annotate(f"R=1km\nP_r={p0:.2e} W", (R0, p0), color=theme.ACCENT3,
                    fontsize=9, xytext=(R0 * 1.05, p0 * 3))
        self.canvas.refresh()

        fsl = F.free_space_loss_db(lam, R0)
        slope = "1/R⁴" if radar else "1/R²"
        self.readout.setText(
            f"<b>λ = {lam*100:.2f} cm</b> (f={f/1e9:.1f} GHz)<br>"
            f"Free-space loss @1km = <b>{fsl:.1f} dB</b><br>"
            f"P_r @1km = <b>{p0:.3e} W</b> = {10*np.log10(p0/1e-3):.1f} dBm<br>"
            f"Εξάρτηση: <b>{slope}</b>")
