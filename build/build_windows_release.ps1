# Genera BogotaSAE.exe (PyInstaller) y, si existe Inno Setup, el instalador Setup.exe.
#
# Requisito instalador: Inno Setup 6 (gratis) desde https://jrsoftware.org/isinfo.php
#
# Uso (desde la raíz del repo):
#   powershell -ExecutionPolicy Bypass -File build/build_windows_release.ps1
#
# workpath/distpath van a %TEMP% para evitar bloqueos de OneDrive en build/build_windows.

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Work = Join-Path $env:TEMP "bogota-sae-pyi-work"
$DistTemp = Join-Path $env:TEMP "bogota-sae-pyi-dist"
$Release = Join-Path $Root "release"

function Find-InnoCompiler {
    $candidates = @(
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 5\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 5\ISCC.exe")
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

Write-Host "Instalando PyInstaller si hace falta..."
py -m pip install "pyinstaller>=6.0.0" -q

Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $DistTemp -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $Release | Out-Null

Set-Location $Root
Write-Host "Compilando ejecutable (workpath en TEMP)..."
py -m PyInstaller (Join-Path $Root "build\build_windows.spec") `
    --workpath $Work `
    --distpath $DistTemp `
    --noconfirm

$Exe = Join-Path $DistTemp "BogotaSAE.exe"
if (-not (Test-Path $Exe)) {
    throw "No se generó BogotaSAE.exe en $DistTemp"
}

Copy-Item -Force $Exe (Join-Path $Release "BogotaSAE.exe")

$Zip = Join-Path $Release "BogotaSAE_Windows_x64.zip"
if (Test-Path $Zip) { Remove-Item $Zip }
Compress-Archive -Path $Exe -DestinationPath $Zip -Force

Write-Host ""
Write-Host "Ejecutable y ZIP:"
Write-Host "  $(Join-Path $Release 'BogotaSAE.exe')"
Write-Host "  $Zip"

$iscc = Find-InnoCompiler
$iss = Join-Path $Root "build\BogotaSAE_Setup.iss"
if ($iscc -and (Test-Path $iss)) {
    Write-Host ""
    Write-Host "Compilando instalador con Inno Setup..."
    & $iscc $iss
    $setup = Get-ChildItem -Path $Release -Filter "BogotaSAE_Setup_*.exe" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($setup) {
        Write-Host "Instalador listo para subir:"
        Write-Host "  $($setup.FullName)"
    }
} else {
    Write-Host ""
    Write-Host "AVISO: No se encontró ISCC.exe (Inno Setup)."
    Write-Host "Instale Inno Setup 6 desde https://jrsoftware.org/isinfo.php"
    Write-Host "y vuelva a ejecutar este script, o compile manualmente:"
    Write-Host "  `"$iss`" con ISCC.exe"
}
