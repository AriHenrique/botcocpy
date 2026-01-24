# Guia de Migração - android.py

## ✅ O que foi feito

### 1. DeviceManager Completo
O arquivo `bot_coc/core/device_manager.py` agora contém **TODOS** os métodos do `android.py` original:

- ✅ `tap()`, `swipe()`, `type()` - Input básico
- ✅ `screenshot()` - Captura de tela
- ✅ `open_app()` - Abrir aplicativo
- ✅ `center_view()` - Centralizar visualização
- ✅ `scroll_horizontal()` - Scroll horizontal
- ✅ `find_and_tap_with_scroll()` - Buscar e clicar com scroll
- ✅ `tap_image()` - Clicar em imagem
- ✅ `wait_image()` - Aguardar imagem aparecer
- ✅ `zoom_out()`, `zoom_in()` - Zoom com minitouch
- ✅ `dump_ui()`, `tap_text()` - UI automation
- ✅ Todos os métodos privados necessários

### 2. Compatibilidade Mantida
O arquivo `android.py` foi transformado em um **wrapper de compatibilidade**:

```python
# android.py agora é apenas um alias
from bot_coc.core.device_manager import DeviceManager
AndroidDevice = DeviceManager
```

**Código antigo continua funcionando:**
```python
from android import AndroidDevice  # ✅ Funciona!
device = AndroidDevice()           # ✅ Funciona!
device.tap(100, 200)                # ✅ Funciona!
```

### 3. Vision Engine Integrado
- `VisionEngine` integrado no `DeviceManager`
- `vision.py` também é um wrapper de compatibilidade
- Método `find_template()` mantém a mesma assinatura

## 🔄 Como Migrar

### Opção 1: Usar Código Antigo (Funciona)
```python
from android import AndroidDevice

device = AndroidDevice()
device.tap_image("menu/bt_army.png")
```

### Opção 2: Usar Nova Estrutura (Recomendado)
```python
from bot_coc.core.device_manager import DeviceManager

device = DeviceManager()
device.tap_image("menu/bt_army.png")
```

### Opção 3: Usar BotController (Mais Alto Nível)
```python
from bot_coc.core.bot_controller import BotController

bot = BotController()
bot.initialize_game()
bot.train_army()
```

## 📋 Checklist de Migração

- [x] DeviceManager completo com todos os métodos
- [x] android.py como wrapper de compatibilidade
- [x] vision.py como wrapper de compatibilidade
- [x] VisionEngine integrado
- [x] Todos os métodos testados e funcionando
- [x] Logs padronizados
- [x] Configurações centralizadas

## ⚠️ Avisos de Deprecation

O código antigo mostrará avisos de deprecation, mas continuará funcionando:

```python
DeprecationWarning: android.AndroidDevice is deprecated. 
Use bot_coc.core.device_manager.DeviceManager instead.
```

Para suprimir os avisos:
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

## 🎯 Benefícios da Nova Estrutura

1. **Organização**: Código em módulos bem definidos
2. **Manutenibilidade**: Fácil encontrar e modificar funcionalidades
3. **Testabilidade**: Classes isoladas são fáceis de testar
4. **Extensibilidade**: Fácil adicionar novas funcionalidades
5. **Compatibilidade**: Código antigo continua funcionando

## 📝 Notas Importantes

- O `android.py` antigo **não precisa ser deletado** - ele funciona como wrapper
- Todos os métodos têm a mesma assinatura
- O comportamento é idêntico ao original
- Logs são padronizados e melhorados
- Configurações são centralizadas em `Settings`
