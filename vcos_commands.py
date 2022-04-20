from cgi import test
import os
import pyaudio
import requests
import wave
import speech_recognition as sr
import subprocess

if __name__ == "__main__":
    pass


# Core System Commands
def calibrate_mic():
    print("Calibrating microphone.")
    r = sr.Recognizer()

    with sr.Microphone() as source:
        calibration = r.adjust_for_ambient_noise(source, duration=5)
        return calibration


# Records user audio and uses Google services for interpretation
def record_audio():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        audio = r.listen(source)

        try:
            # Return the detected speech as a string.
            return r.recognize_google(audio).lower()

        # Avoids the program crashing if the recognition failed
        except sr.UnknownValueError as e:
            pass


# Renders the loaded .scad file to a .png
def render(openscad_path, file_dir):
    # Blocks the renderer if no file is open
    if file_dir == "":
        print("File not loaded.")
        pass
    else:
        out_file = " -o " + '"' + file_dir.replace(".scad", ".png") + '"'
        full_command = openscad_path + out_file + " " + '"' + file_dir + '"'

        ds = subprocess.Popen(full_command, shell=True, stdin=None, stdout=open(os.devnull, "wb"), stderr=None)
        ds.wait()

        print("Render complete")


# Returns the named OpenSCAD file
def load_projects():
    """Display all projects in the /projects folder and allow user to select one."""

    file_amount = 0
    file_path = os.getcwd() + "\projects"
    files = []

    # Print project list
    print("Here are your available projects:")
    for file in os.listdir(file_path):
        if file.endswith(".scad"):
            print(file_amount, " ", file)
            file_amount += 1
            files.append(file_path + '\\' + file)

    # Prompt user for file selection
    print("Which file would you like to load? ")
    print("Please say a number or 'cancel' to go back")

    run_loop = True

    while run_loop:
        try:
            # Get user input
            user_input = record_audio()

            # Commands tree
            if user_input == "cancel":
                print(user_input)
                return (0)
            else:
                # Check if the selected number is in range of the file array
                selected_file = int(user_input)

                # If the number exists in the file array
                if selected_file < len(files):
                    print("File " + files[selected_file])
                    return files[selected_file]
        except:
            pass


# Prints the contents of the provided file
def print_file(file_dir):
    try:
        # Attempt to open and print contents
        file = open(file_dir, "r")
        for line in file:
            print(line)
    except Exception as e:
        print("File not loaded")


# Prints help information to the terminal
def display_help():
    print("Here are the commands available:")
    print("Load - Starts file opening dialogue")
    print("Exit - Exits this software")

    # Mathmatical Operations


def run_addition():
    print("ADDITION NOT IMPLETMENTED YET")


def run_subtraction():
    print("SUBTRACTION NOT IMPLEMENTED YET")


def run_multiplication():
    print("MULTIPLICATION NOT IMPLEMENTED YET")


def run_division():
    print("DIVISION NOT IMPLEMENTED YET")


def run_modulo():
    print("MODULO NOT IMPLEMENTED YET")


def run_exponentiation():
    print("EXPONENTIATION NOT IMPLEMENTED YET")
