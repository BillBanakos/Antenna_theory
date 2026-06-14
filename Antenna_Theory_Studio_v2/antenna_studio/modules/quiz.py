"""
Quiz Mode — αυτο-παραγόμενες ερωτήσεις εξάσκησης με σκορ.
ΣΗΜΑΝΤΙΚΟ: δεν υπάρχουν αποθηκευμένα θέματα εξετάσεων ή λυμένες ασκήσεις.
Κάθε ερώτηση παράγεται δυναμικά με τυχαίες παραμέτρους και η σωστή απάντηση
υπολογίζεται live από το core/formulas.py. Οι περισπασμοί (λάθος επιλογές)
παράγονται αλγοριθμικά.
"""

import random
import numpy as np
from PyQt5.QtWidgets import (QLabel, QPushButton, QComboBox, QWidget, QVBoxLayout,
                             QButtonGroup)
from PyQt5.QtCore import Qt

from ..core.mpl_canvas import ModulePage
from ..core import theme
from ..core import formulas as F


# ---------- βοηθητικά παραγωγής επιλογών ----------
def _opts_numeric(correct, fmt, spread=(0.55, 0.78, 1.4), unit=""):
    """Φτιάχνει 4 επιλογές: τη σωστή + 3 περισπασμούς πολλαπλασιαστικά."""
    vals = [correct]
    for s in spread:
        v = correct * s
        if all(abs(v - x) > abs(correct) * 0.08 + 1e-9 for x in vals):
            vals.append(v)
    while len(vals) < 4:
        vals.append(correct * random.uniform(0.3, 2.2))
    labels = [fmt.format(v) + unit for v in vals]
    correct_label = labels[0]
    random.shuffle(labels)
    return labels, labels.index(correct_label)


def _opts_choices(correct, distractors):
    opts = [correct] + distractors
    random.shuffle(opts)
    return opts, opts.index(correct)


# ---------- γεννήτριες ερωτήσεων ----------
def q_dipole_rin():
    L = random.choice([0.25, 0.5, 0.75])
    Rin = F.dipole_input_resistance(L)
    opts, ci = _opts_numeric(Rin, "{:.0f}", unit=" Ω")
    return (f"Ποια είναι η αντίσταση εισόδου ενός διπόλου μήκους l = {L:g}λ;",
            opts, ci,
            f"R_in = R_r,max/sin²(πl/λ) = {Rin:.1f} Ω. (λ/2→73 Ω, 3λ/4→372 Ω).")


def q_uniform_sll():
    return ("Ποια η στάθμη του 1ου πλευρικού λοβού μιας ΟΜΟΙΟΜΟΡΦΗΣ στοιχειοκεραίας;",
            *_opts_choices("≈ −13.5 dB", ["≈ −20 dB", "≈ −26 dB", "≈ −3 dB"]),
            "Η ομοιόμορφη διέγερση δίνει πάντα ~−13.5 dB ανεξαρτήτως N.")


def q_no_sidelobes():
    return ("Ποια κατανομή διέγερσης ΔΕΝ έχει πλευρικούς λοβούς (για d≤λ/2);",
            *_opts_choices("Διωνυμική (binomial)",
                           ["Ομοιόμορφη", "Dolph–Tschebyscheff", "Τριγωνική"]),
            "Η διωνυμική εξαλείφει τους πλευρικούς, με κόστος ευρύτερο κύριο λοβό.")


def q_far_field():
    D = round(random.uniform(2, 8), 1)
    lam = 1.0
    R2 = F.far_field_distance(D, lam)
    opts, ci = _opts_numeric(R2, "{:.1f}", unit=" λ")
    return (f"Κεραία διάστασης D = {D:g}λ: από ποια απόσταση αρχίζει το μακρινό πεδίο;",
            opts, ci, f"R ≥ 2D²/λ = {R2:.1f} λ (κριτήριο σφάλματος φάσης π/8).")


def q_patch_W():
    fr = random.choice([2e9, 5e9, 10e9])
    er = random.choice([2.2, 4.4, 10.2])
    W = F.patch_design(fr, er, 1.27e-3)["W"] * 100
    opts, ci = _opts_numeric(W, "{:.2f}", unit=" cm")
    return (f"Πλάτος W ορθογώνιου patch στα {fr/1e9:g} GHz με εr={er};",
            opts, ci, "W = (c/2fr)·√(2/(εr+1)).")


