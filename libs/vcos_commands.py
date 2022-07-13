import curses
import os
import subprocess
import traceback
from re import search

import speech_recognition as sr

from libs.vcos_data import VCOSData as Data

data = Data()


def update_header_box(state):
    """
    Updates the header to show current speech recognition engine state

    Parameters:
        data - data class
        state - The current state of the sr engine
    """

    states = ["Starting  ",
              "Listening ",
              "Processing"]

    data.screen_main.addstr(0, 0, "┌──────────────┐┌───────────────────┐")
    data.screen_main.addstr(1, 0,
                            "│ VCOS-" + data.os_id + ' ' + data.version + " │" + "│ State: " +
                            states[state] + " │")
    data.screen_main.addstr(2, 0, "└──────────────┘└───────────────────┘")

    data.screen_main.refresh()


def update_command_window(nc):
    """
    Adds commands to the buffer and refreshes the screen

    Parameters:
        data - The data class
        nc - New command to be added to the buffer

    """

    # Add the new command to the list
    data.command_log.append(nc)

    if not data.command_log == 0:
        # Remove the oldest entry from the log
        while len(data.command_log) >= data.window_rows:
            data.command_log.pop(0)

        for loop in range(len(data.command_log)):
            while len(data.command_log[loop]) < 57:
                data.command_log[loop] = data.command_log[loop] + " "
            data.screen_container_commands.addstr(loop, 0, data.command_log[loop], curses.color_pair(2))

    data.screen_container_commands.refresh()


def update_text_window():
    """
    Updates and fits the content to the screen
    """

    # Print text box information to screen
    try:
        # If the editor window is taller than the textbox
        if data.window_rows - 1 > len(data.text_box):

            # Draw the rows
            for rows in range(len(data.text_box)):
                for char in range(len(data.text_box[rows])):
                    if char == data.editor_cols:
                        break
                    else:
                        temp_string = data.text_box[data.screen_scroll_v + rows][char]
                        data.screen_container_editor.addstr(rows, char, temp_string, curses.color_pair(1))

        # Or if the editor window size is smaller than the textbox
        else:
            for rows in range(data.window_rows - 1):
                temp_string = data.text_box[data.screen_scroll_v + rows][
                              data.screen_scroll_h:data.editor_cols + data.screen_scroll_h]
                data.screen_container_editor.addstr(rows, 0, temp_string, curses.color_pair(1))
                data.screen_container_editor.refresh()

            # display cursor information
            data.screen_border_editor.box()
            data.screen_border_editor.addstr(data.border_rows - 1, 1,
                                             str(data.cursor_scroll_v + data.screen_scroll_v) + '/' + str(
                                                 data.cursor_scroll_h + data.screen_scroll_h))

        if data.cursor_scroll_v > len(data.text_box):
            data.cursor_scroll_v += -1

        elif data.cursor_scroll_h == len(data.text_box[data.cursor_scroll_v]):
            data.cursor_scroll_h += -1

        # Add a cursor to the screen
        data.screen_container_editor.addstr(data.cursor_scroll_v, data.cursor_scroll_h,
                                            data.text_box[data.cursor_scroll_v + data.screen_scroll_v][
                                                data.cursor_scroll_h + data.screen_scroll_h],
                                            curses.A_BLINK)

        # Refresh and signify successful completion
        data.screen_container_editor.refresh()

        return True

    except curses.error as e:
        update_command_window("Textbox Error")
        print(e)

    except IndexError:
        traceback.print_exc()
        quit()


def record_audio():
    """
    Records user input and returns it to the calling function.

    Parameters:
        data - The data class
    Returns:
        Speech data processed by Google, as a String
    """

    with sr.Microphone() as source:
        update_header_box(1)
        user_in = rec.listen(source)

        try:
            # Return the detected speech as a string and update header state.
            update_header_box(2)
            return rec.recognize_google(user_in).lower()

        # Avoids the program crashing if the recognition failed or no speech
        # is detected
        except sr.UnknownValueError:
            return ""


