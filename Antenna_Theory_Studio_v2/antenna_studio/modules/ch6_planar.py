"""
Κεφ. 6.10 — Επίπεδες στοιχειοκεραίες (Planar):
διαχωρίσιμη διέγερση AF = AFx(M)·AFy(N), broadside & σάρωση,
grating lobes όταν d ≥ λ. 3D επιφάνεια |AF| + πλέγμα στοιχείων.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QSpinBox, QCheckBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter6Planar(ModulePage):
    TITLE = "Κεφ. 6.10 · Επίπεδη Στοιχειοκεραία (M×N) — Σάρωση"
    SUBTITLE = ("AF = AFₓ(M)·AF_y(N). Στρέψτε τη δέσμη σε (θ₀,φ₀). "
                "Για σάρωση χωρίς grating lobes χρειάζεται d < λ/2.")

    def build_controls(self, form):
        self.M = QSpinBox(); self.M.setRange(1, 16); self.M.setValue(6)
        self.M.valueChanged.connect(self.update_plot)
        form.addRow(QLabel("Στοιχεία κατά x (M):"), self.M)

        self.N = QSpinBox(); self.N.setRange(1, 16); self.N.setValue(6)
        self.N.valueChanged.connect(self.update_plot)
        form.addRow(QLabel("Στοιχεία κατά y (N):"), self.N)

        self.dx_slider, _ = labeled_slider(
            form, "Απόσταση dx/λ:", 5, 150, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())
        self.dy_slider, _ = labeled_slider(
            form, "Απόσταση dy/λ:", 5, 150, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())

        self.theta0, _ = labeled_slider(
            form, "Σάρωση θ₀:", 0, 80, 0, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())
        self.phi0, _ = labeled_slider(
            form, "Σάρωση φ₀:", 0, 360, 0, fmt="{}", suffix="°",
            on_change=lambda v: self.update_plot())

        self.show3d = QCheckBox("3D επιφάνεια |AF|")
        self.show3d.setChecked(True)
        self.show3d.stateChanged.connect(self._rebuild)
        form.addRow(self.show3d)

        self.readout = QLabel(); self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "Broadside: ίσες φάσεις ⇒ μέγιστο κάθετο στο επίπεδο.<br>"
            "Σάρωση εκτός broadside ⇒ HPBW αυξάνει (∝ 1/cos θ₀).<br>"
            "D₀ ∝ D₀ₓ·D_y · cos θ₀.  d ≥ λ ⇒ grating lobes.")

    def build_canvas(self):
        self._make_canvas(True)

    def _make_canvas(self, three_d):
        proj = ["3d", None] if three_d else [None, None]
        self.canvas = MplCanvas(nrows=1, ncols=2, projection=proj, figsize=(9.2, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def _rebuild(self):
        # αφαίρεση παλιού καμβά/toolbar και ξαναχτίσιμο για αλλαγή projection
        while self.canvas_container.count():
            item = self.canvas_container.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        self._make_canvas(self.show3d.isChecked())
        self.update_plot()

    def _progressive_phase(self):
        """β που εστιάζει τη δέσμη στο (θ₀,φ₀)."""
        th0 = np.radians(self.theta0.value())
        ph0 = np.radians(self.phi0.value())
        dx = self.dx_slider.value() / 100.0
        dy = self.dy_slider.value() / 100.0
        bx = -2 * np.pi * dx * np.sin(th0) * np.cos(ph0)
        by = -2 * np.pi * dy * np.sin(th0) * np.sin(ph0)
        return bx, by

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        M = self.M.value(); N = self.N.value()
        dx = self.dx_slider.value() / 100.0
        dy = self.dy_slider.value() / 100.0
        bx, by = self._progressive_phase()

        # πλέγμα ημισφαιρίου (θ:0..90, φ:0..360) προβολή u=sinθcosφ, v=sinθsinφ
        th = np.linspace(0, np.pi / 2, 160)
        ph = np.linspace(0, 2 * np.pi, 200)
        TH, PH = np.meshgrid(th, ph)
        psix = 2 * np.pi * dx * np.sin(TH) * np.cos(PH) + bx
        psiy = 2 * np.pi * dy * np.sin(TH) * np.sin(PH) + by

        def afn(psi, n):
            num = np.sin(n * psi / 2)
            den = n * np.sin(psi / 2)
            out = np.where(np.abs(den) < 1e-9, 1.0, num / np.where(den == 0, 1e-9, den))
            return np.abs(out)

        AF = afn(psix, M) * afn(psiy, N)
        AF = AF / max(AF.max(), 1e-9)

        ax0 = self.canvas.axes[0]
        ax0.clear()
        U = TH / (np.pi / 2)  # ακτίνα ∝ θ (0 στο ζενίθ)
        X = U * np.cos(PH); Y = U * np.sin(PH)
        if self.show3d.isChecked():
            ax0.plot_surface(X, Y, AF, cmap="viridis", linewidth=0, antialiased=True,
                             rcount=60, ccount=60)
            ax0.set_zlim(0, 1)
            ax0.set_title("|AF| (ημισφαίριο, ακτίνα∝θ)", color=theme.TEXT, fontsize=10)
            ax0.set_facecolor(theme.BG_BASE)
            for axis in (ax0.xaxis, ax0.yaxis, ax0.zaxis):
                axis.set_pane_color((0, 0, 0, 0))
            ax0.tick_params(colors=theme.TEXT_DIM)
        else:
            cf = ax0.contourf(X, Y, 20 * np.log10(np.maximum(AF, 1e-3)),
                              levels=40, cmap="viridis", vmin=-40, vmax=0)
            ax0.set_aspect("equal")
            ax0.set_title("|AF| (dB, κάτοψη u–v)", color=theme.TEXT, fontsize=10)
            ax0.tick_params(colors=theme.TEXT_DIM)
            self.canvas.fig.colorbar(cf, ax=ax0, fraction=0.046, pad=0.04)

        # --- πλέγμα στοιχείων ---
        ax1 = self.canvas.axes[1]
        ax1.clear()
        xx = np.arange(M) * dx
        yy = np.arange(N) * dy
        GX, GY = np.meshgrid(xx, yy)
        ax1.scatter(GX, GY, s=80, c=theme.ACCENT, edgecolors=theme.TEXT, linewidths=0.4)
        ax1.set_aspect("equal")
        ax1.set_xlabel("x (λ)"); ax1.set_ylabel("y (λ)")
        ax1.set_title(f"Πλέγμα {M}×{N}", color=theme.TEXT, fontsize=10)
        ax1.grid(color=theme.GRID, alpha=0.3)
        self.canvas.refresh()

        grating = (dx >= 1.0) or (dy >= 1.0)
        scan = self.theta0.value()
        hpbw_factor = 1.0 / max(np.cos(np.radians(scan)), 1e-3)
        warn = (f"<span style='color:{theme.DANGER}'>⚠ grating lobes (d≥λ)</span>"
                if grating else
                f"<span style='color:{theme.GOOD}'>✓ χωρίς grating</span>")
        self.readout.setText(
            f"<b>Σάρωση:</b> θ₀={scan}°, φ₀={self.phi0.value()}°<br>"
            f"<b>β:</b> βₓ={np.degrees(bx):.0f}°, β_y={np.degrees(by):.0f}°<br>"
            f"<b>Διεύρυνση HPBW (1/cosθ₀):</b> ×{hpbw_factor:.2f}<br>{warn}")