def q_polarization():
    cases = [
        ((1, 1, 0), "Γραμμική"),
        ((1, 1, 90), "Κυκλική"),
        ((1, 0.5, 45), "Ελλειπτική"),
        ((1, 0, 0), "Γραμμική"),
    ]
    (ex, ey, dphi), _ = random.choice(cases)
    typ, _sense = F.classify_polarization(ex, ey, np.radians(dphi))
    short = typ.split(" ")[0]
    others = [s for s in ["Γραμμική", "Κυκλική", "Ελλειπτική"] if s != short]
    return (f"Πόλωση για Ex₀={ex}, Ey₀={ey}, Δφ={dphi}°;",
            *_opts_choices(short, others),
            "Ίσα πλάτη + Δφ=±90°→κυκλική· Δφ=0/180°→γραμμική· αλλιώς ελλειπτική.")


def q_endfire():
    return ("Ποια προοδευτική φάση β δίνει end-fire (μέγιστο στους 0°);",
            *_opts_choices("β = −kd", ["β = 0", "β = +kd/2", "β = π"]),
            "End-fire: β=∓kd ώστε ψ=0 στη διεύθυνση του άξονα.")


def q_image():
    return ("Κατακόρυφο δίπολο πάνω από τέλειο αγωγό (PEC): πρόσημο ειδώλου;",
            *_opts_choices("+1 (σε φάση)", ["−1 (αντίθετη φάση)", "0", "±j"]),
            "PEC: κατακόρυφο →+1, οριζόντιο →−1.")


def q_dolph_tradeoff():
    return ("Αυξάνοντας την καταστολή πλευρικών σε σχεδίαση Dolph, ο κύριος λοβός:",
            *_opts_choices("διευρύνεται", ["στενεύει", "μένει ίδιος", "εξαφανίζεται"]),
            "Υπάρχει αντιστάθμιση: χαμηλότεροι πλευρικοί ⇒ ευρύτερη δέσμη (f>1).")


def q_directivity_cosn():
    n = random.choice([2, 4, 6, 8])
    th = np.linspace(1e-3, np.pi / 2, 1000)
    U = np.cos(th) ** (2 * n)
    th_full = np.linspace(1e-3, np.pi, 2000)
    U_full = np.where(th_full <= np.pi / 2, np.cos(th_full) ** (2 * n), 0.0)
    D0 = F.directivity_numerical(U_full, th_full)
    opts, ci = _opts_numeric(D0, "{:.1f}")
    return (f"Κατευθυντικότητα διαγράμματος U=cos^{2*n}θ (άνω ημισφαίριο);",
            opts, ci, f"D₀ = 4π·Umax/∫∫U dΩ ≈ {D0:.2f} = {10*np.log10(D0):.1f} dBi.")


GENERATORS = {
    "Όλα": None,
    "Κεφ. 2 — Παράμετροι": [q_far_field, q_polarization, q_directivity_cosn],
    "Κεφ. 4 — Δίπολα": [q_dipole_rin, q_image],
    "Κεφ. 6 — Στοιχειοκεραίες": [q_uniform_sll, q_no_sidelobes, q_endfire, q_dolph_tradeoff],
    "Κεφ. 14 — Patch": [q_patch_W],
}
ALL_GENS = [g for v in GENERATORS.values() if v for g in v]