def calibrate_audio():
    with sr.Microphone() as source:
        rec.adjust_for_ambient_noise(source, duration=5)


def move_cursor(d, v, s):
    """
    Moves the cursor in the selected direction by the provided number of characters

    Parameters:
    d - selected direction
    v - amount to move the cursor
    s - silences command window updates
    """

    for i in range(v):

        if d == 'U':
            if i == 0 and s is True:
                update_command_window("Scroll Up " + str(v))
                update_command_window("")

            if data.cursor_scroll_v != 0:
                data.cursor_scroll_v += -1

        elif d == 'D':
            if i == 0 and s is True:
                update_command_window("Scroll Down " + str(v))
                update_command_window("")

            if data.cursor_scroll_v < data.window_rows - 1 or (data.cursor_scroll_v + data.screen_scroll_v) < len(
                    data.text_box):
                data.cursor_scroll_v += 1

        elif d == 'L':
            if i == 0 and s is True:
                update_command_window("Scroll Left " + str(v))
                update_command_window("")

            if data.cursor_scroll_h != 0:
                data.cursor_scroll_h += -1

        elif d == 'R':
            if i == 0 and s is True:
                update_command_window("Scroll Right " + str(v))
                update_command_window("")

            if data.cursor_scroll_h < data.editor_cols:
                data.cursor_scroll_h += 1

        elif d == 'SU':
            if i == 0 and s is True:
                update_command_window("Screen Up " + str(v))
                update_command_window("")
            if data.screen_scroll_v > 0:
                data.screen_scroll_v += -1

        elif d == 'SD':
            if i == 0 and s is True:
                update_command_window("Screen Down " + str(v))
                update_command_window("")
            if data.screen_scroll_v < data.file_line_limit - data.window_rows:
                data.screen_scroll_v += 1

        elif d == 'SL':
            if i == 0 and s is True:
                update_command_window("Screen Left " + str(v))
                update_command_window("")

            if data.screen_scroll_h > 0:
                data.screen_scroll_h += -1

        elif d == 'SR':
            if i == 0 and s is True:
                update_command_window("Screen Right " + str(v))
                update_command_window("")

            if data.screen_scroll_h < data.file_column_limit - data.editor_cols:
                data.screen_scroll_h += 1

    update_text_window()


def symbol_translate(text):
    """
    Converts text input into symbols and converts text into numbers

    Parameters:
        text - The users' text input
    """

    # Misinterpretation protection
    text = text.replace("write", "right")
    text = text.replace("lord", "load")
    text = text.replace("sex", "six")
    text = text.replace(' ad', 'add')

    # Alternate interpretations
    text = text.replace("won", "1")
    text = text.replace("two", "2")
    text = text.replace("too", "2")
    text = text.replace("to", "2")

    # Numbers
    text = text.replace("one", "1")
    text = text.replace("three", "3")
    text = text.replace("four", "4")
    text = text.replace("five", "5")
    text = text.replace("six", "6")
    text = text.replace("seven", "7")
    text = text.replace("eight", "8")
    text = text.replace("nine", "9")
    text = text.replace("ten", "10")

    # Symbols
    text = text.replace(' space', ' ')
    text = text.replace('grave', '`')
    text = text.replace('grave accent', '`')
    text = text.replace('backtick', '`')
    text = text.replace('back quote', '`')
    text = text.replace('tilde', '~')
    text = text.replace('exclamation mark', '!')
    text = text.replace('exclamation point', '!')
    text = text.replace('bang', '!')
    text = text.replace(' at', '@')
    text = text.replace('at sign', '@')
    text = text.replace('at symbol', '@')
    text = text.replace('pound', '#')
    text = text.replace('hash', '#')
    text = text.replace('number', '#')
    text = text.replace('dollar sign', '$')
    text = text.replace('dollar', '$')
    text = text.replace('percent', '%')
    text = text.replace('percent sign', '%')
    text = text.replace('open parenthesis', '(')
    text = text.replace('left parenthesis', '(')
    text = text.replace('close parenthesis', ')')
    text = text.replace('right parenthesis', ')')
    text = text.replace('hyphen', '-')
    text = text.replace('minus', '-')
    text = text.replace('minus sign', '-')
    text = text.replace('dash', '-')
    text = text.replace('underscore', '_')
    text = text.replace('equals', '=')
    text = text.replace('equals sign', '=')
    text = text.replace('add', '+')
    text = text.replace('plus', '+')
    text = text.replace('plus sign', '+')
    text = text.replace('left bracket', '[')
    text = text.replace('right bracket', ']')
    text = text.replace('left brace', '{')
    text = text.replace('right brace', '}')
    text = text.replace('backslash', '\\')
    text = text.replace('exclamation mark', '^')
    text = text.replace('ampersand', '&')
    text = text.replace('asterisk', '*')
    text = text.replace('pipe', '|')
    text = text.replace('semicolon', ';')
    text = text.replace('colon', ':')
    text = text.replace(' add', '+')
    text = text.replace(' add', '+')
    text = text.replace('forward slash', '/')
    text = text.replace('slash', '/')
    text = text.replace('quotation mark', '"')
    text = text.replace('apostrophe', '\'')
    text = text.replace('single quote', '\'')
    text = text.replace('comma', ',')
    text = text.replace('period', '.')
    text = text.replace('point', '.')
    text = text.replace('less than', '<')
    text = text.replace('greater than', '>')
    text = text.replace('question mark', '?')

    return text


