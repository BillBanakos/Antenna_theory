"""
Βήμα-προς-βήμα Υπολογισμοί (live).
Δείχνει τον ΕΝΕΡΓΟ τύπο σε LaTeX, αντικαθιστά τις τρέχουσες τιμές των ολισθητών
και εμφανίζει το αποτέλεσμα. Δεν περιέχει αποθηκευμένες/λυμένες ασκήσεις — όλα
υπολογίζονται δυναμικά από τη μηχανή τύπων (core/formulas.py).
"""

import numpy as np
from PyQt5.QtWidgets import QLabel, QComboBox, QWidget, QFormLayout

from ..core.mpl_canvas import ModulePage, labeled_slider
from ..core.equation import EquationView
from ..core import theme
from ..core import formulas as F


class DerivationStudio(ModulePage):
    TITLE = "Βήμα-προς-Βήμα · Ζωντανοί Υπολογισμοί (LaTeX)"
    SUBTITLE = ("Ο ενεργός τύπος, με αντικατάσταση των τρεχουσών τιμών και αποτέλεσμα. "
                "Άλλαξε τους ολισθητές και δες πώς προκύπτει το νούμερο.")

    # κάθε θέμα: (όνομα, [(key,label,lo,hi,val,scale,fmt,suffix)], compute)
    def _topics(self):
        return [
            ("Δίπολο — αντίσταση εισόδου", [
                ("L", "Μήκος l/λ:", 5, 145, 50, 0.01, "{:.2f}", " λ")],
             self._dipole),
            ("Microstrip patch — διαστάσεις", [
                ("fr", "Συχνότητα fr:", 5, 200, 20, 0.1, "{:.1f}", " GHz"),
                ("er", "εr:", 10, 120, 102, 0.1, "{:.1f}", ""),
                ("h", "Ύψος h:", 20, 320, 127, 0.01, "{:.2f}", " mm")],
             self._patch),
            ("Friis — λόγος ισχύος", [
                ("f", "Συχνότητα:", 1, 300, 24, 0.1, "{:.1f}", " GHz"),
                ("R", "Απόσταση R:", 1, 5000, 1000, 1.0, "{:.0f}", " m"),
                ("Gt", "Gt:", 0, 40, 15, 1.0, "{:.0f}", " dBi"),
                ("Gr", "Gr:", 0, 40, 15, 1.0, "{:.0f}", " dBi")],
             self._friis),
            ("Κατευθυντικότητα — Kraus", [
                ("h1", "HPBW E-plane:", 1, 180, 40, 1.0, "{:.0f}", "°"),
                ("h2", "HPBW H-plane:", 1, 180, 40, 1.0, "{:.0f}", "°")],
             self._kraus),
            ("Όριο far-field", [
                ("D", "Διάσταση D/λ:", 10, 300, 50, 0.1, "{:.1f}", " λ")],
             self._farfield),
            ("Dolph–Tschebyscheff — x₀", [
                ("N", "Στοιχεία N:", 3, 21, 5, 1.0, "{:.0f}", ""),
                ("sll", "Στάθμη πλευρικών:", 20, 60, 30, 1.0, "{:.0f}", " dB")],
             self._dolph),
        ]

    def build_controls(self, form):
        self.topics = self._topics()
        self.topic = QComboBox()
        self.topic.addItems([t[0] for t in self.topics])
        self.topic.currentIndexChanged.connect(self._rebuild_params)
        form.addRow(QLabel("Υπολογισμός:"), self.topic)

        # δυναμικό panel παραμέτρων
        self.param_host = QWidget()
        self.param_form = QFormLayout(self.param_host)
        self.param_form.setContentsMargins(0, 0, 0, 0)
        form.addRow(self.param_host)
        self.sliders = {}

        self.add_theory(
            "Όλα υπολογίζονται live από τους ίδιους τύπους που τροφοδοτούν τα γραφήματα.<br>"
            "Καμία αποθηκευμένη/λυμένη άσκηση — μόνο ο τύπος και οι τρέχουσες τιμές.")
        self._rebuild_params()

    def build_canvas(self):
        self.eqview = EquationView(figsize=(6.6, 5.4))
        self.canvas_container.addWidget(self.eqview)

    def _rebuild_params(self):
        # καθάρισε παλιούς ολισθητές
        while self.param_form.count():
            item = self.param_form.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        self.sliders = {}
        _, params, _ = self.topics[self.topic.currentIndex()]
        for key, label, lo, hi, val, scale, fmt, suffix in params:
            s, _ = labeled_slider(self.param_form, label, lo, hi, val,
                                  scale=scale, fmt=fmt, suffix=suffix,
                                  on_change=lambda v: self.update_plot())
            self.sliders[key] = (s, scale)
        self.update_plot()

    def _val(self, key):
        s, scale = self.sliders[key]
        return s.value() * scale

    def update_plot(self):
        if not hasattr(self, "eqview") or not self.sliders:
            return
        compute = self.topics[self.topic.currentIndex()][2]
        try:
            lines = compute()
        except Exception as e:
            lines = [("Σφάλμα", "title"), (str(e), "note")]
        self.eqview.show_lines(lines)

    # ---------------- θέματα (μόνο live υπολογισμός) ----------------
    def _dipole(self):
        L = self._val("L")
        s2 = np.sin(np.pi * L) ** 2
        Rr = F.dipole_radiation_resistance(L)
        Rin = F.dipole_input_resistance(L)
        rin_txt = "∞" if not np.isfinite(Rin) else f"{Rin:.2f}\\,\\Omega"
        return [
            ("Αντίσταση εισόδου διπόλου", "title"),
            (r"$R_{in}=\dfrac{R_{r,\max}}{\sin^2(kl/2)},\ \ kl/2=\pi\,l/\lambda$", "eq"),
            (r"$l/\lambda=%.2f\Rightarrow \sin^2(\pi l/\lambda)=%.4f$" % (L, s2), "sub"),
            (r"$R_{r,\max}=%.2f\,\Omega$  (μέσω $S_i,C_i$)" % Rr, "sub"),
            (r"$R_{in}=%s$" % rin_txt, "result"),
            ("Έλεγχος: λ/2→73 Ω, 3λ/4→372 Ω, λ→∞", "note"),
        ]

    def _patch(self):
        fr = self._val("fr") * 1e9
        er = self._val("er")
        h = self._val("h") * 1e-3
        d = F.patch_design(fr, er, h)
        return [
            ("Διαστάσεις ορθογώνιου patch", "title"),
            (r"$W=\dfrac{c}{2f_r}\sqrt{\dfrac{2}{\varepsilon_r+1}}=%.3f$ cm" % (d["W"] * 100), "eq"),
            (r"$\varepsilon_{reff}=\dfrac{\varepsilon_r+1}{2}+\dfrac{\varepsilon_r-1}{2}"
             r"\left(1+12\,h/W\right)^{-1/2}=%.3f$" % d["eps_reff"], "sub"),
            (r"$\Delta L=0.412\,h\,\dfrac{(\varepsilon_{reff}+0.3)(W/h+0.264)}"
             r"{(\varepsilon_{reff}-0.258)(W/h+0.8)}=%.4f$ cm" % (d["dL"] * 100), "sub"),
            (r"$L=\dfrac{c}{2f_r\sqrt{\varepsilon_{reff}}}-2\Delta L=%.3f$ cm" % (d["L"] * 100), "result"),
            ("fr=%.2f GHz, εr=%.1f, h=%.2f mm" % (fr / 1e9, er, h * 1e3), "note"),
        ]

    def _friis(self):
        f = self._val("f") * 1e9
        R = self._val("R")
        Gt = 10 ** (self._val("Gt") / 10)
        Gr = 10 ** (self._val("Gr") / 10)
        lam = F.C0 / f
        ratio = F.friis_pr_pt(lam, R, Gt, Gr)
        fsl = F.free_space_loss_db(lam, R)
        return [
            ("Εξίσωση Friis", "title"),
            (r"$\dfrac{P_r}{P_t}=G_t\,G_r\left(\dfrac{\lambda}{4\pi R}\right)^2$", "eq"),
            (r"$\lambda=c/f=%.2f$ mm,  $R=%.0f$ m" % (lam * 1e3, R), "sub"),
            (r"$\mathrm{FSL}=20\log_{10}(4\pi R/\lambda)=%.1f$ dB" % fsl, "sub"),
            (r"$P_r/P_t=%.1f$ dB" % (10 * np.log10(ratio)), "result"),
            ("Διπλασιασμός R ⇒ −6 dB (Friis)", "note"),
        ]

    def _kraus(self):
        h1 = self._val("h1"); h2 = self._val("h2")
        D0 = F.directivity_kraus(h1, h2)
        return [
            ("Κατευθυντικότητα — προσέγγιση Kraus", "title"),
            (r"$D_0\approx\dfrac{41253}{\Theta_{1d}\,\Theta_{2d}}$  (δέσμη-μολύβι)", "eq"),
            (r"$\Theta_{1d}=%.0f^\circ,\ \Theta_{2d}=%.0f^\circ$" % (h1, h2), "sub"),
            (r"$D_0=%.2f=%.2f$ dBi" % (D0, 10 * np.log10(D0)), "result"),
            ("Ισχύει μόνο για έναν στενό λοβό (όχι παντοκατευθυντικό)", "note"),
        ]

    def _farfield(self):
        D = self._val("D")  # σε λ
        R2 = F.far_field_distance(D, 1.0, np.pi / 8)
        R1 = F.field_regions(D, 1.0)[0]
        return [
            ("Όριο μακρινού πεδίου (Fraunhofer)", "title"),
            (r"$R\geq\dfrac{2D^2}{\lambda}$  (σφάλμα φάσης $\leq\pi/8$)", "eq"),
            (r"$D=%.1f\,\lambda$" % D, "sub"),
            (r"$R_1=0.62\sqrt{D^3/\lambda}=%.2f\,\lambda$" % R1, "sub"),
            (r"$R_{ff}=2D^2/\lambda=%.2f\,\lambda$" % R2, "result"),
        ]

    def _dolph(self):
        N = int(round(self._val("N")))
        sll = self._val("sll")
        coeffs, x0, R0 = F.dolph_tschebyscheff_coeffs(N, sll)
        return [
            ("Dolph–Tschebyscheff — παράμετρος x₀", "title"),
            (r"$R_0=10^{\,SLL/20},\ \ x_0=\cosh\!\left(\dfrac{\cosh^{-1}R_0}{N-1}\right)$", "eq"),
            (r"$N=%d,\ SLL=%.0f$ dB $\Rightarrow R_0=%.2f$" % (N, sll, R0), "sub"),
            (r"$x_0=%.4f$" % x0, "result"),
            ("Συντελεστές: " + ", ".join(f"{c:.2f}" for c in coeffs), "note"),
        ]
