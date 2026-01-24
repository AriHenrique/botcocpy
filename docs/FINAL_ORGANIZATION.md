# Organização Final do Projeto

## ✅ Arquivos Organizados

### GUI Movida
- ✅ `gui.py` → `bot_coc/ui/gui.py`
- ✅ Criado `run_gui.py` como entry point no root

### Bot Entry Point
- ✅ Criado `run_bot.py` como entry point recomendado
- ✅ `main_new.py` mantido no root para compatibilidade

## 📁 Estrutura Final do Root

### Entry Points Recomendados
- `run_bot.py` - Executar bot
- `run_gui.py` - Executar interface gráfica

### Entry Points Legados (Compatibilidade)
- `main.py` - Entry point legado
- `main_new.py` - Entry point legado

### Wrappers de Compatibilidade
- `android.py` - Wrapper para DeviceManager
- `vision.py` - Wrapper para VisionEngine
- `config.py` - Configuração legada
- `i18n.py` - Wrapper para I18n
- `logger.py` - Wrapper para BotLogger

### Configuração
- `pyproject.toml` - Configuração do projeto
- `poetry.lock` - Lock file

### Documentação
- `README.md` - Documentação principal

## 🎯 Como Usar

### Executar Bot
```bash
# Recomendado
python run_bot.py

# Ou legado
python main_new.py
```

### Executar GUI
```bash
# Recomendado
python run_gui.py

# Ou como módulo
python -m bot_coc.ui.gui
```

## 📂 Estrutura de Código

```
bot_coc/
├── run_bot.py              # Entry point bot (recomendado)
├── run_gui.py              # Entry point GUI (recomendado)
├── main.py                 # Entry point legado
├── main_new.py            # Entry point legado
│
├── bot_coc/
│   ├── ui/
│   │   └── gui.py         # Interface gráfica (movida)
│   ├── core/              # Lógica principal
│   ├── utils/             # Utilitários
│   └── config/            # Configurações
│
├── scripts/                # Scripts utilitários
├── docs/                   # Documentação
└── build/                  # Build files
```

## ✨ Benefícios

1. **Organização**: GUI agora está em `bot_coc/ui/` onde deveria estar
2. **Entry Points Claros**: `run_bot.py` e `run_gui.py` são fáceis de encontrar
3. **Compatibilidade**: Código legado continua funcionando
4. **Estrutura POO**: Código organizado seguindo princípios OOP
