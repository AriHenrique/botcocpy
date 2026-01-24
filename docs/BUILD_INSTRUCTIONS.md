# Instruções para Compilar em .exe

## Pré-requisitos

1. Python 3.10+ instalado
2. PyInstaller: `pip install pyinstaller`
3. ADB instalado no sistema (ou binários copiados)

## Passo 1: Preparar Recursos

Execute o script de setup para copiar ADB e scripts:

```bash
python scripts/setup_resources.py
```

Este script irá:
- Copiar `adb.exe` para `bot_coc/resources/adb/`
- Copiar scripts do minitouch para `bot_coc/resources/adb_scripts/`
- Copiar DLLs necessárias do ADB

**Importante**: Se o ADB não for encontrado automaticamente, copie manualmente:
- `adb.exe` → `bot_coc/resources/adb/adb.exe`
- `AdbWinApi.dll` → `bot_coc/resources/adb/AdbWinApi.dll`
- `AdbWinUsbApi.dll` → `bot_coc/resources/adb/AdbWinUsbApi.dll`

## Passo 2: Verificar Estrutura

Certifique-se de que a estrutura está assim:

```
bot_coc/
├── resources/
│   ├── adb/
│   │   ├── adb.exe
│   │   ├── AdbWinApi.dll
│   │   └── AdbWinUsbApi.dll
│   └── adb_scripts/
│       ├── minitouch
│       ├── Normal1.BlueStacks5.minitouch
│       └── ... (outros binários)
├── ...
```

## Passo 3: Compilar

### Opção 1: Usar o spec file (Recomendado)

```bash
pyinstaller build_exe.spec
```

### Opção 2: Comando direto

```bash
pyinstaller --name=BotCOC ^
    --onefile ^
    --windowed ^
    --add-data "bot_coc/resources;resources" ^
    --add-data "templates;templates" ^
    --add-data "config;config" ^
    --add-data "locales;locales" ^
    --hidden-import=bot_coc ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    main_new.py
```

## Passo 4: Testar

O executável será gerado em `dist/BotCOC.exe`

Teste executando:
```bash
dist\BotCOC.exe
```

## Estrutura do .exe

Quando compilado, o .exe incluirá:
- ✅ Todos os módulos Python
- ✅ ADB e DLLs (em resources/adb/)
- ✅ Scripts minitouch (em resources/adb_scripts/)
- ✅ Templates de imagens
- ✅ Configurações
- ✅ Traduções (locales)

## Resolução de Problemas

### ADB não encontrado
- Verifique se `bot_coc/resources/adb/adb.exe` existe
- Execute `scripts/setup_resources.py` novamente

### Minitouch não encontrado
- Verifique se os binários estão em `bot_coc/resources/adb_scripts/`
- Copie manualmente de `adb.scripts/` se necessário

### Erro ao executar .exe
- Execute com `--console` para ver erros
- Verifique se todas as dependências estão incluídas
- Teste em uma máquina limpa

## Notas Importantes

1. **BlueStacks**: O caminho do BlueStacks ainda precisa estar instalado no sistema
   - Não é possível embutir o BlueStacks no .exe
   - O usuário precisa ter BlueStacks instalado

2. **Primeira Execução**: O .exe pode ser lento na primeira execução
   - PyInstaller extrai arquivos temporariamente
   - Execuções subsequentes são mais rápidas

3. **Antivírus**: Alguns antivírus podem detectar o .exe como suspeito
   - Isso é comum com executáveis Python
   - Considere assinar digitalmente o .exe

4. **Tamanho**: O .exe será grande (~100-200MB)
   - Inclui Python, OpenCV, NumPy, etc.
   - Use `--onefile` para um único arquivo ou `--onedir` para pasta
