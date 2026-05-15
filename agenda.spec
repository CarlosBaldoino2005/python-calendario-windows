# -*- mode: python ; coding: utf-8 -*-
"""
Arquivo de configuração do PyInstaller para gerar o executável Agenda.exe.

PyInstaller empacota Python + bibliotecas + main.py em um único .exe para Windows.
Execute: pyinstaller agenda.spec
"""

from PyInstaller.utils.hooks import collect_all  # Coleta arquivos de um pacote pip

# Listas que o PyInstaller inclui no .exe
datas = []       # Arquivos de dados (imagens, temas, etc.)
binaries = []    # DLLs e bibliotecas nativas
hiddenimports = [  # Módulos importados dinamicamente que o analisador não vê
    "win32com.client",   # Outlook COM
    "win32timezone",
    "pywintypes",
    "babel",             # Localização de datas
    "babel.numbers",
    "babel.dates",
    "tkcalendar",        # Calendário popup no formulário
    "winrt.windows.applicationmodel.appointments",  # Calendário WinRT
    "winrt.windows.foundation",
    "winrt.windows.foundation.collections",
]

# Inclui todos os arquivos de customtkinter e tkcalendar (temas, fontes, etc.)
for pkg in ("customtkinter", "tkcalendar"):
    tmp = collect_all(pkg)
    datas += tmp[0]
    binaries += tmp[1]
    hiddenimports += tmp[2]

# Analysis: analisa main.py e dependências para montar o pacote
a = Analysis(
    ["main.py"],           # Script de entrada
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)  # Arquivo zip interno com bytecode Python

# EXE: gera um único executável com tudo embutido
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Agenda",              # Nome do arquivo: Agenda.exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                   # Comprime o executável (se UPX estiver instalado)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # False = app com janela, sem terminal preto
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                  # Caminho para .ico se quiser ícone personalizado
)