def add_text(t):
    """
    Handles adding text to the pre-existing buffer

    Parameters
        data - data class
        t - The text to add to the array
    """

    try:
        new_string = ""

        # Loop through string to inject the new text
        for i in range(len(t) + (len(data.text_box[data.cursor_scroll_v + data.screen_scroll_v]) - 1)):

            if i < len(t):
                data.text_box[data.cursor_scroll_v + data.screen_scroll_v] = data.text_box[
                                                                                 data.cursor_scroll_v + data.screen_scroll_v] + " "

            if i == data.cursor_scroll_h + data.screen_scroll_h:
                for item in t:
                    new_string = new_string + item

            current_char = data.text_box[data.cursor_scroll_v + data.screen_scroll_v][i]
            new_string = new_string + current_char

        data.text_box[data.cursor_scroll_v + data.screen_scroll_v] = new_string

        for i in range(len(t)):
            move_cursor('R', 1, False)
            update_text_window()

    except IndexError:
        update_command_window("No file loaded, or internal buffer problem")
        traceback.print_exc()


def remove_text(v):
    """
    Handles removing text from the pre-existing buffer

    Parameters:
        v - amount to backspace
    """
    for q in range(v):
        if v == 0:
            update_command_window("Backspace " + str(v))

        try:
            new_string = ""

            for i in range(len(data.text_box[data.cursor_scroll_v + data.screen_scroll_v]) - 1):

                if i == data.cursor_scroll_h + data.screen_scroll_h - 1:
                    pass
                else:
                    current_char = data.text_box[data.cursor_scroll_v + data.screen_scroll_v][i]
                    new_string = new_string + current_char

            data.text_box[data.cursor_scroll_v + data.screen_scroll_v] = new_string

            move_cursor('L', 1, False)
            update_text_window()

        except IndexError:
            pass


def insert_new_line():
    update_command_window("New Line")
    update_command_window(" ")
    new_text_box = []

    for a in range(len(data.text_box)):

        if a == data.cursor_scroll_v + data.screen_scroll_v:
            new_text_box.append(data.text_box[a])

            # Generate new line fitting to the line length limit
            temp_string = " "

            while len(temp_string) < data.file_line_limit:
                temp_string = temp_string + " "

            new_text_box.append(temp_string)
            # new_text_box.append(data.text_box[a])
        else:
            new_text_box.append(data.text_box[a])

    data.text_box = new_text_box

    update_text_window()


