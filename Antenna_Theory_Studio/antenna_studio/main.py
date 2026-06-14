"""
Antenna Theory Studio — κεντρικό παράθυρο.
Πλευρική πλοήγηση ανά κεφάλαιο (Balanis) + στοίβα σελίδων (lazy-loaded modules).
Εκτέλεση:  python -m antenna_studio.main   ή   python main.py
"""

import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QListWidget, QListWidgetItem,
                             QStackedWidget, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .core import theme
from .core.theme import DarkPalette, STYLESHEET

# --- modules ---
from .modules.ch1_radiation import Chapter1Radiation
from .modules.ch2_pattern import Chapter2Pattern
from .modules.ch2_regions import Chapter2Regions
from .modules.ch2_directivity import Chapter2Directivity
from .modules.ch2_polarization import Chapter2Polarization
from .modules.ch2_plf import Chapter2PLF
from .modules.ch2_friis import Chapter2Friis
from .modules.ch4_dipole import Chapter4Dipole
from .modules.ch4_image import Chapter4Image
from .modules.ch6_array import Chapter6Array
from .modules.ch6_synthesis import Chapter6Synthesis
from .modules.ch6_planar import Chapter6Planar
from .modules.ch14_patch import Chapter14Patch
from .modules.ch14_circular import Chapter14Circular
from .modules.mcq import MCQGallery


# Δομή πλοήγησης: (επικεφαλίδα κεφαλαίου, [(ετικέτα, κλάση), ...])
NAV = [
    ("ΚΕΦ. 1 — Κεραίες", [
        ("Μηχανισμός & ρεύμα", Chapter1Radiation),
    ]),
    ("ΚΕΦ. 2 — Θεμελιώδεις Παράμετροι", [
        ("Διάγραμμα ακτινοβολίας", Chapter2Pattern),
        ("Πεδιακές περιοχές", Chapter2Regions),
        ("Κατευθυντικότητα", Chapter2Directivity),
        ("Πόλωση (ζωντανή)", Chapter2Polarization),
        ("PLF — σύζευξη πόλωσης", Chapter2PLF),
        ("Friis & Ραντάρ (RCS)", Chapter2Friis),
    ]),
    ("ΚΕΦ. 4 — Γραμμικές Κεραίες", [
        ("Δίπολο & αντίσταση", Chapter4Dipole),
        ("Θεωρία ειδώλων", Chapter4Image),
    ]),
    ("ΚΕΦ. 6 — Στοιχειοκεραίες", [
        ("Ομοιόμορφη — Beamsteering", Chapter6Array),
        ("Σύνθεση (Binomial/Dolph)", Chapter6Synthesis),
        ("Επίπεδη M×N", Chapter6Planar),
    ]),
    ("ΚΕΦ. 14 — Μικροταινίας", [
        ("Σχεδιαστής patch", Chapter14Patch),
        ("Κυκλικό patch", Chapter14Circular),
    ]),
    ("ΠΟΛΛΑΠΛΗΣ ΕΠΙΛΟΓΗΣ", [
        ("Οπτικοποιητής εννοιών", MCQGallery),
    ]),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antenna Theory Studio — Balanis (Κεφ. 1,2,4,6,14)")
        self.resize(1480, 920)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------- αριστερή πλοήγηση ----------
        side = QWidget()
        side.setObjectName("Sidebar")
        side.setStyleSheet(f"#Sidebar {{ background:{theme.BG_PANEL}; }}")
        side.setFixedWidth(280)
        side_l = QVBoxLayout(side)
        side_l.setContentsMargins(12, 14, 12, 12)

        title = QLabel("📡 Antenna Theory Studio")
        title.setStyleSheet(f"color:{theme.ACCENT}; font-size:16px; font-weight:700;")
        side_l.addWidget(title)
        sub = QLabel("Διαδραστική οπτικοποίηση θεωρίας")
        sub.setStyleSheet(f"color:{theme.TEXT_DIM}; font-size:11px; margin-bottom:6px;")
        side_l.addWidget(sub)

        self.nav = QListWidget()
        self.nav.setStyleSheet(
            f"QListWidget {{ background:{theme.BG_PANEL}; border:none; outline:none; }}")
        side_l.addWidget(self.nav, stretch=1)

        self.stack = QStackedWidget()

        # ρητό mapping: nav_row -> stack_index, και nav_row -> κλάση (lazy)
        self._row_to_stack = {}
        self._factories = {}
        self._pages = {}

        for header, items in NAV:
            hdr = QListWidgetItem(header)
            hdr.setFlags(Qt.NoItemFlags)
            f = QFont(); f.setBold(True); f.setPointSize(9)
            hdr.setFont(f)
            hdr.setForeground(Qt.gray)
            self.nav.addItem(hdr)
            for label, cls in items:
                it = QListWidgetItem("   " + label)
                self.nav.addItem(it)
                row = self.nav.row(it)
                stack_idx = self.stack.count()
                self.stack.addWidget(QWidget())  # placeholder
                self._row_to_stack[row] = stack_idx
                self._factories[row] = cls
            # κενή γραμμή χωρισμού (χωρίς σελίδα)
            spacer = QListWidgetItem("")
            spacer.setFlags(Qt.NoItemFlags)
            self.nav.addItem(spacer)

        self.nav.currentRowChanged.connect(self._navigate)

        root.addWidget(side)
        root.addWidget(self.stack, stretch=1)

        # επιλογή πρώτης πραγματικής σελίδας
        for row in sorted(self._factories):
            self.nav.setCurrentRow(row)
            break

    def _navigate(self, row):
        if row not in self._factories:
            return
        stack_idx = self._row_to_stack[row]
        if row not in self._pages:  # lazy instantiation
            page = self._factories[row]()
            self._pages[row] = page
            old = self.stack.widget(stack_idx)
            self.stack.insertWidget(stack_idx, page)
            self.stack.removeWidget(old)
            old.deleteLater()
            stack_idx = self.stack.indexOf(page)
            self._row_to_stack[row] = stack_idx
        self.stack.setCurrentIndex(self._row_to_stack[row])


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
