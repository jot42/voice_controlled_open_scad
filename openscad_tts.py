import argparse
import os
import platform
import subprocess
import subprocess

import speech_recognition as sr

from config import *
from openscad_runner import RenderMode, OpenScadRunner
from vcos_commands import *

#Parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Opens VCOS configuration menu'      , required=False, action='store_true')
parser.add_argument('-f', '--file'  , help='Specifies a file to be opened'      , required=False, nargs=1) 
args = parser.parse_args()

if args.config:
    config_mode()

#Detect Operating System
version = ""

if platform.system() == 'Linux':
    version = "L"
elif platform.system() == 'Darwin':
    version = "M"
elif platform.system() == "Windows":
    version = "W"

def update_screen(version):
    if version == "W":
        os.system('cls')
    else:
        os.system('clear')
    
    print("######################")
    print("# VCOS - Version ", version, " #")
    print("#####################################")
    print("# Say 'help' for a list of commands #")
    print("#####################################")

def start_vcos(version, path):

    file_location_temp = ""

    loaded_file = ""
    temp_file = ""
    openscad_path = path
    calibration = 0

    #Calibrate microphone
    # calibration = calibrate_mic()

    #Display main screen
    update_screen(version)

    #Run main voice detection loop
    while True:
        var = record_audio()

        if var == "load":
            print(var)
            file_location_temp = load_projects()

            if file_location_temp == 0:
                pass
            else:
                loaded_file = file_location_temp
                temp_file = loaded_file
                temp_file = temp_file.replace(".scad",".tmp")
                print("File ", loaded_file, " loaded")

        elif var == "help":
            print(var)
            display_help()
        elif var == "print":
            print(var)
            print_file(loaded_file)
        elif var == "render":
            print(var)
            render(openscad_path, loaded_file)


            

        elif var == "exit":
                        print(var)
                        quit()

#This ensures the code is not run if it is imported
if __name__ == "__main__":

    #Temporary hardocded path
    #Will be able to load from configuration later
    p = '"C:\Program Files\OpenSCAD\openscad.com"'

    #Start execution of the main program
    start_vcos(version, p)
