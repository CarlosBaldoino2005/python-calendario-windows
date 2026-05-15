@echo off
cd /d "%~dp0"
echo Instalando PyInstaller...
python -m pip install pyinstaller -q
echo.
echo Gerando executavel...
python -m PyInstaller agenda.spec --noconfirm
echo.
if exist "dist\Agenda.exe" (
    echo Sucesso! Executavel em: dist\Agenda.exe
) else (
    echo Falha na geracao. Verifique os erros acima.
)
pause
