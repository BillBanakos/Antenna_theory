"""
Κεφ. 6 — Σύνθεση στοιχειοκεραιών (§6.7–6.9):
σύγκριση Ομοιόμορφης vs Διωνυμικής (binomial) vs Dolph–Tschebyscheff,
με τα πλάτη διέγερσης, στάθμη πλευρικών και HPBW.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QSpinBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter6Synthesis(ModulePage):
    TITLE = "Κεφ. 6 · Σύνθεση — Ομοιόμορφη vs Διωνυμική vs Dolph–Tschebyscheff"
    SUBTITLE = ("Ομοιόμορφη: μικρότερο HPBW, πλευρικοί −13.5 dB.  Διωνυμική: κανένας "
                "πλευρικός.  Dolph: βέλτιστο (ίσοι πλευρικοί στη ζητούμενη στάθμη).")

    def build_controls(self, form):
        self.N = QSpinBox(); self.N.setRange(3, 21); self.N.setValue(7)
        self.N.valueChanged.connect(self.update_plot)
        form.addRow(QLabel("Αριθμός στοιχείων N:"), self.N)

        self.d_slider, _ = labeled_slider(
            form, "Απόσταση d/λ:", 25, 100, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())
        self.sll_slider, _ = labeled_slider(
            form, "Στάθμη πλευρ. Dolph:", 15, 60, 30, fmt="−{}", suffix=" dB",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "Dolph–Tschebyscheff: για δεδομένη στάθμη πλευρικών δίνει το <b>μικρότερο "
            "δυνατό HPBW</b>. Τάξη πολυωνύμου = N−1. Συντελεστές από T_{N−1}.")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=2, ncols=1, figsize=(8.0, 6.2))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        N = self.N.value()
        d = self.d_slider.value() / 100.0
        sll = self.sll_slider.value()

        th = np.linspace(0, np.pi, 2000)
        uniform = F.array_factor_uniform(th, N, d, 0.0)
        binom_c = F.binomial_coeffs(N)
        binomial = F.array_factor_uniform(th, N, d, 0.0, taper=binom_c)
        dolph_c, x0, R0 = F.dolph_tschebyscheff_coeffs(N, sll)
        dolph = F.array_factor_uniform(th, N, d, 0.0, taper=dolph_c)

        ax1, ax2 = self.canvas.axes
        ax1.clear()
        for data, col, lab in [(uniform, theme.ACCENT, "Ομοιόμορφη"),
                               (binomial, theme.ACCENT2, "Διωνυμική"),
                               (dolph, theme.ACCENT3, f"Dolph −{sll}dB")]:
            db = np.clip(20 * np.log10(np.maximum(data / data.max(), 1e-4)), -50, 0)
            ax1.plot(np.degrees(th), db, color=col, lw=2, label=lab)
        ax1.axhline(-sll, color=theme.TEXT_DIM, lw=1, ls=":")
        ax1.set_xlabel("θ (μοίρες)"); ax1.set_ylabel("|AF| (dB)")
        ax1.set_ylim(-50, 2); ax1.set_xlim(0, 180)
        ax1.set_title("Παράγοντες διάταξης (broadside)", color=theme.TEXT, fontsize=10)
        ax1.legend(facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
                   labelcolor=theme.TEXT, fontsize=8)
        ax1.grid(color=theme.GRID, alpha=0.35)

        # πλάτη διέγερσης (stem)
        ax2.clear()
        n = np.arange(N)
        w = 0.25
        ax2.bar(n - w, np.ones(N) / 1, w, color=theme.ACCENT, label="Ομοιόμορφη")
        ax2.bar(n, binom_c / binom_c.max(), w, color=theme.ACCENT2, label="Διωνυμική")
        ax2.bar(n + w, dolph_c / dolph_c.max(), w, color=theme.ACCENT3, label="Dolph")
        ax2.set_xlabel("στοιχείο n"); ax2.set_ylabel("σχετικό πλάτος")
        ax2.set_title("Πλάτη διέγερσης (κανονικοποιημένα)", color=theme.TEXT, fontsize=10)
        ax2.legend(facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
                   labelcolor=theme.TEXT, fontsize=8)
        ax2.grid(axis="y", color=theme.GRID, alpha=0.35)
        self.canvas.refresh()

        def hp(data):
            U = (data / data.max()) ** 2
            h = F.hpbw_from_pattern(th, U)
            return np.degrees(h) if h else np.nan
        f_factor = F.dolph_beam_broadening(R0)
        self.readout.setText(
            f"<b>HPBW</b> — Ομοιόμορφη: {hp(uniform):.1f}° · "
            f"Διωνυμική: {hp(binomial):.1f}° · Dolph: {hp(dolph):.1f}°<br>"
            f"<b>Dolph x₀ =</b> {x0:.4f},  beam-broadening f = {f_factor:.3f}<br>"
            f"<b>Συντελεστές Dolph:</b> {', '.join(f'{c:.2f}' for c in dolph_c)}<br>"
            f"<b>Διωνυμικοί (Pascal):</b> {', '.join(f'{int(c)}' for c in binom_c)}")
