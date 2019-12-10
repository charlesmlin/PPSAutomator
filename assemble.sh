#!/usr/bin/env bash 
source activate pps
scipy_path="$(pip show scipy | grep Location | awk '{print $NF}')\\scipy\\.libs"
pyinstaller --onefile --paths $scipy_path --add-binary="libs/*;libs" --add-binary="images/pps.ico;images" --add-binary="*.bat;." --hidden-import=tensorflow --hidden-import=sklearn --icon images/pps.ico --distpath="." src/com/charlesmlin/pps_automator/pps.py