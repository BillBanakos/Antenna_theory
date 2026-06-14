"""
Κεφ. 2 — Διάγραμμα ακτινοβολίας (§2.1, §2.4): 3D επιφάνεια + πολικά E/H,
με λοβούς (κύριος/πλευρικοί/οπίσθιος), μηδενισμούς, HPBW & FNBW.
"""

import numpy as np
from PyQt5.QtWidgets import QComboBox, QLabel, QCheckBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter2Pattern(ModulePage):
    TITLE = "Κεφ. 2 · Διάγραμμα Ακτινοβολίας (3D + Πολικό)"
    SUBTITLE = ("Κύριος/πλευρικοί/οπίσθιος λοβός, μηδενισμοί, HPBW (−3 dB) & FNBW. "
                "Επιλέξτε διάγραμμα και δείτε 3D + τομή πολικού.")

    PATTERNS = {
        "Απειροστό δίπολο  (sinθ)": "inf",
        "Δίπολο λ/2": "halfwave",
        "Πεπερασμένο δίπολο (slider l/λ)": "finite",
        "cosⁿθ  (κατευθυντικό)": "cosn",
        "sin³θ  (παντοκατευθυντικό)": "sin3",
    }

    def build_controls(self, form):
        self.pat = QComboBox()
        self.pat.addItems(list(self.PATTERNS.keys()))
        self.pat.setCurrentIndex(1)
        self.pat.currentIndexChanged.connect(self._mode_changed)
        form.addRow(QLabel("Διάγραμμα:"), self.pat)

        self.len_slider, _ = labeled_slider(
            form, "Μήκος l/λ:", 5, 250, 100, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())

        self.n_slider, _ = labeled_slider(
            form, "Εκθέτης n (cosⁿθ):", 1, 12, 4,
            on_change=lambda v: self.update_plot())

        self.chk_db = QCheckBox("Πολικό σε dB (−40 dB κλίμακα)")
        self.chk_db.stateChanged.connect(self.update_plot)
        form.addRow(self.chk_db)

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"color:{theme.ACCENT}; font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "<b>HPBW</b>: γωνία μεταξύ σημείων −3 dB (U=½U_max).<br>"
            "<b>FNBW</b>: γωνία μεταξύ πρώτων μηδενισμών.<br>"
            "Κύριος λοβός = διεύθυνση μεγίστου· πλευρικοί φραγμένοι από μηδενισμούς.")
        self._mode_changed()

    def build_canvas(self):
        self.canvas3d = MplCanvas(projection="3d", figsize=(6.6, 5.0))
        self.canvas_polar = MplCanvas(projection="polar", figsize=(6.6, 3.6))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas3d, self))
        self.canvas_container.addWidget(self.canvas3d, stretch=3)
        self.canvas_container.addWidget(self.canvas_polar, stretch=2)

    def _mode_changed(self):
        mode = self.PATTERNS[self.pat.currentText()]
        self.len_slider.setEnabled(mode == "finite")
        self.n_slider.setEnabled(mode == "cosn")
        self.update_plot()

    def _pattern_theta(self, theta):
        mode = self.PATTERNS[self.pat.currentText()]
        if mode == "inf":
            return F.infinitesimal_dipole_pattern(theta)
        if mode == "halfwave":
            return F.finite_dipole_pattern(theta, 0.5)
        if mode == "finite":
            return F.finite_dipole_pattern(theta, self.len_slider.value() / 100.0)
        if mode == "cosn":
            n = self.n_slider.value()
            return np.abs(np.cos(theta)) ** n * (np.abs(theta) <= np.pi / 2)
        if mode == "sin3":
            return np.abs(np.sin(theta)) ** 1.5
        return F.infinitesimal_dipole_pattern(theta)

    def update_plot(self):
        if not hasattr(self, "canvas3d"):
            return
        # --- 3D επιφάνεια ---
        ax = self.canvas3d.ax
        ax.clear()
        theta = np.linspace(1e-3, np.pi - 1e-3, 120)
        phi = np.linspace(0, 2 * np.pi, 120)
        T, P = np.meshgrid(theta, phi)
        r = self._pattern_theta(T)
        r = r / max(np.max(r), 1e-9)
        X = r * np.sin(T) * np.cos(P)
        Y = r * np.sin(T) * np.sin(P)
        Z = r * np.cos(T)
        ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.9, edgecolor="none",
                        rcount=60, ccount=60)
        ax.plot([0, 0], [0, 0], [-0.6, 0.6], color=theme.TEXT, lw=3)
        m = 1.0
        ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m, m)
        ax.set_title("3D διάγραμμα ισχύος (κανονικοποιημένο)")
        ax.set_axis_off()
        try:
            ax.set_box_aspect((1, 1, 1))
        except Exception:
            pass
        self.canvas3d.refresh()

        # --- πολική τομή + μετρικές ---
        axp = self.canvas_polar.ax
        axp.clear()
        th = np.linspace(0, np.pi, 1000)
        U = self._pattern_theta(th) ** 2  # διάγραμμα ισχύος
        U = U / max(np.max(U), 1e-9)
        # κατοπτρισμός για πλήρες πολικό (0..2π)
        th_full = np.concatenate([th, th + np.pi])
        U_full = np.concatenate([U, U[::-1]])
        if self.chk_db.isChecked():
            data = np.clip(10 * np.log10(np.maximum(U_full, 1e-4)), -40, 0) + 40
            rmax = 40
            label = "dB (offset +40)"
        else:
            data = U_full
            rmax = 1.05
            label = "γραμμικό"
        axp.plot(th_full, data, color=theme.ACCENT, lw=2)
        axp.fill(th_full, data, color=theme.ACCENT, alpha=0.22)
        axp.set_theta_zero_location("N")
        axp.set_theta_direction(-1)
        axp.set_rlabel_position(135)
        axp.set_ylim(0, rmax)
        axp.set_facecolor(theme.BG_BASE)
        axp.tick_params(colors=theme.TEXT_DIM)
        axp.grid(color=theme.GRID, alpha=0.6)
        axp.set_title(f"Πολική τομή ({label})", color=theme.TEXT, fontsize=10)
        self.canvas_polar.refresh()

        # --- HPBW / FNBW / D0 ---
        hp = F.hpbw_from_pattern(th, U)
        D0 = F.directivity_numerical(np.sqrt(U), th)  # U(pattern) πεδίο->ισχύς ήδη
        D0 = F.directivity_numerical(U, th)
        hp_txt = f"{np.degrees(hp):.1f}°" if hp else "—"
        # πρώτος μηδενισμός
        imax = int(np.argmax(U))
        nulls = []
        for i in range(imax + 1, len(U)):
            if U[i] < 1e-3:
                nulls.append(th[i]); break
        fn = 2 * abs(nulls[0] - th[imax]) if nulls else None
        fn_txt = f"{np.degrees(fn):.1f}°" if fn else "—"
        self.readout.setText(
            f"<b>Μέγιστο:</b> θ = {np.degrees(th[imax]):.0f}°<br>"
            f"<b>HPBW:</b> {hp_txt} &nbsp;|&nbsp; <b>FNBW:</b> {fn_txt}<br>"
            f"<b>D₀ (αριθμητικά):</b> {D0:.3f} = {10*np.log10(D0):.2f} dBi")
