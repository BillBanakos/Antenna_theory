"""
Κεφ. 4 — Θεωρία ειδώλων & κεραία πάνω από έδαφος (§4.6–4.7).
Στοιχείο + είδωλο: κατακόρυφο AF=2cos(kh cosθ), οριζόντιο AF=2|sin(kh cosθ)|.
Τοποθέτηση μηδενισμών, αριθμός λοβών, πίνακας ειδώλων.
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme
from ..core import formulas as F


class Chapter4Image(ModulePage):
    TITLE = "Κεφ. 4 · Θεωρία Ειδώλων — Κεραία πάνω από Έδαφος"
    SUBTITLE = ("Πολλαπλασιασμός διαγραμμάτων: (διάγραμμα στοιχείου) × (AF στοιχείου+ειδώλου). "
                "θ μετριέται από την κατακόρυφο.")

    def build_controls(self, form):
        self.orient = QComboBox()
        self.orient.addItems(["Κατακόρυφο δίπολο (είδωλο +1)",
                              "Οριζόντιο δίπολο (είδωλο −1)"])
        self.orient.currentIndexChanged.connect(self.update_plot)
        form.addRow(QLabel("Προσανατολισμός:"), self.orient)

        self.h_slider, _ = labeled_slider(
            form, "Ύψος h/λ:", 5, 300, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())

        self.readout = QLabel()
        self.readout.setWordWrap(True)
        self.readout.setStyleSheet(
            f"font-size:12px; background:{theme.BG_BASE};"
            f"border:1px solid {theme.GRID}; border-radius:6px; padding:8px; margin-top:6px;")
        form.addRow(self.readout)

        self.add_theory(
            "<b>Πίνακας ειδώλων (PEC):</b> κατακόρυφο +1, οριζόντιο −1.<br>"
            "Αριθμός λοβών: κατακόρυφο ≈2h/λ, οριζόντιο ≈2h/λ+1.<br>"
            "Μηδενισμοί κατακόρυφου: kh·cosθ = (2n+1)π/2.")

    def build_canvas(self):
        self.canvas = MplCanvas(nrows=1, ncols=2,
                                projection=["polar", None], figsize=(8.6, 5.0))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        h = self.h_slider.value() / 100.0
        vertical = self.orient.currentIndex() == 0

        # θ από την κατακόρυφο: 0..π/2 (πάνω από το έδαφος). Σχεδιάζουμε άνω ημιχώρο.
        th = np.linspace(0, np.pi / 2, 800)
        AF = F.image_array_factor(th, h, vertical)
        # συνολικό = AF × διάγραμμα στοιχείου (λ/2 δίπολο). Για το element pattern:
        # κατακόρυφο: μέγιστο στον ορίζοντα· οριζόντιο ~ ομοιόμορφο σε αυτό το επίπεδο.
        elem = np.ones_like(th)
        total = AF * elem
        total = total / max(total.max(), 1e-9)

        axp = self.canvas.axes[0]
        axp.clear()
        # πολικό με θ από την κατακόρυφο, μόνο άνω ημιχώρος (0..180 με κατοπτρισμό σε φ)
        th_plot = np.concatenate([th, np.pi - th[::-1]])  # δεξιά+αριστερά
        data = np.concatenate([total, total[::-1]])
        axp.plot(th_plot, data, color=theme.ACCENT, lw=2)
        axp.fill(th_plot, data, color=theme.ACCENT, alpha=0.2)
        axp.set_theta_zero_location("N")
        axp.set_theta_direction(-1)
        axp.set_thetamin(-90); axp.set_thetamax(90)
        axp.set_facecolor(theme.BG_BASE)
        axp.tick_params(colors=theme.TEXT_DIM)
        axp.grid(color=theme.GRID)
        axp.set_title(f"Διάγραμμα (άνω ημιχώρος), h={h:.2f}λ", color=theme.TEXT, fontsize=10)

        # γεωμετρία στοιχείου + ειδώλου
        axg = self.canvas.axes[1]
        axg.clear()
        axg.axhline(0, color=theme.ACCENT2, lw=3)  # έδαφος
        axg.fill_between([-1, 1], -h * 1.5, 0, color=theme.ACCENT2, alpha=0.12)
        # στοιχείο
        if vertical:
            axg.plot([0, 0], [h - 0.1, h + 0.1], color=theme.ACCENT, lw=4)
            axg.plot([0, 0], [-h - 0.1, -h + 0.1], color=theme.ACCENT4, lw=4, ls="--")
        else:
            axg.plot([-0.15, 0.15], [h, h], color=theme.ACCENT, lw=4)
            axg.plot([-0.15, 0.15], [-h, -h], color=theme.ACCENT4, lw=4, ls="--")
        axg.text(0.2, h, "στοιχείο", color=theme.ACCENT, fontsize=10, va="center")
        sign = "+1" if vertical else "−1"
        axg.text(0.2, -h, f"είδωλο ({sign})", color=theme.ACCENT4, fontsize=10, va="center")
        axg.annotate("", xy=(-0.5, h), xytext=(-0.5, 0),
                     arrowprops=dict(arrowstyle="<->", color=theme.TEXT_DIM))
        axg.text(-0.6, h / 2, "h", color=theme.TEXT, ha="right")
        axg.set_xlim(-1, 1); axg.set_ylim(-h * 1.6, h * 1.6)
        axg.set_title("Στοιχείο + Είδωλο", color=theme.TEXT, fontsize=10)
        axg.set_xticks([])
        axg.grid(color=theme.GRID, alpha=0.2)
        self.canvas.refresh()

        # μηδενισμοί κατακόρυφου
        nulls = []
        if vertical:
            n = 0
            while True:
                arg = (2 * n + 1) * np.pi / 2
                c = arg / (2 * np.pi * h)
                if c > 1:
                    break
                nulls.append(np.degrees(np.arccos(c)))
                n += 1
        n_lobes = (int(2 * h) if vertical else int(2 * h) + 1)
        nulls_txt = ", ".join(f"{x:.1f}°" for x in nulls) if nulls else "—"
        self.readout.setText(
            f"<b>h = {h:.2f} λ</b><br>"
            f"Είδωλο: <b>{'+1 (κατακόρυφο)' if vertical else '−1 (οριζόντιο)'}</b><br>"
            f"Αριθμός λοβών ≈ <b>{n_lobes}</b><br>"
            f"Μηδενισμοί (από κατακόρυφο): <b>{nulls_txt}</b>")
