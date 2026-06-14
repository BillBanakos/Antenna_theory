"""
Κεφ. 2/4 — Παράγοντας απωλειών πόλωσης PLF (§2.8, §4.10):
ζεύξη Tx→Rx, υπολογισμός PLF = |ρ̂_w·ρ̂_a|², με ζωντανό 3D κύμα.
Καλύπτει: γραμμικές υπό γωνία, κυκλικές (RHCP/LHCP), σταυρωτά δίπολα.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox
from PyQt5.QtCore import QTimer

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter2PLF(ModulePage):
    TITLE = "Κεφ. 2/4 · Παράγοντας Απωλειών Πόλωσης (PLF)"
    SUBTITLE = ("PLF = |ρ̂_w · ρ̂_a|².  PLF=1 (0 dB) ίδια πόλωση, "
                "PLF=0 (−∞ dB) ορθογώνιες.  Ζωντανή 3D ζεύξη Tx → Rx.")

    POLS = ["Γραμμική (γωνία)", "Κυκλική RHCP", "Κυκλική LHCP"]

    def build_controls(self, form):
        self.t = 0.0
        self.tx = QComboBox(); self.tx.addItems(self.POLS)
        self.tx.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Εκπομπός (Tx):"), self.tx)
        self.rx = QComboBox(); self.rx.addItems(self.POLS)
        self.rx.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Δέκτης (Rx):"), self.rx)

        self.tx_ang, _ = labeled_slider(
            form, "Γωνία Tx (γραμμ.):", 0, 180, 0, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())
        self.rx_ang, _ = labeled_slider(
            form, "Γωνία Rx (γραμμ.):", 0, 180, 90, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:18px; font-weight:700; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:12px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "Σταυρωτά γραμμικά: PLF = cos²(Δθ).<br>"
            "Γραμμική ↔ κυκλική: πάντα PLF = 0.5 (−3 dB).<br>"
            "Ίδια κυκλική: PLF=1· αντίθετη (RHCP↔LHCP): PLF=0.")

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

    def build_canvas(self):
        self.canvas = MplCanvas(projection="3d", figsize=(7.6, 5.8))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def _tick(self):
        self.t += 0.2
        self.update_plot()

    def _jones(self, pol, ang_deg):
        """Επιστρέφει μιγαδικό διάνυσμα πόλωσης (x,y)."""
        if pol == "Γραμμική (γωνία)":
            a = np.radians(ang_deg)
            return np.array([np.cos(a), np.sin(a)], dtype=complex)
        if pol == "Κυκλική RHCP":
            return np.array([1, -1j], dtype=complex) / np.sqrt(2)
        return np.array([1, 1j], dtype=complex) / np.sqrt(2)  # LHCP

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        txp = self.tx.currentText(); rxp = self.rx.currentText()
        rho_w = self._jones(txp, self.tx_ang.value())
        rho_a = self._jones(rxp, self.rx_ang.value())
        val = F.plf(rho_w, rho_a)

        ax = self.canvas.ax
        ax.clear()
        dist = 14
        z = np.linspace(0, dist, 400)
        # κύμα Tx
        x = np.real(rho_w[0]) * np.cos(z - self.t) - np.imag(rho_w[0]) * np.sin(z - self.t)
        y = np.real(rho_w[1]) * np.cos(z - self.t) - np.imag(rho_w[1]) * np.sin(z - self.t)
        col = theme.GOOD if val > 0.49 else (theme.ACCENT2 if val > 1e-3 else theme.DANGER)
        ax.plot(x, y, z, color=col, lw=2, alpha=0.9)
        ax.plot(x, y, np.zeros_like(z), color=col, lw=0.8, alpha=0.25)

        # σύμβολα κεραιών
        self._draw_antenna(ax, 0, txp, self.tx_ang.value(), theme.TEXT, "Tx")
        self._draw_antenna(ax, dist, rxp, self.rx_ang.value(), col, "Rx")

        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_zlim(-1, dist + 1)
        ax.set_title("Ζεύξη πόλωσης Tx → Rx")
        ax.set_axis_off()
        self.canvas.refresh()

        if val < 1e-9:
            txt = f"PLF = 0.00  →  −∞ dB"
            color = theme.DANGER
        else:
            txt = f"PLF = {val:.3f}  →  {10*np.log10(val):.2f} dB"
            color = theme.GOOD if val > 0.49 else theme.ACCENT2
        self.readout.setText(f"<span style='color:{color}'>{txt}</span>")

    def _draw_antenna(self, ax, zpos, pol, ang, color, label):
        L = 1.6
        if pol == "Γραμμική (γωνία)":
            a = np.radians(ang)
            dx, dy = L * np.cos(a), L * np.sin(a)
            ax.plot([-dx, dx], [-dy, dy], [zpos, zpos], color=color, lw=4)
        else:  # κυκλική: σταυρός
            ax.plot([-L, L], [0, 0], [zpos, zpos], color=color, lw=3)
            ax.plot([0, 0], [-L, L], [zpos, zpos], color=color, lw=3)
        ax.text(0, L + 0.4, zpos, label, color=color, fontsize=12, fontweight="bold")
