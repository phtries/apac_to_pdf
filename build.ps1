Write-Host "============================================" -ForegroundColor Cyan
Write-Host " GERADOR DE EXE - APAC FISICA POR REMESSA" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

if (!(Test-Path "main.py")) {
    Write-Host "ERRO: main.py nao encontrado. Execute este script dentro da pasta do projeto." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python nao encontrado no PATH." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "[2/5] Instalando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
}
python -m pip install --upgrade pyinstaller

Write-Host "[3/5] Limpando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

Write-Host "[4/5] Gerando executavel pelo arquivo .spec..." -ForegroundColor Yellow
python -m PyInstaller .\Gerador_APAC_Fisica.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao gerar o executavel." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "[5/5] Copiando pastas editaveis para dist..." -ForegroundColor Yellow
if (Test-Path "data") { Copy-Item "data" "dist\data" -Recurse -Force }
if (Test-Path "assets") { Copy-Item "assets" "dist\assets" -Recurse -Force }
if (!(Test-Path "dist\output")) { New-Item -ItemType Directory -Path "dist\output" | Out-Null }

Write-Host ""
Write-Host "EXE GERADO COM SUCESSO!" -ForegroundColor Green
Write-Host "Arquivo:" -ForegroundColor Green
Write-Host "$PSScriptRoot\dist\Gerador_APAC_Fisica.exe" -ForegroundColor Green
Write-Host ""
Write-Host "As pastas data e assets ficaram fora do EXE." -ForegroundColor Cyan
Write-Host "Voce pode editar procedimentos.csv, medicos.csv e estabelecimentos.csv sem recompilar." -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para sair"
