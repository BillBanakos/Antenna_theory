"""
Κεφ. 6 — Αρχή Πολλαπλασιασμού Διαγραμμάτων (§6.3):
Συνολικό διάγραμμα = Διάγραμμα στοιχείου × Παράγοντας διάταξης (AF).
Δείχνει ταυτόχρονα τα τρία διαγράμματα και πώς το στοιχείο «φιλτράρει» τους
λοβούς του AF (π.χ. καταστολή grating lobes από το στοιχείο).
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox, QSpinBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter6PatternMult(ModulePage):
    TITLE = "Κεφ. 6.3 · Αρχή Πολλαπλασιασμού Διαγραμμάτων"
    SUBTITLE = ("Συνολικό = Στοιχείο × AF.  Το διάγραμμα του στοιχείου διαμορφώνει "
                "(και μπορεί να καταστείλει) τους λοβούς του παράγοντα διάταξης.")

    ELEMENTS = ["Ισοτροπικό", "Απειροστό δίπολο (sinθ)", "Ημικυματικό λ/2", "cosθ"]
    MODES = ["Broadside (β=0)", "End-fire (β=−kd)", "Χειροκίνητη φάση β"]

    def build_controls(self, form):
        self.elem = QComboBox(); self.elem.addItems(self.ELEMENTS)
        self.elem.setCurrentIndex(2)
        self.elem.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Στοιχείο:"), self.elem)

        self.N = QSpinBox(); self.N.setRange(2, 24); self.N.setValue(6)
        self.N.valueChanged.connect(self.update_plot)
        form.addRow(QLabel("Στοιχεία N:"), self.N)

        self.mode = QComboBox(); self.mode.addItems(self.MODES)
        self.mode.currentIndexChanged.connect(self._mode_changed)
        form.addRow(QLabel("Φάση:"), self.mode)

        self.d_slider, _ = labeled_slider(
            form, "Απόσταση d/λ:", 5, 200, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())
        self.beta_slider, _ = labeled_slider(
            form, "Φάση β:", -360, 360, 0, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())
        self.beta_slider.setEnabled(False)

        self.readout = QLabel(); self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_export_button(self._export)
        self.add_theory(
            "Συνολικό(θ) = |EF(θ)| · |AF(θ)|.<br>"
            "Ισοτροπικό στοιχείο ⇒ συνολικό = AF.<br>"
            "Κατευθυντικό στοιχείο ⇒ καταστέλλει λοβούς εκτός της δέσμης του "
            "(π.χ. μειώνει grating lobes).")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=3, projection=["polar", "polar", "polar"],
                                figsize=(11.4, 4.6))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def _mode_changed(self):
        self.beta_slider.setEnabled(self.mode.currentIndex() == 2)
        self.update_plot()

    def _element_pattern(self, theta):
        idx = self.elem.currentIndex()
        if idx == 0:
            return np.ones_like(theta)
        if idx == 1:
            return np.abs(np.sin(theta))
        if idx == 2:
            s = np.where(np.abs(np.sin(theta)) < 1e-9, 1e-9, np.sin(theta))
            return np.abs(np.cos(np.pi / 2 * np.cos(theta)) / s)
        return np.abs(np.cos(theta))

    def _beta(self, d):
        idx = self.mode.currentIndex()
        if idx == 0:
            return 0.0
        if idx == 1:
            return F.beta_endfire(d, 0.0)
        return self.beta_slider.value()

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        N = self.N.value()
        d = self.d_slider.value() / 100.0
        beta = self._beta(d)
        if self.mode.currentIndex() != 2:
            self.beta_slider.blockSignals(True)
            self.beta_slider.setValue(int(np.clip(beta, -360, 360)))
            self.beta_slider.blockSignals(False)

        th = np.linspace(0, np.pi, 2000)
        EF = self._element_pattern(th); EF = EF / max(EF.max(), 1e-9)
        AF = F.array_factor_uniform(th, N, d, beta); AF = AF / max(AF.max(), 1e-9)
        TOT = EF * AF; TOT = TOT / max(TOT.max(), 1e-9)

        titles = ["Στοιχείο  EF(θ)", "Παράγοντας AF(θ)", "Συνολικό  EF·AF"]
        colors = [theme.ACCENT4, theme.ACCENT2, theme.ACCENT]
        for ax, data, ttl, col in zip(self.canvas.axes, [EF, AF, TOT], titles, colors):
            ax.clear()
            th_full = np.concatenate([th, th + np.pi])
            dd = np.concatenate([data, data[::-1]])
            ax.plot(th_full, dd, color=col, lw=2)
            ax.fill(th_full, dd, color=col, alpha=0.2)
            ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
            ax.set_ylim(0, 1)
            ax.set_facecolor(theme.BG_BASE)
            ax.tick_params(colors=theme.TEXT_DIM)
            ax.grid(color=theme.GRID)
            ax.set_title(ttl, color=theme.TEXT, fontsize=10)
            ax.set_xticklabels([])
        self.canvas.refresh()

        sll_af = F.sidelobe_level_db(th, AF)
        sll_tot = F.sidelobe_level_db(th, TOT)
        imax = int(np.argmax(TOT))
        self.readout.setText(
            f"<b>Μέγιστο συνολικού:</b> θ = {np.degrees(th[imax]):.1f}°<br>"
            f"<b>Πλευρικός AF:</b> {sll_af:.1f} dB<br>"
            f"<b>Πλευρικός συνολικού:</b> {sll_tot:.1f} dB<br>"
            f"<span style='color:{theme.GOOD}'>Το στοιχείο μεταβάλλει τους πλευρικούς "
            f"κατά {sll_tot - sll_af:+.1f} dB</span>")

    def _export(self):
        th = np.linspace(0, np.pi, 2000)
        EF = self._element_pattern(th); EF /= max(EF.max(), 1e-9)
        d = self.d_slider.value() / 100.0
        AF = F.array_factor_uniform(th, self.N.value(), d, self._beta(d)); AF /= max(AF.max(), 1e-9)
        TOT = EF * AF; TOT /= max(TOT.max(), 1e-9)
        rows = list(zip(np.degrees(th), EF, AF, TOT))
        return ["theta_deg", "EF", "AF", "Total"], rows
