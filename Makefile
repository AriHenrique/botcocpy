# Makefile para compilação do Bot COC em .exe
# Uso: make build ou make all

.PHONY: help build clean setup test install-deps check-deps

# Variáveis
POETRY := poetry
PYTHON := poetry run python
PIP := poetry run pip
PYINSTALLER := poetry run pyinstaller
PROJECT_NAME := BotCOC
BUILD_DIR := build
DIST_DIR := dist
SPEC_FILE := build_exe.spec
RESOURCES_DIR := resources
ADB_DIR := $(RESOURCES_DIR)/adb
ADB_SCRIPTS_DIR := adb.scripts
SETUP_SCRIPT := scripts/setup_resources.py

# Cores removidas - não funcionam bem no PowerShell do Windows
# Use texto simples para compatibilidade

help:
	@echo.
	@echo === Bot COC - Makefile ===
	@echo.
	@echo Comandos disponiveis:
	@echo   make help          - Mostra esta ajuda
	@echo   make check-deps    - Verifica dependencias
	@echo   make install-deps   - Instala dependencias necessarias
	@echo   make setup         - Prepara recursos (ADB, scripts)
	@echo   make build         - Compila o projeto em .exe
	@echo   make clean         - Remove arquivos de build
	@echo   make test          - Testa o executavel gerado
	@echo   make all           - Executa tudo (setup + build)
	@echo.

check-deps:
	@echo Verificando Poetry...
	@$(POETRY) --version >nul 2>&1 || (echo ERRO: Poetry nao encontrado! Instale: https://python-poetry.org/docs/#installation && exit 1)
	@echo [OK] Poetry encontrado
	@echo Verificando dependencias do projeto...
	@$(POETRY) check >nul 2>&1 || (echo [AVISO] Executando poetry install... && $(POETRY) install)
	@$(PYTHON) -c "import sys; print(f'Python: {sys.version}')" || (echo ERRO: Python nao encontrado! && exit 1)
	@$(PYTHON) -c "import PyInstaller" 2>nul || (echo ERRO: PyInstaller nao encontrado! Execute: make install-deps && exit 1)
	@echo [OK] PyInstaller encontrado
	@$(PYTHON) -c "import cv2" 2>nul || (echo [AVISO] OpenCV nao encontrado)
	@$(PYTHON) -c "import numpy" 2>nul || (echo [AVISO] NumPy nao encontrado)
	@$(PYTHON) -c "import PIL" 2>nul || (echo [AVISO] Pillow nao encontrado)
	@echo [OK] Dependencias verificadas

install-deps:
	@echo Instalando dependencias com Poetry...
	@$(POETRY) install
	@echo [OK] Dependencias instaladas

setup:
	@echo Preparando recursos...
	@if not exist "$(RESOURCES_DIR)" mkdir "$(RESOURCES_DIR)"
	@if not exist "$(ADB_DIR)" mkdir "$(ADB_DIR)"
	@if not exist "$(ADB_SCRIPTS_DIR)" mkdir "$(ADB_SCRIPTS_DIR)"
	@$(PYTHON) $(SETUP_SCRIPT)
	@echo [OK] Recursos preparados

check-resources:
	@echo Verificando recursos...
	@if not exist "$(ADB_DIR)\adb.exe" (echo [AVISO] ADB nao encontrado em $(ADB_DIR) && echo Execute: make setup) else (echo [OK] ADB encontrado)
	@if not exist "$(ADB_SCRIPTS_DIR)" (echo [AVISO] Scripts ADB nao encontrados em $(ADB_SCRIPTS_DIR)) else (echo [OK] Scripts ADB encontrados)

build: setup check-deps check-resources
	@echo.
	@echo === Compilando projeto ===
	@echo.
	@if not exist "$(SPEC_FILE)" (echo ERRO: Arquivo $(SPEC_FILE) nao encontrado! && exit 1)
	@echo Executando PyInstaller...
	@$(PYINSTALLER) --clean $(SPEC_FILE)
	@if exist "$(DIST_DIR)\$(PROJECT_NAME).exe" (echo [OK] Compilacao concluida! && echo Executavel: $(DIST_DIR)\$(PROJECT_NAME).exe) else (echo ERRO: Erro na compilacao && exit 1)
	@echo.

clean:
	@echo Limpando arquivos de build...
	@if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
	@if exist "$(DIST_DIR)" rmdir /s /q "$(DIST_DIR)"
	@if exist "__pycache__" rmdir /s /q "__pycache__"
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@echo [OK] Limpeza concluida
	@echo Nota: build_exe.spec mantido no root (arquivo de configuracao)

test:
	@echo Testando executavel...
	@if not exist "$(DIST_DIR)\$(PROJECT_NAME).exe" (echo ERRO: Executavel nao encontrado! Execute: make build && exit 1)
	@echo [OK] Executavel encontrado: $(DIST_DIR)\$(PROJECT_NAME).exe
	@echo Execute manualmente para testar: $(DIST_DIR)\$(PROJECT_NAME).exe

all: setup build
	@echo.
	@echo === Compilacao completa! ===
	@echo Executavel gerado em: $(DIST_DIR)\$(PROJECT_NAME).exe
	@echo.

# Alias para comandos comuns
compile: build
rebuild: clean build
full: clean all
