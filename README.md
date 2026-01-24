# Bot COC - Automação BlueStacks (ADB + OpenCV)

Bot para automação do Clash of Clans usando BlueStacks, ADB e OpenCV.

## 🚀 Início Rápido

### Interface Gráfica (Recomendado)

```bash
python run_gui.py
# ou
python -m bot_coc.ui.gui
```

### Linha de Comando

```bash
python run_bot.py
# ou
python main_new.py  # Entry point legado
```

## 📋 Requisitos

- Windows
- BlueStacks rodando
- ADB instalado (ou embutido em `bot_coc/resources/adb/`)
- Python 3.10+
- Dependências:
  ```bash
  pip install opencv-python numpy pillow
  ```

## 📁 Estrutura do Projeto

```
bot_coc/
├── README.md              # Este arquivo
├── main.py                # Entry point legado
├── main_new.py            # Entry point novo (recomendado)
├── gui.py                 # Interface gráfica
│
├── bot_coc/               # Pacote principal (POO)
│   ├── core/              # Lógica principal
│   ├── ui/                # Interface gráfica
│   ├── utils/             # Utilitários
│   ├── config/            # Configurações
│   └── resources/         # Recursos embutidos
│
├── docs/                   # Documentação completa
├── build/                  # Arquivos de compilação
├── scripts/                # Scripts utilitários
├── templates/              # Imagens de templates
├── config/                 # Configurações do usuário
└── locales/                # Traduções
```

**Veja `docs/PROJECT_STRUCTURE.md` para estrutura detalhada.**

## 📚 Documentação

Toda a documentação está em `docs/`:

- **docs/ARCHITECTURE.md** - Arquitetura do projeto
- **docs/README_BUILD.md** - Guia de compilação
- **docs/MIGRATION_GUIDE.md** - Guia de migração
- **docs/REFACTORING_SUMMARY.md** - Resumo da refatoração

## 🛠️ Compilação

Para compilar em .exe:

```powershell
# Usar Makefile PowerShell (recomendado)
.\build\Makefile.ps1 all

# Ou manualmente
pyinstaller build\build_exe.spec
```

Veja `docs/README_BUILD.md` para instruções completas.

## 🎯 Funcionalidades

- ✅ Automação completa do jogo
- ✅ Interface gráfica intuitiva
- ✅ Sistema de logs robusto
- ✅ Suporte multi-idioma (pt-BR, en-US)
- ✅ Compilação em .exe standalone
- ✅ Arquitetura POO bem organizada

## 📝 Uso

### Interface Gráfica

A GUI oferece:
- **Control Tab**: Controle do BlueStacks e ações do jogo
- **Settings Tab**: Configurações de ADB e visualização
- **Army Tab**: Configuração visual do exército
- **Log Tab**: Log de todas as operações
- **Menu Language**: Seletor de idioma

### Scripts Utilitários

```bash
# Normalizar nomes de arquivos PNG
python scripts/normalize_troop_names.py

# Recortar templates
python scripts/grab_template.py
```

## 🔧 Configuração

Edite `config/army.json` para configurar o exército.

## 📖 Mais Informações

- Veja `docs/` para documentação completa
- Veja `docs/ARCHITECTURE.md` para entender a estrutura
- Veja `docs/README_BUILD.md` para compilar

## 📄 Licença

Este projeto é para uso pessoal e educacional.
