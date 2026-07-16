@echo off
call .venv\Scripts\activate.bat
python -m automation.executar_automacao --arquivo dados\estornos_exemplo.xlsx --visivel --tentativas 2

