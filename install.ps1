# ============================
# Minitouch Setup - BlueStacks x86_64 (Robust)
# ============================

$ADB = "C:\android\platform-tools\adb.exe"
$DEVICE = "127.0.0.1:5556"
$BIN_URL = "https://github.com/DeviceFarmer/minitouch/releases/latest/download/minitouch-x86_64"
$LOCAL_BIN = "$PSScriptRoot\minitouch_bin"
$REMOTE_BIN = "/data/local/tmp/minitouch"

Write-Host "=== MINITOUCH SETUP ==="

# ----- Check ADB -----
if (!(Test-Path $ADB)) {
    Write-Host "[ERROR] ADB não encontrado em $ADB"
    exit 1
}

# ----- Start ADB -----
Write-Host "[ADB] Starting server..."
& $ADB start-server | Out-Null

# ----- Connect Device -----
Write-Host "[ADB] Connecting to BlueStacks..."
& $ADB connect $DEVICE | Out-Null

$devices = & $ADB devices
if (-not ($devices | Select-String $DEVICE)) {
    Write-Host "[ERROR] BlueStacks não conectado ($DEVICE não aparece em adb devices)"
    Write-Host $devices
    exit 1
}

Write-Host "[OK] Device conectado: $DEVICE"

# ----- Cleanup old bin on device -----
Write-Host "[ADB] Limpando binário antigo no Android..."
& $ADB -s $DEVICE shell rm -rf $REMOTE_BIN | Out-Null

# ----- Download binary (robust) -----
Write-Host "[NET] Baixando minitouch x86_64..."

$downloaded = $false

# 1) curl.exe normal
try {
    & curl.exe -L $BIN_URL -o $LOCAL_BIN
    if (Test-Path $LOCAL_BIN) { $downloaded = $true }
} catch {}

# 2) curl.exe com HTTP/1.1 (proxy/firewall)
if (-not $downloaded) {
    try {
        Write-Host "[NET] Tentando com --http1.1..."
        & curl.exe -L --http1.1 $BIN_URL -o $LOCAL_BIN
        if (Test-Path $LOCAL_BIN) { $downloaded = $true }
    } catch {}
}

# 3) Fallback PowerShell
if (-not $downloaded) {
    try {
        Write-Host "[NET] Tentando Invoke-WebRequest..."
        Invoke-WebRequest $BIN_URL -OutFile $LOCAL_BIN
        if (Test-Path $LOCAL_BIN) { $downloaded = $true }
    } catch {}
}

if (-not $downloaded) {
    Write-Host "[ERROR] Falha ao baixar binário após múltiplas tentativas"
    Write-Host "Baixe manualmente em:"
    Write-Host "https://github.com/DeviceFarmer/minitouch/releases/latest"
    Write-Host "E salve como: $LOCAL_BIN"
    exit 1
}

# ----- Validate file -----
$size = (Get-Item $LOCAL_BIN).Length
Write-Host "[NET] Binário baixado: $size bytes"

if ($size -lt 100000) {
    Write-Host "[ERROR] Arquivo muito pequeno (provável HTML/redirect)."
    Write-Host "Baixe manualmente e tente novamente."
    exit 1
}

# ----- Push to device -----
Write-Host "[ADB] Enviando binário para Android..."
& $ADB -s $DEVICE push $LOCAL_BIN $REMOTE_BIN

# ----- Permissions -----
Write-Host "[ADB] Ajustando permissões..."
& $ADB -s $DEVICE shell chmod 755 $REMOTE_BIN

# ----- Run minitouch -----
Write-Host "[ADB] Iniciando minitouch..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`"$ADB -s $DEVICE shell $REMOTE_BIN`""

# ----- Forward socket -----
Start-Sleep -Seconds 2
Write-Host "[ADB] Forward socket tcp:1111 -> localabstract:minitouch"
& $ADB -s $DEVICE forward tcp:1111 localabstract:minitouch

Write-Host "=== SETUP FINALIZADO ==="
Write-Host "Se aparecer na nova janela:"
Write-Host "Type B protocol"
Write-Host "Max contacts: X"
Write-Host "Então o minitouch iniciou corretamente."
