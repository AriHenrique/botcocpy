# Como Instalar Make no Windows

## 🚀 Instalação Automática (Recomendado)

Execute o script de instalação:

```powershell
.\scripts\install_make.ps1
```

O script tentará instalar Make automaticamente usando Chocolatey ou Scoop, se disponíveis.

## 📦 Opções de Instalação

### Opção 1: Chocolatey (Mais Fácil)

#### Passo 1: Instalar Chocolatey

Abra PowerShell **como Administrador** e execute:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### Passo 2: Instalar Make

```powershell
choco install make -y
```

#### Passo 3: Verificar

```powershell
make --version
```

### Opção 2: Scoop

#### Passo 1: Instalar Scoop

Abra PowerShell e execute:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

#### Passo 2: Instalar Make

```powershell
scoop install make
```

#### Passo 3: Verificar

```powershell
make --version
```

### Opção 3: Download Manual (GnuWin32)

1. **Baixar Make:**
   - Acesse: https://sourceforge.net/projects/gnuwin32/files/make/
   - Baixe o instalador (ex: `make-3.81.exe`)

2. **Instalar:**
   - Execute o instalador
   - Instale em: `C:\Program Files (x86)\GnuWin32\`

3. **Adicionar ao PATH:**
   - Abra "Variáveis de Ambiente" (Win + R → `sysdm.cpl` → Avançado)
   - Edite a variável `Path`
   - Adicione: `C:\Program Files (x86)\GnuWin32\bin`
   - Reinicie o terminal

4. **Verificar:**
   ```cmd
   make --version
   ```

### Opção 4: WSL (Windows Subsystem for Linux)

Se você tem WSL instalado:

```bash
# No WSL
sudo apt-get update
sudo apt-get install make
```

**Nota:** Isso só funciona dentro do WSL, não no Windows nativo.

## ✅ Verificação

Após instalar, verifique se Make está funcionando:

```cmd
make --version
```

Você deve ver algo como:
```
GNU Make 4.3
```

## 🎯 Alternativa: Usar PowerShell Makefile

**Você NÃO precisa instalar Make!** O projeto já inclui `Makefile.ps1` que funciona nativamente no Windows:

```powershell
# Funciona sem Make instalado
.\Makefile.ps1 build
.\Makefile.ps1 all
```

## 🔧 Solução de Problemas

### Erro: "make não é reconhecido"

1. **Verifique se está no PATH:**
   ```powershell
   $env:Path -split ';' | Select-String "make"
   ```

2. **Reinicie o terminal** após instalar

3. **Adicione manualmente ao PATH** se necessário

### Erro: "Acesso negado" ao instalar Chocolatey

- Execute PowerShell **como Administrador**

### Chocolatey não instala

- Verifique conexão com internet
- Execute: `choco install make -y --force`

## 📝 Recomendação

Para este projeto, **não é necessário instalar Make**. Use o `Makefile.ps1` que já está incluído:

```powershell
.\Makefile.ps1 all
```

Isso funciona nativamente no Windows sem dependências adicionais!

## 🎉 Pronto!

Após instalar Make (ou usar Makefile.ps1), você pode compilar o projeto:

```bash
# Com Make instalado
make all

# Ou com PowerShell (sem Make)
.\Makefile.ps1 all
```