def remove_line():
    new_textbox = []

    for i in range(len(data.text_box)):
        if i == data.cursor_scroll_v + data.screen_scroll_v:
            pass
        else:
            new_textbox.append(data.text_box[i])

    data.text_box = new_textbox
    update_text_window()

    while data.cursor_scroll_v > 0:
        move_cursor('L', 1, False)


def save_file():
    file = open(data.project_file_path, "w")

    for line in data.text_box:
        line = line.rstrip()
        file.write(line + '\n')


def load_file(file):
    """
    Loads the contents of the named file into memory

    Parameters:
        file - The file to be loaded
    """

    f = open(os.getcwd() + file, "r")

    data.text_box.clear()

    # Add contents of file to the textbox buffer
    for line in f:
        data.text_box.append(line)

    while len(data.text_box) < data.file_line_limit:
        data.text_box.append(" ")

    # Replace all instances of new lines and tabs with spaces
    for row in range(data.file_line_limit):

        data.text_box[row] = data.text_box[row].replace('\t', ' ')
        data.text_box[row] = data.text_box[row].replace('\n', ' ')

        while len(data.text_box[row]) < data.file_column_limit:
            data.text_box[row] += " "

    # Add trailing spaces to enable effective scrolling
    current_longest_index = 0
    current_longest_length = 0

    for i in range(len(data.text_box)):
        if len(data.text_box[i]) > current_longest_length:
            current_longest_index = i
            current_longest_length = len(data.text_box[i])

    # Ensure all other lines match the length by adding spaces
    for i in range(len(data.text_box)):
        if i != current_longest_index:
            while len(data.text_box[i]) < current_longest_length:
                data.text_box[i] = data.text_box[i] + " "

    update_text_window()
    data.scad_file_path = file
    data.project_file_path = os.getcwd() + file
    f.close()


def create_new_file_dialog():
    update_command_window("Please say the name of the new file")
    update_command_window("NOTE: You do not need to include the file type")

    while True:
        filename = record_audio()
        confirm = False

        if filename == "":
            pass
        else:
            update_command_window("")
            update_command_window("Are you sure you want to create " + filename + ".scad?")
            update_command_window("This will overwrite any unsaved changes")
            update_command_window("")
            update_command_window("'Yes' to confirm, 'No' to cancel, 'Retry to rename'")
            update_command_window("")

            while not confirm:
                response = record_audio()

                if search("yes", response):
                    file = open("projects/" + filename + ".scad", "w")
                    file.write("")
                    file.close()
                    load_file("/projects/" + filename + ".scad")
                    return
                elif search("no", response):
                    return
                elif search("retry", response):
                    create_new_file_dialog()
                    return


def load_file_dialog():
    """
    Display all projects in the /projects folder and allow user to select one.
    """

    file_amount = 0
    files = []

    # Print project list
    update_command_window("Here are your available projects:")
    for file in os.listdir('projects'):
        if file.endswith(".scad"):
            update_command_window((str(file_amount) + " " + file))
            file_amount += 1
            files.append('\\' + 'projects' + '\\' + file)

    # Prompt user for file selection
    update_command_window("")
    update_command_window("Which file would you like to load?")
    update_command_window("Please say a number or 'cancel'")

    while True:

        # Get user input
        user_input = record_audio()

        # Commands tree

        if search("cancel", user_input):
            update_command_window("cancelled")
            return
        else:
            # Check if the selected number is in range of the file array
            selected_file = int(symbol_translate(user_input))

            # If the number exists in the file array
            if selected_file < len(files):
                load_file(files[selected_file])
                update_command_window("File " + files[selected_file] + "loaded")
                return


def render_image(file_dir):
    file_dir = file_dir.replace('\\', '/')

    # Blocks the renderer if no file is open
    if file_dir == "":
        update_command_window("File not loaded")
    else:
        # Assemble the command to run the renderer
        out_file = '"' + file_dir.replace(".scad", ".png") + '"'
        full_command = ".\\openscad\\openscad.com -o " + "\"" + out_file[2:] + " " + '"' + file_dir[1:] + '"'

        # Run the renderer on the current file and update the command window once complete
        subprocess.run(full_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        update_command_window("Render complete")
