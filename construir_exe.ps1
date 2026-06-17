# Genera GestorTaller.exe a partir del codigo fuente.
# Ejecutar desde la carpeta del proyecto, en PowerShell:
#     .\construir_exe.ps1
# Si PowerShell no deja ejecutar el script por la politica de seguridad, usa:
#     powershell -ExecutionPolicy Bypass -File .\construir_exe.ps1

# Instala PyInstaller la primera vez (si no esta ya instalado).
if (-not (pip show pyinstaller 2>$null)) {
    Write-Host "Instalando PyInstaller..." -ForegroundColor Cyan
    pip install pyinstaller
}

# Asegura las dependencias de la aplicacion.
pip install -r requirements.txt

# Genera el .exe usando la receta del .spec.
Write-Host "Generando el ejecutable..." -ForegroundColor Cyan
pyinstaller gestor_taller.spec

Write-Host ""
Write-Host "Listo. El ejecutable esta en:  dist\GestorTaller.exe" -ForegroundColor Green
