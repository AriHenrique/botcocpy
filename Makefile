.PHONY: install run build clean lint format test exe

# Instalar dependencias
install:
	poetry install

# Rodar o bot
run:
	poetry run python main.py

# Rodar o exe
exe:
	.\dist\BotCOC.exe

# Compilar para .exe
build: lint clean
	poetry run pyinstaller --onefile --windowed --name BotCOC \
		--add-data "templates;templates" \
		--add-data "locales;locales" \
		--add-data "config;config" \
		--add-data "resources;resources" \
		main.py

# Lint com ruff
lint:
	poetry run ruff check bot ui functions main.py

# Formatar com black e ruff
format:
	poetry run black bot ui functions main.py
	poetry run ruff check --fix bot ui functions main.py

# Rodar testes
test:
	poetry run pytest tests -v

# Limpar arquivos de build
clean:
	cmd /c "if exist build rmdir /s /q build"
	cmd /c "if exist dist rmdir /s /q dist"
	cmd /c "if exist .pytest_cache rmdir /s /q .pytest_cache"
	cmd /c "if exist __pycache__ rmdir /s /q __pycache__"
	cmd /c "if exist bot\__pycache__ rmdir /s /q bot\__pycache__"
	cmd /c "if exist ui\__pycache__ rmdir /s /q ui\__pycache__"
	cmd /c "if exist functions\__pycache__ rmdir /s /q functions\__pycache__"
	cmd /c "if exist tests\__pycache__ rmdir /s /q tests\__pycache__"
	cmd /c "del /q *.spec 2>nul || exit /b 0"
