# Guia de Compilação - Bot COC

## 🚀 Compilação Rápida

### Windows (PowerShell - Recomendado)

```powershell
# Compilar tudo (setup + build)
.\Makefile.ps1 all

# Ou passo a passo
.\Makefile.ps1 setup      # Prepara recursos
.\Makefile.ps1 build     # Compila
```

**Nota:** Este Makefile funciona **sem instalar Make**! É um script PowerShell nativo.

### Windows (CMD)

```cmd
# Usa PowerShell automaticamente
make.bat all

# Ou diretamente
make.bat setup
make.bat build
```

### Windows (Make - se instalado)

```bash
# Requer GnuWin32 Make ou similar
make all
```

## 📋 Comandos Disponíveis

### Comandos Básicos

| Comando | Descrição |
|---------|-----------|
| `help` | Mostra ajuda |
| `check-deps` | Verifica dependências instaladas |
| `install-deps` | Instala PyInstaller e dependências |
| `setup` | Prepara recursos (ADB, scripts) |
| `build` | Compila o projeto em .exe |
| `clean` | Remove arquivos de build |
| `test` | Verifica se executável foi gerado |
| `all` | Executa setup + build |
| `rebuild` | Limpa e compila novamente |
| `full` | Limpa, setup e compila |

## 🔧 Pré-requisitos

1. **Python 3.10+** instalado
2. **PowerShell** (Windows 10+ já inclui)
3. **ADB** instalado no sistema (ou copiado para `bot_coc/resources/adb/`)

**Nota:** Não é necessário instalar Make! O `Makefile.ps1` funciona nativamente no Windows.

## 📦 Instalação de Dependências

```powershell
# Instala tudo automaticamente
.\Makefile.ps1 install-deps

# Ou manualmente
pip install pyinstaller opencv-python numpy pillow
```

## 🏗️ Processo de Compilação

### 1. Preparar Recursos

```powershell
.\Makefile.ps1 setup
```

Este comando:
- Cria diretórios `bot_coc/resources/`
- Copia ADB de locais comuns
- Copia scripts minitouch de `adb.scripts/`

### 2. Verificar Dependências

```powershell
.\Makefile.ps1 check-deps
```

Verifica se:
- Python está instalado
- PyInstaller está instalado
- OpenCV, NumPy, Pillow estão instalados

### 3. Compilar

```powershell
.\Makefile.ps1 build
```

Gera o executável em `dist/BotCOC.exe`

### 4. Testar

```powershell
.\Makefile.ps1 test
```

Verifica se o executável foi gerado corretamente.

## 🎯 Compilação Completa (Um Comando)

```powershell
.\Makefile.ps1 all
```

Executa automaticamente:
1. Setup de recursos
2. Verificação de dependências
3. Compilação
4. Confirmação

## 🧹 Limpeza

```powershell
# Remove arquivos de build
.\Makefile.ps1 clean

# Limpa e recompila
.\Makefile.ps1 rebuild
```

## 📁 Estrutura de Build

```
projeto/
├── build/              ← Arquivos temporários (pode ser deletado)
├── dist/               ← Executável final
│   └── BotCOC.exe
├── build_exe.spec      ← Configuração PyInstaller
└── bot_coc/
    └── resources/      ← Recursos embutidos
        ├── adb/
        └── adb_scripts/
```

## ⚠️ Solução de Problemas

### Erro: "PyInstaller não encontrado"

```powershell
.\Makefile.ps1 install-deps
```

### Erro: "ADB não encontrado"

```powershell
# Copia ADB automaticamente
.\Makefile.ps1 setup

# Ou copie manualmente para bot_coc/resources/adb/adb.exe
```

### Erro: "Módulo não encontrado"

```powershell
# Instala dependências faltantes
pip install <modulo>
```

### Executável não funciona

1. Verifique logs em `logs/`
2. Execute com console para ver erros:
   ```powershell
   # Edite build_exe.spec e mude console=False para console=True
   pyinstaller build_exe.spec
   ```

## 🔍 Verificação Manual

Se preferir compilar manualmente:

```powershell
# 1. Preparar recursos
python scripts\setup_resources.py

# 2. Compilar
pyinstaller build_exe.spec

# 3. Executar
.\dist\BotCOC.exe
```

## 📝 Notas

- O executável será grande (~100-200MB) devido às dependências
- Primeira execução pode ser lenta (extração de recursos)
- BlueStacks ainda precisa estar instalado no sistema
- Antivírus pode detectar como suspeito (falso positivo comum)

## 🎉 Pronto!

Após a compilação, o executável estará em:
```
dist\BotCOC.exe
```

Copie este arquivo para onde quiser usar o bot!
