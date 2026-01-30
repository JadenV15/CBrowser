@echo off

call .\venv\Scripts\activate.bat

pyinstaller --clean --noconfirm ComplXBrowser.spec

call .\venv\Scripts\deactivate.bat
pause