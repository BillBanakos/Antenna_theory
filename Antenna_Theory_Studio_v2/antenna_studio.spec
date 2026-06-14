# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec για standalone εκτελέσιμο του Antenna Theory Studio.
Χτίσιμο:  pyinstaller antenna_studio.spec
Παράγει:  dist/AntennaTheoryStudio(.exe)
"""

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'scipy.special', 'scipy.special._ufuncs',
        'matplotlib.backends.backend_qt5agg',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='AntennaTheoryStudio',
    debug=False, strip=False, upx=True, console=False,
)
