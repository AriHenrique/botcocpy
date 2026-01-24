# Preparação para Compilação em .exe

## ✅ O que foi implementado

### 1. Sistema de Recursos Embutidos
- ✅ Estrutura `bot_coc/resources/` para recursos embutidos
- ✅ `ResourceManager` para gerenciar recursos
- ✅ Detecção automática de ADB (embutido ou sistema)
- ✅ Suporte para execução como .exe

### 2. Detecção Automática de ADB
O sistema agora procura ADB na seguinte ordem:
1. **Recursos embutidos**: `bot_coc/resources/adb/adb.exe`
2. **Sistema**: `C:\android\platform-tools\adb.exe`
3. **PATH**: ADB disponível no PATH do sistema

### 3. Caminhos Dinâmicos
- ✅ Todos os caminhos agora são relativos ao projeto
- ✅ Suporte para execução como .exe (detecta automaticamente)
- ✅ Recursos são extraídos automaticamente quando necessário

## 📁 Estrutura de Recursos

```
bot_coc/
└── resources/
    ├── adb/
    │   ├── adb.exe              ← ADB principal
    │   ├── AdbWinApi.dll        ← DLLs necessárias
    │   └── AdbWinUsbApi.dll
    └── adb_scripts/
        ├── minitouch            ← Binário genérico
        ├── Normal1.BlueStacks5.minitouch
        └── ... (outros binários)
```

## 🚀 Como Preparar para .exe

### Passo 1: Copiar ADB e Scripts

Execute o script de setup:
```bash
python scripts/setup_resources.py
```

Ou copie manualmente:
- `adb.exe` → `bot_coc/resources/adb/adb.exe`
- `AdbWinApi.dll` → `bot_coc/resources/adb/AdbWinApi.dll`
- `AdbWinUsbApi.dll` → `bot_coc/resources/adb/AdbWinUsbApi.dll`
- Todos os `.minitouch` → `bot_coc/resources/adb_scripts/`

### Passo 2: Compilar

Use o spec file fornecido:
```bash
pyinstaller build_exe.spec
```

## 📋 O que está incluído no .exe

- ✅ Todos os módulos Python
- ✅ ADB e DLLs (se copiados para resources/)
- ✅ Scripts minitouch (se copiados para resources/)
- ✅ Templates de imagens
- ✅ Configurações
- ✅ Traduções (locales)

## ⚠️ Limitações

- **BlueStacks**: Precisa estar instalado no sistema (não pode ser embutido)
- **Primeira execução**: Pode ser lenta (extração de recursos)
- **Tamanho**: O .exe será grande (~100-200MB)

## 🔧 Configuração Automática

O sistema detecta automaticamente:
- Se está rodando como .exe (`sys.frozen`)
- Onde estão os recursos
- Qual ADB usar (embutido ou sistema)

Não é necessário configurar nada manualmente!
