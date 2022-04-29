import argparse
import subprocess
import os
import sys
import requests
import shutil
import wget
from pathlib import Path
from zipfile import ZipFile

print("Installing openscad requirements")
filename = wget.download("https://files.openscad.org/OpenSCAD-2021.01-x86-64.zip")
os.mkdir("openscad")
with ZipFile(filename, 'r') as scad:
    scad.extractall("openscad")

shutil.copy("curses_test.py", "testing/VCOS.py")
