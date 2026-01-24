# Arquitetura do Projeto Bot COC

## Visão Geral

O projeto foi reorganizado seguindo princípios de POO (Programação Orientada a Objetos) e boas práticas de manutenção de código.

## Estrutura de Diretórios

```
bot_coc/
├── __init__.py              # Pacote principal
├── core/                    # Lógica principal do bot
│   ├── __init__.py
│   ├── bot_controller.py   # Orquestrador principal
│   ├── device_manager.py   # Gerenciamento de dispositivo Android
│   ├── army_manager.py     # Gerenciamento de exército
│   ├── game_actions.py     # Ações do jogo
│   ├── vision_engine.py    # Motor de visão computacional
│   └── bluestacks_manager.py # Gerenciamento do BlueStacks
├── ui/                      # Interface gráfica
│   ├── __init__.py
│   └── gui.py              # Interface gráfica principal
├── utils/                   # Utilitários
│   ├── __init__.py
│   ├── logger.py           # Sistema de logs
│   ├── i18n.py             # Sistema de internacionalização
│   └── compat.py           # Camada de compatibilidade
└── config/                  # Configurações
    ├── __init__.py
    ├── settings.py         # Configurações e constantes
    └── config_manager.py   # Gerenciador de configurações

scripts/                     # Scripts utilitários
├── grab_template.py
└── normalize_troop_names.py

tests/                       # Testes (futuro)
```

## Princípios Aplicados

### 1. Single Responsibility Principle (SRP)
Cada classe tem uma única responsabilidade:
- `DeviceManager`: Comunicação com dispositivo Android
- `ArmyManager`: Gerenciamento de exército
- `GameActions`: Ações do jogo
- `VisionEngine`: Reconhecimento de imagens
- `BlueStacksManager`: Controle do emulador

### 2. Dependency Injection
Classes recebem dependências via construtor:
```python
army_manager = ArmyManager(device, config_manager)
```

### 3. Separation of Concerns
- **Core**: Lógica de negócio
- **UI**: Interface gráfica
- **Utils**: Utilitários compartilhados
- **Config**: Configurações centralizadas

### 4. Configuration Management
Todas as configurações centralizadas em `Settings` e `ConfigManager`.

## Classes Principais

### BotController
Orquestrador principal que coordena todas as operações do bot.

```python
bot = BotController()
bot.initialize_game()
bot.train_army()
bot.donate_to_castle()
```

### DeviceManager
Gerencia comunicação com dispositivo Android via ADB.

```python
device = DeviceManager(host="127.0.0.1", port="5556")
device.tap(x, y)
device.screenshot()
```

### ArmyManager
Gerencia operações relacionadas ao exército.

```python
army = ArmyManager(device, config_manager)
army.create_army()
army.delete_army()
army.train_army()
```

### GameActions
Gerencia ações do jogo.

```python
actions = GameActions(device)
actions.donate_castle()
actions.request_castle()
actions.init_game()
```

## Migração

### Código Antigo
```python
from android import AndroidDevice
from functions.create_army import create_army

device = AndroidDevice()
create_army(device)
```

### Código Novo
```python
from bot_coc.core.bot_controller import BotController

bot = BotController()
bot.create_army()
```

## Compatibilidade

O arquivo `bot_coc/utils/compat.py` fornece uma camada de compatibilidade para código legado:

```python
from bot_coc.utils.compat import AndroidDevice  # Funciona como antes
```

## Benefícios

1. **Manutenibilidade**: Código organizado e fácil de entender
2. **Testabilidade**: Classes isoladas são fáceis de testar
3. **Extensibilidade**: Fácil adicionar novas funcionalidades
4. **Reusabilidade**: Componentes podem ser reutilizados
5. **Clareza**: Responsabilidades bem definidas
