# Script para instalar Make no Windows
# Executa: .\scripts\install_make.ps1

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "=== Instalador de Make para Windows ==="
Write-Output ""

# Verifica se Make já está instalado
$makeInstalled = $false
try {
    $makeVersion = & make --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "✓ Make já está instalado!"
        Write-Output $makeVersion
        if (-not $Force) {
            Write-Output ""
            Write-ColorOutput Yellow "Use -Force para reinstalar"
            exit 0
        }
    }
} catch {
    # Make não encontrado, continuar
}

Write-Output "Verificando métodos de instalação disponíveis..."
Write-Output ""

# Método 1: Chocolatey
$chocoInstalled = $false
try {
    $chocoVersion = & choco --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $chocoInstalled = $true
        Write-ColorOutput Green "✓ Chocolatey encontrado: $chocoVersion"
    }
} catch {
    Write-ColorOutput Yellow "⚠ Chocolatey não encontrado"
}

# Método 2: Scoop
$scoopInstalled = $false
try {
    $scoopVersion = & scoop --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $scoopInstalled = $true
        Write-ColorOutput Green "✓ Scoop encontrado: $scoopVersion"
    }
} catch {
    Write-ColorOutput Yellow "⚠ Scoop não encontrado"
}

Write-Output ""

# Tentar instalar via Chocolatey
if ($chocoInstalled) {
    Write-ColorOutput Yellow "Instalando Make via Chocolatey..."
    try {
        & choco install make -y
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "✓ Make instalado com sucesso via Chocolatey!"
            
            # Atualizar PATH na sessão atual
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            # Verificar instalação
            Start-Sleep -Seconds 2
            $makeVersion = & make --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput Green "✓ Make funcionando!"
                Write-Output $makeVersion
                Write-Output ""
                Write-ColorOutput Green "Instalação concluída!"
                exit 0
            }
        }
    } catch {
        Write-ColorOutput Red "✗ Erro ao instalar via Chocolatey: $_"
    }
}

# Tentar instalar via Scoop
if ($scoopInstalled) {
    Write-ColorOutput Yellow "Instalando Make via Scoop..."
    try {
        & scoop install make
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "✓ Make instalado com sucesso via Scoop!"
            
            # Verificar instalação
            Start-Sleep -Seconds 2
            $makeVersion = & make --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput Green "✓ Make funcionando!"
                Write-Output $makeVersion
                Write-Output ""
                Write-ColorOutput Green "Instalação concluída!"
                exit 0
            }
        }
    } catch {
        Write-ColorOutput Red "✗ Erro ao instalar via Scoop: $_"
    }
}

# Se nenhum gerenciador de pacotes disponível, mostrar instruções
Write-Output ""
Write-ColorOutput Yellow "=== Nenhum gerenciador de pacotes encontrado ==="
Write-Output ""
Write-ColorOutput Cyan "Opções de instalação:"
Write-Output ""
Write-ColorOutput Green "OPÇÃO 1: Instalar Chocolatey (Recomendado)"
Write-Output "  1. Abra PowerShell como Administrador"
Write-Output "  2. Execute:"
Write-Output "     Set-ExecutionPolicy Bypass -Scope Process -Force;"
Write-Output "     [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;"
Write-Output "     iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
Write-Output "  3. Execute novamente este script"
Write-Output ""
Write-ColorOutput Green "OPÇÃO 2: Instalar Scoop"
Write-Output "  1. Abra PowerShell"
Write-Output "  2. Execute:"
Write-Output "     Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"
Write-Output "     irm get.scoop.sh | iex"
Write-Output "  3. Execute novamente este script"
Write-Output ""
Write-ColorOutput Green "OPÇÃO 3: Download Manual (GnuWin32)"
Write-Output "  1. Baixe de: https://sourceforge.net/projects/gnuwin32/files/make/"
Write-Output "  2. Instale o pacote"
Write-Output "  3. Adicione ao PATH: C:\Program Files (x86)\GnuWin32\bin"
Write-Output ""
Write-ColorOutput Green "OPÇÃO 4: Usar PowerShell Makefile (Não requer Make)"
Write-Output "  O projeto já inclui Makefile.ps1 que funciona sem Make!"
Write-Output "  Use: .\Makefile.ps1 build"
Write-Output ""

# Perguntar se quer instalar Chocolatey
$response = Read-Host "Deseja instalar Chocolatey agora? (S/N)"
if ($response -eq "S" -or $response -eq "s") {
    Write-ColorOutput Yellow "Instalando Chocolatey..."
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        Write-ColorOutput Green "✓ Chocolatey instalado!"
        Write-ColorOutput Yellow "Reinicie o PowerShell e execute este script novamente"
    } catch {
        Write-ColorOutput Red "✗ Erro ao instalar Chocolatey: $_"
        Write-Output "Execute manualmente como Administrador"
    }
}

Write-Output ""
Write-ColorOutput Yellow "Nota: Você pode usar .\Makefile.ps1 sem instalar Make!"
