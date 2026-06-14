"""
Κεφ. 2 — Κατευθυντικότητα & προσεγγιστικοί τύποι (§2.5, §2.7):
ακριβής (αριθμητική) vs Kraus, Tai–Pereira, McDonald, Pozar.
Δείχνει πότε καταρρέει κάθε προσέγγιση.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter2Directivity(ModulePage):
    TITLE = "Κεφ. 2 · Κατευθυντικότητα — Ακριβής vs Προσεγγίσεις"
    SUBTITLE = ("U(θ) = cosⁿθ (δέσμη-μολύβι) ή sinⁿθ (παντοκατευθυντικό). "
                "Σύγκριση ακριβούς D₀ με Kraus / Tai–Pereira / McDonald / Pozar.")

    KINDS = {
        "cosⁿθ  (δέσμη-μολύβι, ένας λοβός)": "pencil",
        "sinⁿθ  (παντοκατευθυντικό)": "omni",
    }

    def build_controls(self, form):
        self.kind = QComboBox()
        self.kind.addItems(list(self.KINDS.keys()))
        self.kind.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Τύπος διαγράμματος:"), self.kind)

        self.n_slider, _ = labeled_slider(
            form, "Εκθέτης n:", 1, 40, 6,
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "<b>Kraus</b> 41253/(Θ₁Θ₂): καλός για στενές δέσμες.<br>"
            "<b>Tai–Pereira</b> 72815/(Θ₁²+Θ₂²): καλύτερος για ευρείες.<br>"
            "<b>McDonald/Pozar</b>: για παντοκατευθυντικά. "
            "Εφαρμογή Kraus σε ευρύ διάγραμμα ⇒ μεγάλο σφάλμα!")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2, figsize=(8.4, 5.2))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        kind = self.KINDS[self.kind.currentText()]
        n = self.n_slider.value()
        th = np.linspace(1e-3, np.pi - 1e-3, 4000)

        if kind == "pencil":
            U = (np.cos(th) ** n) * (th <= np.pi / 2)
            U = U ** 1  # ήδη ισχύς αν θεωρήσουμε cosⁿ ως ισχύ
        else:
            U = np.sin(th) ** n

        D_exact = F.directivity_numerical(U, th)
        hp = F.hpbw_from_pattern(th, U)
        hp_deg = np.degrees(hp) if hp else np.nan

        rows = [("Ακριβής (αριθμητική)", D_exact)]
        if not np.isnan(hp_deg):
            if kind == "pencil":
                rows.append(("Kraus", F.directivity_kraus(hp_deg, hp_deg)))
                rows.append(("Tai–Pereira", F.directivity_tai_pereira(hp_deg, hp_deg)))
            else:
                rows.append(("McDonald", F.directivity_mcdonald(hp_deg)))
                rows.append(("Pozar", F.directivity_pozar(hp_deg)))
                rows.append(("Kraus (λάθος χρήση)", F.directivity_kraus(hp_deg, hp_deg)))

        # --- αριστερό: πολικό διάγραμμα ---
        self.canvas.fig.clf()
        self.canvas.axes = [
            self.canvas.fig.add_subplot(1, 2, 1, projection="polar"),
            self.canvas.fig.add_subplot(1, 2, 2),
        ]
        axp, axb = self.canvas.axes
        Un = U / np.max(U)
        th_full = np.concatenate([th, th + np.pi])
        U_full = np.concatenate([Un, Un[::-1]])
        axp.plot(th_full, U_full, color=theme.ACCENT, lw=2)
        axp.fill(th_full, U_full, color=theme.ACCENT, alpha=0.2)
        axp.set_theta_zero_location("N")
        axp.set_theta_direction(-1)
        axp.set_facecolor(theme.BG_BASE)
        axp.tick_params(colors=theme.TEXT_DIM)
        axp.grid(color=theme.GRID)
        axp.set_title("Διάγραμμα ισχύος U(θ)", color=theme.TEXT, fontsize=10)

        # --- δεξιό: bar σύγκρισης ---
        names = [r[0] for r in rows]
        vals = [10 * np.log10(max(r[1], 1e-6)) for r in rows]
        colors = [theme.ACCENT] + [theme.ACCENT2, theme.ACCENT4, theme.ACCENT3, theme.DANGER][:len(rows) - 1]
        bars = axb.barh(range(len(names)), vals, color=colors)
        axb.set_yticks(range(len(names)))
        axb.set_yticklabels(names, fontsize=9)
        axb.invert_yaxis()
        axb.set_xlabel("D₀ (dBi)")
        axb.set_title("Σύγκριση κατευθυντικότητας", color=theme.TEXT, fontsize=10)
        axb.grid(axis="x", color=theme.GRID, alpha=0.4)
        for i, v in enumerate(vals):
            axb.text(v, i, f" {v:.2f}", va="center", color=theme.TEXT, fontsize=9)

        theme.apply_mpl_style(self.canvas.fig, self.canvas.axes)
        self.canvas.refresh()

        html = f"<b>HPBW:</b> {hp_deg:.2f}°<br><table cellpadding='2'>"
        for name, val in rows:
            err = (val / D_exact - 1) * 100
            html += (f"<tr><td>{name}</td><td>&nbsp;<b>{val:.3f}</b> "
                     f"({10*np.log10(max(val,1e-6)):.2f} dBi)</td>"
                     f"<td>&nbsp;<span style='color:{theme.TEXT_DIM}'>{err:+.1f}%</span></td></tr>")
        html += "</table>"
        self.readout.setText(html)
