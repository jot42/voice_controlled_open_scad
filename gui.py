# -*- coding: utf-8 -*-
import argparse
import os
import platform
import subprocess
# Form implementation generated from reading ui file 'X:\Desktop\ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
from re import search
from threading import Thread
from time import sleep

import keyboard
import speech_recognition as sr
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

run_main_loop = False

# -----Argument Parsing----- #
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-debug', action='store_true')
args = arg_parser.parse_args()

# Audio Requirements
rec = sr.Recognizer()


# System Memory Values
class UserInputThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.value = None

    def run(self):
        with sr.Microphone() as audio_in:
            ui.parse_log_item("Calibrating microphone, please wait", 0)
            rec.adjust_for_ambient_noise(audio_in, duration=5)

        ui.parse_log_item('', 2)
        self.value = keyboard.read_key()


"""class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    key = ""

    def run(self):
        self.key = keyboard.read_key()"""


class UiMainWindow(object):
    total_commands_run = 0

    # -----UI Initialisation----- #

    def __init__(self, main_window):

        # -----System Version Information----- #
        self.version_number = "0.0.1"

        if platform.system() == 'Linux':
            self.os_id = "L"
        elif platform.system() == 'Darwin':
            self.os_id = "M"
        elif platform.system() == "Windows":
            self.os_id = "W"

        # -----Main Window----- #
        main_window.setObjectName("main_window")
        main_window.setWindowModality(QtCore.Qt.WindowModal)
        main_window.setEnabled(True)
        main_window.resize(1366, 768)
        main_window.setMinimumSize(QtCore.QSize(1366, 768))
        main_window.setMaximumSize(QtCore.QSize(1366, 768))
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        main_window.setCentralWidget(self.centralwidget)
        main_window.setWindowTitle("VCOS - Voice Controlled OpenSCAD")

        # -----System Memory----- #
        self.loaded_file = None
        self.temp_file = None
        self.file_path = ""
        self.command_history = []  # Stores a list of function references to be able to undo commands
        self.redo_buffer = []  # Stores functions on an undo, and will be restored if redo is run
        self.is_calibrated = False  # The status of the calibration of the default microphone

        # -----UI Elements----- #

        # -----Fonts----- #
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        font.setKerning(True)

        # -----Labels----- #
        self.label_version = QtWidgets.QLabel(self.centralwidget)
        self.label_version.setGeometry(QtCore.QRect(10, 10, 150, 80))
        self.label_version.setFont(font)
        self.label_version.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_version.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_version.setAlignment(QtCore.Qt.AlignCenter)
        self.label_version.setObjectName("label_version")
        self.label_version.setText("VCOS-" + self.os_id + " " + self.version_number)

        self.label_state_header = QtWidgets.QLabel(self.centralwidget)
        self.label_state_header.setGeometry(QtCore.QRect(160, 10, 150, 40))
        self.label_state_header.setFont(font)
        self.label_state_header.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_state_header.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_state_header.setAlignment(QtCore.Qt.AlignCenter)
        self.label_state_header.setObjectName("label_state_header")
        self.label_state_header.setText("Current State:")

        self.label_state = QtWidgets.QLabel(self.centralwidget)
        self.label_state.setGeometry(QtCore.QRect(160, 50, 150, 40))
        self.label_state.setFont(font)
        self.label_state.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_state.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_state.setAlignment(QtCore.Qt.AlignCenter)
        self.label_state.setObjectName("label_state")
        self.label_state.setText("Stopped")

        # -----Group Boxes----- #
        self.groupbox_text = QtWidgets.QGroupBox(self.centralwidget)
        self.groupbox_text.setGeometry(QtCore.QRect(10, 99, 820, 661))
        self.groupbox_text.setObjectName("groupbox_text")
        self.groupbox_text.setTitle("Text View")

        self.groupbox_render = QtWidgets.QGroupBox(self.centralwidget)
        self.groupbox_render.setGeometry(QtCore.QRect(840, 0, 522, 535))
        self.groupbox_render.setObjectName("groupbox_render")
        self.groupbox_render.setTitle("Render View")

        self.groupbox_commands = QtWidgets.QGroupBox(self.centralwidget)
        self.groupbox_commands.setGeometry(QtCore.QRect(840, 535, 521, 225))
        self.groupbox_commands.setObjectName("groupbox_commands")
        self.groupbox_commands.setTitle("Commands")

        # -----Buttons----- #
        self.button_start_voice = QtWidgets.QCommandLinkButton(self.centralwidget)
        self.button_start_voice.clicked.connect(lambda: self.start_voice_control())
        self.button_start_voice.setGeometry(QtCore.QRect(310, 10, 185, 41))
        self.button_start_voice.setObjectName("btn_start-vc")
        self.button_start_voice.setText("Start")
        self.button_start_voice.setEnabled(True)

        if args.debug:
            self.button_debug = QtWidgets.QCommandLinkButton(self.centralwidget)
            self.button_debug.clicked.connect(lambda: self.open_newWindow())
            self.button_debug.setGeometry(QtCore.QRect(500, 10, 185, 41))
            self.button_debug.setObjectName("btn_debug")
            self.button_debug.setText("Debug")
            self.button_debug.setEnabled(True)

        self.button_stop_voice = QtWidgets.QCommandLinkButton(self.centralwidget)
        self.button_stop_voice.clicked.connect(lambda: self.stop_voice_control())
        self.button_stop_voice.setGeometry(QtCore.QRect(310, 50, 185, 41))
        self.button_stop_voice.setObjectName("btn_stop-vc")
        self.button_stop_voice.setText("Stop")
        self.button_stop_voice.setEnabled(False)

        # -----Text Boxes----- #
        self.textbox_editor = QtWidgets.QTextEdit(self.groupbox_text)
        self.textbox_editor.setGeometry(QtCore.QRect(5, 15, 810, 640))
        self.textbox_editor.setObjectName("textEdit")
        self.textbox_editor.setReadOnly(True)
        self.textbox_editor_clear_signal = pyqtSignal(int, name="clear")
        self.textbox_open_document = self.textbox_editor.document()
        self.textbox_cursor = QTextCursor(self.textbox_open_document)

        # -----List Boxes----- #
        self.listbox_commands = QtWidgets.QListWidget(self.groupbox_commands)
        self.listbox_commands.setGeometry(QtCore.QRect(5, 15, 511, 205))
        self.listbox_commands.setObjectName("listCommand")
        self.listbox_commands.setAutoScroll(True)

        # -----Image Boxes----- #
        self.label = QtWidgets.QLabel(self.groupbox_render)
        self.label.setGeometry(QtCore.QRect(5, 15, 512, 512))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("res/default.png"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.windows = []

    def debug_print_last_internal_command(self):
        debug_info = []

        if len(self.command_history) == 0:
            debug_info.append("NO_COMMANDS_ISSUED")
        else:
            debug_info.append(str(self.command_history[len(self.command_history) - 1]))

        if len(self.redo_buffer) == 0:
            debug_info.append("NO REDO COMMANDS")
        else:
            debug_info.append(str(self.redo_buffer[len(self.redo_buffer) - 1]))

        return debug_info

    def open_newWindow(self):

        temp_array = [self.version_number, self.os_id, self.label_state.text(), self.file_path,
                      str(self.debug_print_last_internal_command()[0]),
                      str(self.debug_print_last_internal_command()[1])]

        window = DebugWindow(temp_array)
        self.windows.append(window)
        window.show()

    # -----UI Manipulation----- #
    def update_vc_state_label(self, state_id):
        """
        Updates the ui label for the state of the VC engine

        Parameters:
            state_id - The id (as an int) of the corresponding message
                        0 - Offline
                        1 - Initialising
                        2 - Listening
                        3 - Processing

        """

        if state_id == 0:
            self.label_state.setText("Offline")
        elif state_id == 1:
            self.label_state.setText("Initialising")
        elif state_id == 2:
            self.label_state.setText("Listening")
        elif state_id == 3:
            self.label_state.setText("Processing")

    # -----Voice Control Functions----- #

    def start_voice_control(self):
        global run_main_loop

        run_main_loop = True

        self.button_start_voice.setEnabled(False)
        self.button_stop_voice.setEnabled(True)

        """self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.
        self.thread.start()"""
        self.thread = UserInputThread()
        self.thread.start()
        self.thread.join()
        self.data = self.thread.value
        print(self.data)

        doc = self.textbox_editor.document()
        cursor = QTextCursor(doc)  # self.textEdit.cursor()

        self.textbox_editor.setTextCursor(cursor)
        # cursor.movePosition(cursor.left, cursor.KeepAnchor, 3)

    def stop_voice_control(self):
        # -----Load Global Variables----- #
        global run_main_loop

        # -----Disable loop running and change ui button state----- #
        run_main_loop = False
        self.button_stop_voice.setEnabled(False)
        self.button_start_voice.setEnabled(True)

    def verify_loop_run_state(self, function, parameters):
        """
        Verifies if the runloop variable is true, and denies the function call if not. This is to enable a responsive
        start/stop button that terminates the loop flow when the user presses the stop button.

        Parameters:
            function - a reference to the desired function
            parameters - the desired parameters of the aforementioned function
        """
        # -----Load Global Variables----- #
        global run_main_loop

        if run_main_loop and function == self.undo_command:
            self.undo_command()
        elif run_main_loop and function == self.redo_command:
            self.redo_command()

        elif run_main_loop and parameters is not None:
            function(parameters)
            self.command_history.append([function, parameters])
            self.redo_buffer.clear()

        elif run_main_loop:
            function()
            self.command_history.append([function])
            self.redo_buffer.clear()

    # -----VCOS Functions----- #

    def print_help(self):
        """ Prints the help dialogs to the command area"""
        helptext_file = open("res/HELP.vcosdata", 'r')

        self.parse_log_item("Help", 1)

        for line in helptext_file:
            self.parse_log_item(line.rstrip(), 0)

        helptext_file.close()

    def load_project(self):
        # -----Vars----- #
        total_projects = 0
        project_list = []
        # -----Print All Projects----- #
        self.parse_log_item("Load", 1)
        self.parse_log_item("Here are your available projects:", 0)
        for project in os.listdir('projects'):
            if os.path.isdir("projects/" + project):
                project_list.append(project)
                total_projects += 1
                self.parse_log_item(str(total_projects) + ": " + project, False)

        while True:
            # -----Prompt User Input----- #
            self.parse_log_item("Which file would you like to load?", 0)
            self.parse_log_item("Please say a number or 'cancel'", 0)
            self.parse_log_item('', 2)
            response = input()
            self.parse_log_item(response, 1)

            # -----Process user input----- #
            if search("cancel", response):
                self.parse_log_item("Loading cancelled.", 0)
                return
            else:
                selected_project_array_index = int(response) - 1
                selected_project_name = project_list[selected_project_array_index]

                if selected_project_array_index < len(project_list):
                    filepath = os.getcwd() + "\\projects\\" + selected_project_name
                    self.file_path = filepath + "\\" + selected_project_name + ".scad"
                    self.loaded_file = open(filepath + "\\" + selected_project_name + ".scad")

                    # -----Load temp file with current file contents----- #
                    self.temp_file = open(filepath + "\\" + selected_project_name + ".tmp", "w")

                    for line in self.loaded_file:
                        self.temp_file.write(line)

                    self.temp_file.close()

                    # -----Erase current contents from text window----- #
                    while self.textbox_cursor.columnNumber() != 0 and self.textbox_cursor.blockNumber() != 0:
                        self.textbox_cursor.deleteChar()
                        self.textbox_cursor.blockNumber()
                        self.textbox_cursor.columnNumber()

                        sleep(0.01)
                    # -----Reset file seeking and load contents into textbox----- #
                    self.loaded_file.seek(0)

                    for line in self.loaded_file:
                        self.textbox_cursor.insertText(line)

                    return

    def create_new_project(self):

        # -----Ask user what the name should be----- #
        while True:

            self.parse_log_item("Please say the name of the project", 0)

            project_title = input()

            if project_title == "":
                pass
            else:
                # -----Proceed if project doesnt already exist----- #
                if not os.path.isdir("projects/" + project_title):

                    # -----Confirmation Prompt----- #
                    self.parse_log_item("Create project with the name: '" + project_title + "'?", 0)
                    self.parse_log_item("This will overwrite any unsaved changes", 0)
                    self.parse_log_item("", 0)
                    self.parse_log_item("'Yes' to confirm, 'No' to cancel, 'Retry' to rename", 0)

                    # -----Collect user response and process----- #
                    response = input()

                    if response == "yes":
                        os.mkdir("projects/" + project_title)
                        loaded_file = open("projects/" + project_title + "/" + project_title + ".scad", 'w')
                        temp_file = open("projects/" + project_title + "/" + project_title + ".scad.tmp", 'w')
                        self.parse_log_item("Project successfully created.", 0)
                        break
                    elif response == "no":
                        break
                    elif response == "retry":
                        pass

                else:
                    self.parse_log_item("A project with this name already exists, please choose another name", 0)

    def render_image(self):

        # Blocks the renderer if no file is open
        if self.file_path == "":
            self.parse_log_item("File not loaded", 0)
        else:

            # -----Save the textbox to a tmp file----- #
            self.temp_file = open(self.file_path.replace(".scad", ".tmp"), "w+")

            for line in self.textbox_editor.toPlainText():
                self.temp_file.write(line)

            # Assemble the command to run the renderer
            out_file = self.file_path.replace(".scad", ".png")
            full_command = "res/openscad/openscad.com -o " + out_file + " " + self.file_path
            print(full_command)

            # Run the renderer on the current file and update the command window once complete
            subprocess.run(full_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            self.parse_log_item("Render complete", 0)
            self.label.setPixmap(QtGui.QPixmap(out_file))

    def parse_log_item(self, text, is_command):
        """ Adds a new entry to the ui command log

        Parameters:
            text - The text to be added to the text box
            is_command - Will only display the '>' ready prompt

        """

        # -----New item isn't a user command----- #
        if is_command == 0:
            self.listbox_commands.insertItem(self.total_commands_run, text)
            self.total_commands_run += 1

        # -----New item is a command----- #
        elif is_command == 1:
            self.listbox_commands.insertItem(self.total_commands_run, '>' + text)
            self.total_commands_run += 1

        # -----Display the 'ready' prompt----- #
        elif is_command == 2:
            self.listbox_commands.insertItem(self.total_commands_run, '>')

    # -----Text Controls----- #

    def insert_new_text(self, text):
        """
        Inserts text into the text area

        Parameters:
            text - The text to add to the text area
        """

        self.parse_log_item("Insert text: " + text, 1)

        self.textbox_cursor.insertText(text)

    def remove_text(self, amount):
        """
        Deletes characters from the text box

        Parameters:
            amount - The amount of characters to remove
        """

        self.parse_log_item("Remove text: " + str(amount), True)

        for a in range(amount):
            self.textbox_cursor.deletePreviousChar()

    def undo_command(self):

        if len(self.command_history) == 0:
            self.parse_log_item("No Commands To Undo.", False)
        else:
            # -----Temp Variables----- #
            command_array_index = self.command_history[len(self.command_history) - 1]

            # ----- Undo Add Text----- #
            if command_array_index[0] == self.insert_new_text:
                self.redo_buffer.append(command_array_index)
                self.remove_text(len(command_array_index[1]))
                self.command_history.remove(command_array_index)

    def redo_command(self):
        if len(self.redo_buffer) == 0:
            self.parse_log_item("No Commands To Redo.", 0)
        else:
            # -----Temp Variables----- #
            redo_array_index = self.redo_buffer[len(self.redo_buffer) - 1]

            if len(redo_array_index) == 1:
                redo_array_index[0]()
            else:
                redo_array_index[0](redo_array_index[1])
            self.command_history.append(redo_array_index)
            self.redo_buffer.remove(redo_array_index)

    # -----User Input----- #

    def parse_user_input(self):
        self.update_vc_state_label(2)
        self.parse_log_item('', 2)

        debug_option = keyboard.read_key()
        self.update_vc_state_label(3)

        # -----Create New Project----- #
        if debug_option == "c":
            self.verify_loop_run_state(self.create_new_project, None)

        # -----Print Help Dialog----- #
        elif debug_option == "h":
            self.verify_loop_run_state(self.print_help, None)

        # -----Load Project----- #
        elif debug_option == "l":
            self.verify_loop_run_state(self.load_project, None)

        # -----Insert Text----- #
        elif debug_option == "i":
            self.verify_loop_run_state(self.insert_new_text, "farts" + str(ui.total_commands_run))

        # -----Remove Text----- #
        elif debug_option == "b":
            self.verify_loop_run_state(self.remove_text, 1)

        # -----Undo Last Command----- #
        elif debug_option == "u":
            self.verify_loop_run_state(self.undo_command, None)

        # -----Undo Last Command----- #
        elif debug_option == "r":
            self.verify_loop_run_state(self.redo_command, None)

        # -----Render Model----- #
        elif debug_option == "q":
            self.verify_loop_run_state(self.render_image, None)


class DebugWindow(QWidget):
    def __init__(self, table_values):
        super().__init__()
        self.title = 'PyQt5 table - pythonspot.com'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.initUI(table_values)

    def initUI(self, table_values):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(300, 200)
        self.createTable(table_values)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # Show widget
        self.show()

    def createTable(self, values):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(6)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Software Version"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem(values[0]))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("Host Operating System"))
        self.tableWidget.setItem(1, 1, QTableWidgetItem(values[1]))
        self.tableWidget.setItem(2, 0, QTableWidgetItem("Engine State"))
        self.tableWidget.setItem(2, 1, QTableWidgetItem(values[2]))
        self.tableWidget.setItem(3, 0, QTableWidgetItem("Loaded File"))
        self.tableWidget.setItem(3, 1, QTableWidgetItem(values[3]))
        self.tableWidget.setItem(4, 0, QTableWidgetItem("Latest Command"))
        self.tableWidget.setItem(4, 1, QTableWidgetItem(values[4]))
        self.tableWidget.setItem(5, 0, QTableWidgetItem("Latest Redo Command"))
        self.tableWidget.setItem(5, 1, QTableWidgetItem(values[5]))
        self.tableWidget.move(0, 0)

        # table selection change
        # self.tableWidget.doubleClicked.connect(self.on_click)


if __name__ == "__main__":
    import sys

    # Initialise and calibrate audio system

    app = QtWidgets.QApplication(sys.argv)
    main_screen = QtWidgets.QMainWindow()

    ui = UiMainWindow(main_screen)

    main_screen.show()
    sys.exit(app.exec_())
