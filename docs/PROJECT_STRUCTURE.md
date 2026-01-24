# Estrutura do Projeto Bot COC

## 📁 Estrutura de Diretórios

```
bot_coc/
├── README.md                    # Documentação principal
├── main.py                      # Entry point legado
├── main_new.py                  # Entry point novo (recomendado)
├── gui.py                       # Interface gráfica
│
├── bot_coc/                     # Pacote principal
│   ├── core/                    # Lógica principal
│   │   ├── bot_controller.py
│   │   ├── device_manager.py
│   │   ├── army_manager.py
│   │   ├── game_actions.py
│   │   ├── vision_engine.py
│   │   └── bluestacks_manager.py
│   ├── ui/                      # Interface gráfica
│   │   └── (GUI será movida aqui)
│   ├── utils/                   # Utilitários
│   │   ├── logger.py
│   │   ├── i18n.py
│   │   ├── resource_manager.py
│   │   └── compat.py
│   ├── config/                  # Configurações
│   │   ├── settings.py
│   │   └── config_manager.py
│   └── resources/               # Recursos embutidos
│       ├── adb/
│       └── adb_scripts/
│
├── build/                       # Arquivos de build
│   ├── build_exe.spec
│   ├── build_exe_debug.spec
│   ├── Makefile
│   ├── Makefile.ps1
│   ├── make.bat
│   └── install_make.bat
│
├── docs/                        # Documentação
│   ├── ARCHITECTURE.md
│   ├── REFACTORING_SUMMARY.md
│   ├── README_BUILD.md
│   ├── BUILD_INSTRUCTIONS.md
│   ├── EXE_PREPARATION.md
│   ├── README_EXE.md
│   ├── INSTALL_MAKE.md
│   └── MIGRATION_GUIDE.md
│
├── scripts/                     # Scripts utilitários
│   ├── setup_resources.py
│   ├── install_make.ps1
│   └── install.ps1
│
├── templates/                   # Templates de imagens
│   ├── menu/
│   ├── troops/
│   ├── donate/
│   └── ...
│
├── config/                      # Configurações do usuário
│   └── army.json
│
├── locales/                     # Traduções
│   ├── pt-BR.json
│   └── en-US.json
│
├── adb.scripts/                 # Scripts ADB (originais)
│   └── *.minitouch
│
├── functions/                   # Funções legadas (compatibilidade)
│   ├── bluestacks_control.py
│   ├── create_army.py
│   ├── delete_army.py
│   └── donate.py
│
├── tests/                       # Testes (futuro)
│
└── logs/                        # Logs (gerado automaticamente)
    └── *.log
```

## 📄 Arquivos no Root

### Essenciais
- `README.md` - Documentação principal
- `main.py` - Entry point legado
- `main_new.py` - Entry point novo (recomendado)
- `gui.py` - Interface gráfica
- `pyproject.toml` - Configuração do projeto
- `poetry.lock` - Lock file do Poetry

### Compatibilidade (Wrappers)
- `android.py` - Wrapper para DeviceManager
- `vision.py` - Wrapper para VisionEngine
- `config.py` - Configuração legada
- `i18n.py` - Wrapper para I18n
- `logger.py` - Wrapper para BotLogger

### Utilitários
- `grab_template.py` - Ferramenta para recortar templates
- `normalize_troop_names.py` - Normalizar nomes de arquivos
- `minitouch_client.py` - Cliente minitouch

## 🗂️ Organização

### Diretórios Principais

1. **bot_coc/** - Código principal (nova estrutura POO)
2. **build/** - Arquivos de compilação
3. **docs/** - Documentação completa
4. **scripts/** - Scripts utilitários
5. **templates/** - Imagens de templates
6. **config/** - Configurações do usuário
7. **locales/** - Traduções
8. **functions/** - Código legado (mantido para compatibilidade)

### Arquivos Temporários (Gitignored)

- `screen.png` - Screenshot temporário
- `ui.xml` - Dump de UI temporário
- `swipe_script.txt` - Script temporário
- `zoom_script.txt` - Script temporário
- `__pycache__/` - Cache Python
- `build/` - Arquivos de build
- `dist/` - Executáveis gerados
- `logs/` - Arquivos de log

## 🔄 Migração

Para migrar código antigo:
- Use `bot_coc/utils/compat.py` para compatibilidade
- Veja `docs/MIGRATION_GUIDE.md` para detalhes

## 📝 Notas

- Arquivos no root são mantidos para compatibilidade ou são entry points
- Toda lógica principal está em `bot_coc/`
- Documentação está em `docs/`
- Build files estão em `build/`
