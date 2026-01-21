# Bot COC - Automação BlueStacks (ADB + OpenCV)

adb -s 127.0.0.1:5556 push .\adb.scripts\Normal1.BlueStacks5.minitouch /data/local/tmp/minitouch
adb -s 127.0.0.1:5556 shell chmod 755 /data/local/tmp/minitouch


## Requisitos
- Windows
- BlueStacks rodando
- ADB instalado em: C:\android\platform-tools\adb.exe
- Python 3.10+
- Dependências:
  pip install opencv-python numpy pillow

## Estrutura
- main.py -> fluxo do bot
- android.py -> controle ADB + visão
- vision.py -> OpenCV template matching
- grab_template.py -> ferramenta para recortar templates
- templates/ -> imagens dos botões

## Uso
1. Inicie o BlueStacks e abra o jogo uma vez
2. Rode:
   python grab_template.py
3. Recorte botões e salve em templates/
4. Edite main.py se quiser mudar o fluxo
5. Execute:
   python main.py

## Dicas
- Recorte só o botão/ícone
- Evite animações
- Use threshold 0.8-0.9
