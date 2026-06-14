"""
Κεφ. 4 — Δίπολο πεπερασμένου μήκους (§4.1–4.4): διάγραμμα ως προς l/λ,
αντίσταση ακτινοβολίας/εισόδου (Si/Ci), VSWR σε γραμμή Z0. Δείχνει τη
διάσπαση του κύριου λοβού πέρα από ~1.25λ.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter4Dipole(ModulePage):
    TITLE = "Κεφ. 4 · Δίπολο — Διάγραμμα, R_r, Z_in, VSWR"
    SUBTITLE = ("F(θ) = [cos(kl/2·cosθ) − cos(kl/2)] / sinθ.  "
                "Δείτε πώς αλλάζει το διάγραμμα και η αντίσταση με το μήκος.")

    def build_controls(self, form):
        self.len_slider, _ = labeled_slider(
            form, "Μήκος l/λ:", 5, 250, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())
        self.z0_slider, _ = labeled_slider(
            form, "Γραμμή Z₀:", 50, 600, 50, fmt="{}", suffix=" Ω",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "Κλασικές τιμές R_in: λ/4≈13.7Ω · λ/2=73Ω · 3λ/4≈372Ω · λ→∞.<br>"
            "Συντονισμός λ/2: Z_in≈73+j42.5Ω (X μηδενίζεται στο ≈0.48λ).")
        self.add_export_button(self._export)

    def _export(self):
        import numpy as np
        Lv = np.linspace(0.05, 1.45, 200)
        Rin = [F.dipole_input_resistance(l) for l in Lv]
        Rr = [F.dipole_radiation_resistance(l) for l in Lv]
        return ["L_over_lambda", "Rin_ohm", "Rr_ohm"], list(zip(Lv, Rin, Rr))

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2,
                                projection=["polar", None], figsize=(8.6, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        L = self.len_slider.value() / 100.0
        Z0 = self.z0_slider.value()

        # --- πολικό διάγραμμα ---
        axp = self.canvas.axes[0]
        axp.clear()
        th = np.linspace(1e-3, np.pi - 1e-3, 1000)
        F_field = F.finite_dipole_pattern(th, L)
        U = (F_field / max(F_field.max(), 1e-9)) ** 2
        th_full = np.concatenate([th, th + np.pi])
        U_full = np.concatenate([U, U[::-1]])
        axp.plot(th_full, U_full, color=theme.ACCENT, lw=2)
        axp.fill(th_full, U_full, color=theme.ACCENT, alpha=0.2)
        axp.set_theta_zero_location("N")
        axp.set_theta_direction(-1)
        axp.set_facecolor(theme.BG_BASE)
        axp.tick_params(colors=theme.TEXT_DIM)
        axp.grid(color=theme.GRID)
        axp.set_title(f"Διάγραμμα l={L:.2f}λ", color=theme.TEXT, fontsize=10)

        # --- R_r / R_in vs μήκος ---
        axc = self.canvas.axes[1]
        axc.clear()
        Ls = np.linspace(0.05, 2.0, 400)
        Rr = np.array([F.dipole_radiation_resistance(x) for x in Ls])
        Rin = np.array([min(F.dipole_input_resistance(x), 2000) for x in Ls])
        axc.plot(Ls, Rr, color=theme.ACCENT2, lw=2, label="R_r (αναφ. μέγιστο)")
        axc.plot(Ls, Rin, color=theme.ACCENT4, lw=2, label="R_in (αναφ. είσοδος)")
        axc.axvline(L, color=theme.ACCENT3, lw=1.5, ls="--")
        axc.set_xlabel("l/λ")
        axc.set_ylabel("Αντίσταση (Ω)")
        axc.set_ylim(0, 800)
        axc.set_title("Αντίσταση ακτινοβολίας/εισόδου", color=theme.TEXT, fontsize=10)
        axc.legend(facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
                   labelcolor=theme.TEXT, fontsize=8)
        axc.grid(color=theme.GRID, alpha=0.35)
        self.canvas.refresh()

        Rr_now = F.dipole_radiation_resistance(L)
        Rin_now = F.dipole_input_resistance(L)
        D0 = F.directivity_numerical(U, th)
        if np.isfinite(Rin_now):
            vswr = F.vswr_from_R(Rin_now, Z0)
            vswr_txt = f"{vswr:.2f}"
            rin_txt = f"{Rin_now:.1f} Ω"
        else:
            vswr_txt = "∞"
            rin_txt = "∞"
        self.readout.setText(
            f"<b>l = {L:.2f} λ</b><br>"
            f"R_r (μέγιστο) = <b>{Rr_now:.1f} Ω</b><br>"
            f"R_in (συντον.) = <b>{rin_txt}</b><br>"
            f"D₀ = <b>{D0:.3f}</b> = {10*np.log10(D0):.2f} dBi<br>"
            f"VSWR (σε {Z0}Ω) = <b>{vswr_txt}</b>")
