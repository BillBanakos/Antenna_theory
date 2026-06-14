"""
Κεφ. 6 — Ομοιόμορφη γραμμική στοιχειοκεραία N στοιχείων (§6.1–6.6):
beamsteering μέσω προοδευτικής φάσης β, broadside / end-fire / Hansen–Woodyard,
στάθμη πλευρικών, μηδενισμοί, κατευθυντικότητα.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox, QSpinBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter6Array(ModulePage):
    TITLE = "Κεφ. 6 · Ομοιόμορφη Στοιχειοκεραία — Beamsteering"
    SUBTITLE = ("AF = (1/N)·sin(Nψ/2)/sin(ψ/2),  ψ = kd·cosθ + β.  "
                "Επιλέξτε τρόπο φάσης ή στρέψτε χειροκίνητα τον λοβό.")

    MODES = ["Χειροκίνητη φάση β", "Broadside (β=0)", "End-fire (β=∓kd)",
             "Hansen–Woodyard"]

    def build_controls(self, form):
        self.N = QSpinBox(); self.N.setRange(2, 32); self.N.setValue(8)
        self.N.valueChanged.connect(self.update_plot)
        form.addRow(QLabel("Αριθμός στοιχείων N:"), self.N)

        self.mode = QComboBox(); self.mode.addItems(self.MODES)
        self.mode.currentIndexChanged.connect(self._mode_changed)
        form.addRow(QLabel("Τρόπος φάσης:"), self.mode)

        self.d_slider, _ = labeled_slider(
            form, "Απόσταση d/λ:", 5, 200, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())
        self.beta_slider, _ = labeled_slider(
            form, "Προοδευτική φάση β:", -360, 360, 0, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "Πλευρικός λοβός ομοιόμορφης ≈ −13.5 dB.<br>"
            "End-fire δίνει ~2× κατευθυντικότητα από broadside (ίδιο N).<br>"
            "d=λ ⇒ grating lobes (broadside + end-fire ταυτόχρονα).")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2,
                                projection=["polar", None], figsize=(8.8, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def _mode_changed(self):
        self.beta_slider.setEnabled(self.mode.currentIndex() == 0)
        self.update_plot()

    def _beta(self):
        N = self.N.value()
        d = self.d_slider.value() / 100.0
        idx = self.mode.currentIndex()
        if idx == 0:
            return self.beta_slider.value()
        if idx == 1:
            return 0.0
        if idx == 2:
            return F.beta_endfire(d, 0.0)
        return F.beta_hansen_woodyard(d, N, 0.0)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        N = self.N.value()
        d = self.d_slider.value() / 100.0
        beta = self._beta()
        if self.mode.currentIndex() != 0:
            self.beta_slider.blockSignals(True)
            self.beta_slider.setValue(int(np.clip(beta, -360, 360)))
            self.beta_slider.blockSignals(False)

        th = np.linspace(0, np.pi, 2000)
        AF = F.array_factor_uniform(th, N, d, beta)
        AF = AF / max(AF.max(), 1e-9)

        # --- πολικό (dB) ---
        axp = self.canvas.axes[0]
        axp.clear()
        AFdb = np.clip(20 * np.log10(np.maximum(AF, 1e-4)), -40, 0) + 40
        th_full = np.concatenate([th, th + np.pi])
        data = np.concatenate([AFdb, AFdb[::-1]])
        axp.plot(th_full, data, color=theme.ACCENT, lw=2)
        axp.fill(th_full, data, color=theme.ACCENT, alpha=0.2)
        axp.set_theta_zero_location("N")
        axp.set_theta_direction(-1)
        axp.set_ylim(0, 40)
        axp.set_facecolor(theme.BG_BASE)
        axp.tick_params(colors=theme.TEXT_DIM)
        axp.grid(color=theme.GRID)
        axp.set_title("AF (dB, offset +40)", color=theme.TEXT, fontsize=10)

        # --- διάταξη στοιχείων ---
        axe = self.canvas.axes[1]
        axe.clear()
        zpos = np.arange(N) * d
        axe.scatter(zpos, np.zeros(N), s=120, c=theme.ACCENT, zorder=3,
                    edgecolors=theme.TEXT, linewidths=0.5)
        for i, z in enumerate(zpos):
            ph = (i * beta) % 360
            axe.annotate(f"{ph:.0f}°", (z, 0.06), color=theme.ACCENT2, fontsize=8,
                         ha="center")
        # κατεύθυνση μεγίστου
        imax = int(np.argmax(AF))
        th_max = th[imax]
        axe.annotate("", xy=(zpos[-1] / 2 + np.cos(th_max) * zpos[-1] / 2,
                             np.sin(th_max) * zpos[-1] / 2),
                     xytext=(zpos[-1] / 2, 0),
                     arrowprops=dict(arrowstyle="-|>", color=theme.ACCENT3, lw=2))
        axe.set_xlim(-d, zpos[-1] + d)
        axe.set_ylim(-0.3, max(zpos[-1] / 2, 0.5))
        axe.set_xlabel("θέση (λ)")
        axe.set_title(f"Διάταξη N={N}, d={d:.2f}λ, β={beta:.0f}°", color=theme.TEXT, fontsize=10)
        axe.set_yticks([])
        axe.grid(color=theme.GRID, alpha=0.25)
        self.canvas.refresh()

        sll = F.sidelobe_level_db(th, AF)
        D_bs = F.uniform_directivity_broadside(N, d)
        D_ef = F.uniform_directivity_endfire(N, d)
        self.readout.setText(
            f"<b>Μέγιστο:</b> θ = {np.degrees(th_max):.1f}°<br>"
            f"<b>Στάθμη 1ου πλευρικού:</b> {sll:.1f} dB<br>"
            f"<b>D₀ (broadside ≈2Nd/λ):</b> {D_bs:.2f} = {10*np.log10(D_bs):.1f} dB<br>"
            f"<b>D₀ (end-fire ≈4Nd/λ):</b> {D_ef:.2f} = {10*np.log10(D_ef):.1f} dB")
