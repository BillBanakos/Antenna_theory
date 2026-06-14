"""
Κεφ. 1 — Μηχανισμός ακτινοβολίας & κατανομή ρεύματος σε λεπτό σύρμα (§1.3–1.4).

Animated: στάσιμο κύμα ρεύματος I(z') = I0 sin[k(l/2 - |z'|)] για διάφορα μήκη,
με τις χαρακτηριστικές μορφές (τριγωνικό, ημικυματικό, λ, 3λ/2).
"""

import numpy as np
from PyQt5.QtWidgets import QComboBox, QLabel, QCheckBox
from PyQt5.QtCore import QTimer

from ..core.mpl_canvas import MplCanvas, ModulePage, StyledNavToolbar, labeled_slider
from ..core import theme


class Chapter1Radiation(ModulePage):
    TITLE = "Κεφ. 1 · Μηχανισμός Ακτινοβολίας & Κατανομή Ρεύματος"
    SUBTITLE = ("Στάσιμο κύμα ρεύματος σε λεπτό δίπολο:  "
                "I(z') = I₀·sin[k(l/2 − |z'|)].  Animated χρονική ταλάντωση.")

    PRESETS = {
        "l ≪ λ  (σχεδόν τριγωνικό)": 0.1,
        "l = λ/2  (ημικυματικό)": 0.5,
        "l = λ  (μηδέν στο κέντρο)": 1.0,
        "l = 3λ/2  (πολυλοβικό)": 1.5,
        "Ελεύθερο (slider)": None,
    }

    def build_controls(self, form):
        self.t = 0.0

        self.preset = QComboBox()
        self.preset.addItems(list(self.PRESETS.keys()))
        self.preset.setCurrentIndex(1)
        self.preset.currentIndexChanged.connect(self._preset_changed)
        form.addRow(QLabel("Προεπιλογή μήκους:"), self.preset)

        self.len_slider, _ = labeled_slider(
            form, "Μήκος l/λ:", 5, 250, 50, scale=0.01, fmt="{:.2f}", suffix=" λ",
            on_change=lambda v: self.update_plot())

        self.chk_envelope = QCheckBox("Εμφάνιση περιβάλλουσας (|I|)")
        self.chk_envelope.setChecked(True)
        self.chk_envelope.stateChanged.connect(self.update_plot)
        form.addRow(self.chk_envelope)

        self.chk_charge = QCheckBox("Εμφάνιση «δεσμίδων» φορτίου (λ/2)")
        self.chk_charge.stateChanged.connect(self.update_plot)
        form.addRow(self.chk_charge)

        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setStyleSheet(f"color:{theme.ACCENT}; font-size:12px; margin-top:6px;")
        form.addRow(self.info)

        self.add_theory(
            "<b>Συνθήκη ακτινοβολίας:</b> χρονικά μεταβαλλόμενο ρεύμα ⇔ "
            "επιτάχυνση/επιβράδυνση φορτίου.  Το ρεύμα μηδενίζεται στα ανοιχτά "
            "άκρα.  Μέγιστο στο σημείο τροφοδοσίας <i>μόνο</i> όταν l = λ/2."
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(40)

    def build_canvas(self):
        self.canvas = MplCanvas(figsize=(7.4, 5.6))
        self.canvas_container.addWidget(StyledNavToolbar(self.canvas, self))
        self.canvas_container.addWidget(self.canvas)

    def _preset_changed(self):
        key = self.preset.currentText()
        val = self.PRESETS[key]
        self.len_slider.setEnabled(val is None)
        if val is not None:
            self.len_slider.setValue(int(val * 100))
        self.update_plot()

    def _tick(self):
        self.t += 0.18
        self.update_plot()

    def update_plot(self):
        if not hasattr(self, "canvas"):
            return
        ax = self.canvas.ax
        ax.clear()
        L = self.len_slider.value() / 100.0  # l/λ
        k = 2 * np.pi
        z = np.linspace(-L / 2, L / 2, 600)
        env = np.sin(k * (L / 2 - np.abs(z)))      # στιγμιαία περιβάλλουσα ρεύματος
        I = env * np.cos(self.t)                    # χρονική ταλάντωση

        ax.axhline(0, color=theme.GRID, lw=1)
        # το σύρμα
        ax.plot([-L / 2, L / 2], [0, 0], color=theme.TEXT, lw=6, solid_capstyle="round",
                zorder=1, alpha=0.5)
        # σημείο τροφοδοσίας
        ax.plot(0, 0, "o", color=theme.ACCENT3, ms=9, zorder=5, label="τροφοδοσία")

        ax.fill_between(z, 0, I, color=theme.ACCENT, alpha=0.35)
        ax.plot(z, I, color=theme.ACCENT, lw=2.5, label="I(z', t)")
        if self.chk_envelope.isChecked():
            ax.plot(z, np.abs(env), color=theme.ACCENT2, lw=1.4, ls="--", label="|I| περιβάλλουσα")
            ax.plot(z, -np.abs(env), color=theme.ACCENT2, lw=1.4, ls="--")

        if self.chk_charge.isChecked():
            # δεσμίδες φορτίου ανά λ/2 (διαφορά προσήμου)
            n_half = int(L / 0.5)
            for i in range(n_half + 1):
                zc = -L / 2 + i * 0.5
                if -L / 2 <= zc <= L / 2:
                    sign = "+" if i % 2 == 0 else "−"
                    col = theme.ACCENT4 if i % 2 == 0 else theme.ACCENT3
                    ax.annotate(sign, (zc, 0.0), color=col, fontsize=16, ha="center",
                                va="center", fontweight="bold")

        ax.set_xlim(-max(L / 2, 0.3) * 1.15, max(L / 2, 0.3) * 1.15)
        ax.set_ylim(-1.25, 1.25)
        ax.set_xlabel("θέση κατά μήκος z' (σε λ)")
        ax.set_ylabel("κανονικ. ρεύμα I/I₀")
        ax.set_title(f"Κατανομή ρεύματος — l = {L:.2f} λ")
        ax.legend(loc="upper right", facecolor=theme.BG_PANEL, edgecolor=theme.GRID,
                  labelcolor=theme.TEXT, fontsize=9)

        # ενημερωτικό κείμενο
        if abs(L - 0.5) < 0.03:
            msg = "l = λ/2: μέγιστο ρεύμα στο κέντρο ⇒ R_in = R_r = 73 Ω."
        elif abs(L - 1.0) < 0.04:
            msg = "l = λ: μηδέν ρεύμα στο κέντρο ⇒ R_in → ∞ (δύο ημικύκλια αντίθετης φάσης)."
        elif L < 0.15:
            msg = "l ≪ λ: σχεδόν τριγωνική κατανομή (μέγιστο κέντρο, μηδέν στα άκρα)."
        elif L > 1.4:
            msg = "l = 3λ/2: τρία ημιτονοειδή τμήματα ⇒ πολυλοβικό διάγραμμα."
        else:
            msg = "Ημιτονοειδής κατανομή· μηδενισμός πάντα στα ανοιχτά άκρα."
        self.info.setText("ℹ " + msg)

        self.canvas.refresh()
