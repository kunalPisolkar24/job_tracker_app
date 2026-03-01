VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help setup run-web run-desktop build-desktop clean

help:
	@echo "Available commands:"
	@echo "  make setup         Create virtual environment and install dependencies"
	@echo "  make run-web       Run the application in the web browser"
	@echo "  make run-desktop   Run the application as a desktop app"
	@echo "  make build-desktop Build a standalone executable for the desktop app"
	@echo "  make clean         Remove virtual environment, build artifacts, and caches"

$(VENV)/bin/activate: requirements.txt
	@python3 -m venv $(VENV) || (echo "Failed to create venv" && exit 1)
	@$(PIP) install --upgrade pip || (echo "Failed to upgrade pip" && exit 1)
	@$(PIP) install -r requirements.txt || (echo "Failed to install requirements" && exit 1)
	@touch $(VENV)/bin/activate

setup: $(VENV)/bin/activate

run-web: setup
	@$(PYTHON) -m streamlit run app.py

run-desktop: setup
	@$(PYTHON) desktop_app.py

build-desktop: setup
	@$(PYTHON) -m PyInstaller --onefile --windowed --name="JobTrackerExec" desktop_app.py

clean:
	@rm -rf $(VENV)
	@rm -rf build
	@rm -rf dist
	@rm -rf *.spec
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf src/__pycache__
	@rm -rf pages/__pycache__