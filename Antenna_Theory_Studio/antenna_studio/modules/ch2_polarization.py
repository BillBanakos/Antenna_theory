"""
Κεφ. 2 — Πόλωση (§2.8): ζωντανή έλλειψη πόλωσης από Ex, Ey, Δφ.
Δείχνει AR, γωνία κλίσης τ, φορά περιστροφής (LH/RH), ταξινόμηση,
και animated διάνυσμα E + 3D ελικοειδές κύμα.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter2Polarization(ModulePage):
    TITLE = "Κεφ. 2 · Πόλωση — Ζωντανή Έλλειψη & Φορά Περιστροφής"
    SUBTITLE = ("E = x̂·E_x + ŷ·E_y·e^{jΔφ}.  Διάδοση +ẑ (σύμβαση Balanis/IEEE): "
                "Δφ>0 ⇒ LH/CCW,  Δφ<0 ⇒ RH/CW.")

    def build_controls(self, form):
        self.t = 0.0
        self.ex_slider, _ = labeled_slider(
            form, "E_x0:", 0, 100, 100, scale=0.01, fmt="{:.2f}",
            on_change=lambda v: self.update_plot())
        self.ey_slider, _ = labeled_slider(
            form, "E_y0:", 0, 100, 100, scale=0.01, fmt="{:.2f}",
            on_change=lambda v: self.update_plot())
        self.dphi_slider, _ = labeled_slider(
            form, "Δφ = φ_y − φ_x:", -180, 180, 90, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:13px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:10px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "<b>Γραμμική:</b> Δφ=0°/±180° ή μία συνιστώσα 0.<br>"
            "<b>Κυκλική:</b> ίσα πλάτη & Δφ=±90°.<br>"
            "<b>Ελλειπτική:</b> κάθε άλλη.  AR=∞(γραμμ.) … 1(κυκλ.).")

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2,
                                projection=[None, "3d"], figsize=(8.6, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def _tick(self):
        self.t += 0.12
        self.update_plot()

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        Ex0 = self.ex_slider.value() / 100.0
        Ey0 = self.ey_slider.value() / 100.0
        dphi = np.radians(self.dphi_slider.value())

        # έλλειψη: παραμετρικά στον χρόνο
        wt = np.linspace(0, 2 * np.pi, 400)
        Ex = Ex0 * np.cos(wt)
        Ey = Ey0 * np.cos(wt + dphi)

        ax = self.canvas.axes[0]
        ax.clear()
        lim = max(Ex0, Ey0, 0.2) * 1.3
        ax.plot(Ex, Ey, color=theme.ACCENT, lw=2)
        # στιγμιαία αιχμή
        ex_now = Ex0 * np.cos(self.t)
        ey_now = Ey0 * np.cos(self.t + dphi)
        ax.annotate("", xy=(ex_now, ey_now), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=theme.ACCENT3, lw=2.5))
        ax.plot(ex_now, ey_now, "o", color=theme.ACCENT3, ms=8)
        ax.axhline(0, color=theme.GRID, lw=1)
        ax.axvline(0, color=theme.GRID, lw=1)

        # άξονες έλλειψης
        AR, OA, OB = F.axial_ratio(Ex0, Ey0, dphi)
        tau = F.tilt_angle(Ex0, Ey0, dphi)
        if np.isfinite(OA) and OA > 0:
            ax.plot([-OA * np.cos(tau), OA * np.cos(tau)],
                    [-OA * np.sin(tau), OA * np.sin(tau)],
                    color=theme.ACCENT2, lw=1.4, ls="--")
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        ax.set_xlabel("E_x"); ax.set_ylabel("E_y")
        ax.set_title("Έλλειψη πόλωσης (επίπεδο ⊥ διάδοσης)")
        ax.grid(color=theme.GRID, alpha=0.3)

        # 3D ελικοειδές κύμα
        ax3 = self.canvas.axes[1]
        ax3.clear()
        z = np.linspace(0, 4 * np.pi, 300)
        x = Ex0 * np.cos(z - self.t)
        y = Ey0 * np.cos(z - self.t + dphi)
        ax3.plot(x, y, z, color=theme.ACCENT, lw=2)
        ax3.plot(x, y, np.zeros_like(z), color=theme.ACCENT3, lw=1, alpha=0.4)
        ax3.plot([0, 0], [0, 0], [0, 4 * np.pi], color=theme.GRID, lw=1)
        ax3.set_xlim(-1.2, 1.2); ax3.set_ylim(-1.2, 1.2); ax3.set_zlim(0, 4 * np.pi)
        ax3.set_title("Διάδοση κύματος +ẑ")
        ax3.set_axis_off()
        self.canvas.refresh()

        kind, sense = F.classify_polarization(Ex0, Ey0, dphi)
        ar_txt = "∞" if not np.isfinite(AR) else f"{AR:.3f}"
        color = (theme.GOOD if "Κυκλική" in kind else
                 theme.ACCENT2 if "Ελλειπτική" in kind else theme.ACCENT4)
        self.readout.setText(
            f"<b style='color:{color}; font-size:15px'>{kind}</b><br>"
            f"<b>Φορά:</b> {sense}<br>"
            f"<b>Axial Ratio:</b> {ar_txt} "
            f"({'∞ dB' if not np.isfinite(AR) else f'{20*np.log10(AR):.2f} dB'})<br>"
            f"<b>Γωνία κλίσης τ:</b> {np.degrees(tau):.1f}°")
