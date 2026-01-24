# Arquivos no Root - Explicação

## Por que alguns arquivos estão no root?

O root do projeto contém apenas arquivos essenciais e entry points. Aqui está a explicação:

## Entry Points (Recomendados)

Estes são os pontos de entrada recomendados:

- **run_bot.py** - Executar bot (recomendado)
- **run_gui.py** - Executar interface gráfica (recomendado)

**Uso:**
```bash
python run_bot.py     # Executar bot
python run_gui.py     # Abrir interface gráfica
```

## Entry Points Legados (Mantidos para compatibilidade)

- **main.py** - Entry point legado (usa código antigo)
- **main_new.py** - Entry point legado (usa estrutura POO)

**Nota:** Estes arquivos são mantidos para compatibilidade, mas `run_bot.py` e `run_gui.py` são os recomendados.

## Wrappers de Compatibilidade (Mantidos no root)

Estes arquivos são wrappers que mantêm compatibilidade com código legado:

- **android.py** - Wrapper para `bot_coc.core.device_manager.DeviceManager`
- **vision.py** - Wrapper para `bot_coc.core.vision_engine.VisionEngine`
- **config.py** - Configuração legada (será deprecada)
- **i18n.py** - Wrapper para `bot_coc.utils.i18n.I18n`
- **logger.py** - Wrapper para `bot_coc.utils.logger.BotLogger`

**Por que estão no root?**
- Permitem que código antigo continue funcionando
- Facilitam migração gradual
- Evitam quebrar imports existentes

**Exemplo:**
```python
# Código antigo ainda funciona
from android import AndroidDevice
from vision import find_template

# Mas o recomendado é:
from bot_coc.core.device_manager import DeviceManager
from bot_coc.core.vision_engine import VisionEngine
```

## Arquivos de Configuração

- **pyproject.toml** - Configuração do projeto (Poetry)
- **poetry.lock** - Lock file do Poetry

## Documentação Principal

- **README.md** - Documentação principal e ponto de entrada

## Scripts Utilitários (Movidos para scripts/)

Estes foram movidos para `scripts/`:
- `grab_template.py` - Recortar templates
- `normalize_troop_names.py` - Normalizar nomes de arquivos
- `minitouch_client.py` - Cliente minitouch

**Uso:**
```bash
python scripts/grab_template.py
python scripts/normalize_troop_names.py
```

## Resumo

### ✅ Mantidos no Root
- Entry points (main.py, main_new.py, gui.py)
- Wrappers de compatibilidade
- Configuração do projeto (pyproject.toml)
- README.md

### 📁 Movidos para Diretórios
- Documentação → `docs/`
- Build files → `build/`
- Scripts utilitários → `scripts/`
- Código principal → `bot_coc/`

## Migração Futura

Eventualmente, os wrappers de compatibilidade podem ser removidos quando todo o código for migrado para a nova estrutura. Por enquanto, eles são mantidos para garantir compatibilidade.
