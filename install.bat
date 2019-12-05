@echo off
activate pps
pyinstaller --onefile --add-binary="libs/chromedriver.exe;libs" --add-binary="images/pps.ico;images" --icon images/pps.ico --distpath="." src/com/charlesmlin/pps_automator/pps.py
pause