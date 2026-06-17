# -*- mode: python ; coding: utf-8 -*-
#
# Receta de PyInstaller para generar el ejecutable de GestorTaller.
#   Uso:        pyinstaller gestor_taller.spec
#   Resultado:  dist/GestorTaller.exe   (un único archivo, no necesita Python)
#
# En 'datas' meto dentro del .exe todo lo que la app necesita y que no es código
# Python: las plantillas HTML, los archivos estáticos (CSS/JS) y el esquema de la
# base de datos. La base de datos y las fotos NO van aquí: se crean en una carpeta
# 'datos' junto al .exe la primera vez que se abre (ver config.py).

a = Analysis(
    ["lanzar.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("static", "static"),
        ("modelos/esquema.sql", "modelos"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GestorTaller",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,            # deja la ventana de consola visible (se ve "en marcha")
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