class QuizMode(ModulePage):
    TITLE = "Quiz · Εξάσκηση με Σκορ (αυτο-παραγόμενες ερωτήσεις)"
    SUBTITLE = ("Οι ερωτήσεις παράγονται δυναμικά από τη μηχανή τύπων με τυχαίες "
                "τιμές — άπειρη εξάσκηση, χωρίς αποθηκευμένα θέματα.")

    def build_controls(self, form):
        self.cat = QComboBox(); self.cat.addItems(list(GENERATORS.keys()))
        self.cat.currentIndexChanged.connect(self._restart)
        form.addRow(QLabel("Κατηγορία:"), self.cat)

        self.score_lbl = QLabel()
        self.score_lbl.setStyleSheet(
            f"font-size:14px; background:{theme.BG_BASE}; border:1px solid {theme.GRID};"
            f"border-radius:6px; padding:10px; margin-top:6px;")
        form.addRow(self.score_lbl)

        self.next_btn = QPushButton("Επόμενη ερώτηση →")
        self.next_btn.clicked.connect(self._next)
        form.addRow(self.next_btn)

        self.reset_btn = QPushButton("↺ Μηδενισμός σκορ")
        self.reset_btn.clicked.connect(self._restart)
        form.addRow(self.reset_btn)

        self.add_theory(
            "Διάλεξε απάντηση: πράσινο=σωστό, κόκκινο=λάθος.<br>"
            "Κάθε «Επόμενη» δημιουργεί νέα ερώτηση με νέες τιμές.")
        self._correct = 0
        self._total = 0

    def build_canvas(self):
        host = QWidget()
        self.qlayout = QVBoxLayout(host)
        self.qlayout.setContentsMargins(10, 10, 10, 10)
        self.qlayout.setSpacing(10)

        self.q_label = QLabel()
        self.q_label.setWordWrap(True)
        self.q_label.setStyleSheet(
            f"font-size:17px; color:{theme.TEXT}; background:{theme.BG_PANEL};"
            f"border:1px solid {theme.ACCENT}; border-radius:8px; padding:16px;")
        self.qlayout.addWidget(self.q_label)

        self.opt_btns = []
        self.opt_group = QButtonGroup(host)
        for i in range(4):
            b = QPushButton()
            b.setMinimumHeight(46)
            b.setStyleSheet(self._opt_style())
            b.clicked.connect(lambda _, idx=i: self._answer(idx))
            self.opt_btns.append(b)
            self.qlayout.addWidget(b)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.feedback.setStyleSheet(f"font-size:13px; color:{theme.TEXT_DIM}; padding:6px;")
        self.qlayout.addWidget(self.feedback)
        self.qlayout.addStretch()

        self.canvas_container.addWidget(host)
        self._restart()

    def _opt_style(self, bg=None, border=None):
        bg = bg or theme.BG_BASE
        border = border or theme.GRID
        return (f"QPushButton {{ text-align:left; padding:10px 16px; font-size:15px;"
                f"color:{theme.TEXT}; background:{bg}; border:1px solid {border};"
                f"border-radius:8px; }}"
                f"QPushButton:hover {{ border-color:{theme.ACCENT}; }}")

    def _gen_pool(self):
        sel = GENERATORS[self.cat.currentText()]
        return sel if sel else ALL_GENS

    def _restart(self):
        self._correct = 0
        self._total = 0
        if hasattr(self, "q_label"):
            self._next()
        if hasattr(self, "score_lbl"):
            self._update_score()

    def _update_score(self):
        pct = (100 * self._correct / self._total) if self._total else 0
        self.score_lbl.setText(
            f"<b>Σκορ:</b> {self._correct} / {self._total}  "
            f"<span style='color:{theme.ACCENT}'>({pct:.0f}%)</span>")

    def _next(self):
        gen = random.choice(self._gen_pool())
        q, opts, ci, expl = gen()
        self._answer_idx = ci
        self._expl = expl
        self._answered = False
        self.q_label.setText(q)
        for i, b in enumerate(self.opt_btns):
            if i < len(opts):
                b.setText(opts[i]); b.setEnabled(True); b.show()
                b.setStyleSheet(self._opt_style())
            else:
                b.hide()
        self.feedback.setText("")
        self._update_score()

    def _answer(self, idx):
        if getattr(self, "_answered", False):
            return
        self._answered = True
        self._total += 1
        if idx == self._answer_idx:
            self._correct += 1
            self.opt_btns[idx].setStyleSheet(self._opt_style(theme.GOOD, theme.GOOD))
            self.feedback.setText(f"<b style='color:{theme.GOOD}'>Σωστό!</b>  {self._expl}")
        else:
            self.opt_btns[idx].setStyleSheet(self._opt_style(theme.DANGER, theme.DANGER))
            self.opt_btns[self._answer_idx].setStyleSheet(self._opt_style(theme.GOOD, theme.GOOD))
            self.feedback.setText(f"<b style='color:{theme.DANGER}'>Λάθος.</b>  {self._expl}")
        for b in self.opt_btns:
            b.setEnabled(False)
        self._update_score()

    def update_plot(self):
        pass
