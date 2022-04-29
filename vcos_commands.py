import curses
import os
import traceback
from re import search

import speech_recognition as sr


def update_header_box(di, state):
    """
    Updates the header to show current speech recognition engine state

    Parameters:
        di - data class
        state - The current state of the sr engine
    """

    states = ["Listening ",
              "Processing"]

    di.screen_main.addstr(0, 0, "┌──────────────────────────────────┐")
    di.screen_main.addstr(1, 0,
                          "│ VCOS-" + di.os_id + ' ' + di.version + " │ " + "State: " +
                          states[state] + " │")
    di.screen_main.addstr(2, 0, "└──────────────────────────────────┘")

    di.refresh_screen(0)


def record_audio(di):
    """
    Records user input and returns it to the calling function.

    Parameters:
        di - The data class
    """

    rec = sr.Recognizer()

    with sr.Microphone() as source:
        update_header_box(di, 0)
        audio = rec.listen(source)

        try:
            # Return the detected speech as a string and update header state.
            update_header_box(di, 1)
            return rec.recognize_google(audio).lower()

        # Avoids the program crashing if the recognition failed or no speech
        # is detected
        except sr.UnknownValueError:
            return ""


def text_to_int(word):
    """
    Converts words that phonetically sound like numbers into those numbers
    e.g. 'won','one' = 1
         'two','to','too' = 2

    Parameters:
        word - The word to convert to int
    """
    if search("won", word) or search("one", word):
        return '1'
    elif search("two", word) or search("too", word) or search("to", word):
        return '2'
    elif search("three", word):
        return '3'
    elif search("four", word):
        return '4'
    elif search("five", word):
        return '5'
    elif search("six", word):
        return '6'
    elif search("seven", word):
        return '7'
    elif search("eight", word):
        return '8'
    elif search("nine", word):
        return '9'
    elif search("ten", word):
        return '10'
    else:
        return int("nan")


def update_command_window(di, nc):
    """
    Adds commands to the buffer and refreshes the screen

    Parameters:
        di - The data class
        nc - New command to be added to the buffer

    """

    # Add the new command to the list
    di.command_log.append(nc)

    if not di.command_log == 0:
        # Remove the oldest entry from the log
        while len(di.command_log) >= di.window_rows:
            di.command_log.pop(0)

        for loop in range(len(di.command_log)):
            while len(di.command_log[loop]) < 57:
                di.command_log[loop] = di.command_log[loop] + " "
            di.screen_container_commands.addstr(loop, 0, di.command_log[loop], curses.color_pair(2))

    di.refresh_screen(3)


def update_text_window(di):
    """
    Updates and fits the content to the screen
    """

    # Print text box information to screen
    try:
        # If the editor window is taller than the textbox
        if di.window_rows - 1 > len(di.text_box):

            # Draw the rows
            for rows in range(len(di.text_box)):
                for char in range(len(di.text_box[rows])):
                    if char == di.editor_cols:
                        break
                    else:
                        temp_string = di.text_box[di.screen_scroll_v + rows][char]
                        di.screen_container_editor.addstr(rows, char, temp_string, curses.color_pair(1))

        # Or if the editor window size is smaller than the textbox
        else:
            for rows in range(di.window_rows - 1):
                temp_string = di.text_box[di.screen_scroll_v + rows][
                              di.screen_scroll_h:di.editor_cols + di.screen_scroll_h]
                di.screen_container_editor.addstr(rows, 0, temp_string, curses.color_pair(1))
                di.screen_container_editor.refresh()

            # Display cursor information
            di.screen_border_editor.box()
            di.screen_border_editor.addstr(di.border_rows - 1, 1,
                                           str(di.cursor_scroll_v + di.screen_scroll_v) + '/' + str(
                                               di.cursor_scroll_h + di.screen_scroll_h))

        if di.cursor_scroll_v > len(di.text_box):
            di.cursor_scroll_v += -1

        elif di.cursor_scroll_h == len(di.text_box[di.cursor_scroll_v]):
            di.cursor_scroll_h += -1

        # Add a cursor to the screen
        di.screen_container_editor.addstr(di.cursor_scroll_v, di.cursor_scroll_h,
                                          di.text_box[di.cursor_scroll_v + di.screen_scroll_v][
                                              di.cursor_scroll_h + di.screen_scroll_h],
                                          curses.A_BLINK)

        # Refresh and signify successful completion
        di.refresh_screen(2)

        return True

    except curses.error as e:
        update_command_window(di.window_rows, "Textbox Error")
        print(e)

    except IndexError:
        traceback.print_exc()
        quit()


def add_text(di, t):
    """
    Handles adding text to the pre-existing buffer

    Parameters
        di - data class
        t - The text to add to the array
    """

    try:
        new_string = ""

        # Loop through string to inject the new text
        for i in range(len(t) + (len(di.text_box[di.cursor_scroll_v + di.screen_scroll_v]) - 1)):

            if i < len(t):
                di.text_box[di.cursor_scroll_v + di.screen_scroll_v] = di.text_box[
                                                                           di.cursor_scroll_v + di.screen_scroll_v] \
                                                                       + " "

            if i == di.data.cursor_scroll_h + di.data.screen_scroll_h:
                for item in t:
                    new_string = new_string + item

            current_char = di.text_box[di.cursor_scroll_v + di.screen_scroll_v][i]
            new_string = new_string + current_char

        di.text_box[di.cursor_scroll_v + di.screen_scroll_v] = new_string

        for i in range(len(t)):
            di.cursor_scroll_h += 1
            update_text_window(di)

    except IndexError:
        update_command_window(di, "No file loaded, or internal buffer problem")
        traceback.print_exc()


def load_file(di, file):
    """
    Loads the contents of the named file into memory

    Parameters:
        file - The file to be loaded
    """

    f = open(os.getcwd() + file, "r")

    di.text_box.clear()

    # Add contents of file to the textbox buffer
    for line in f:
        di.text_box.append(line)

    while len(di.text_box) < di.file_line_limit:
        di.text_box.append(" ")

    # Replace all instances of new lines and tabs with spaces
    for row in range(di.file_line_limit):

        di.text_box[row] = di.text_box[row].replace('\t', ' ')
        di.text_box[row] = di.text_box[row].replace('\n', ' ')

        while len(di.text_box[row]) < di.file_column_limit:
            di.text_box[row] += " "

    # Add trailing spaces to enable effective scrolling
    current_longest_index = 0
    current_longest_length = 0

    for i in range(len(di.text_box)):
        if len(di.text_box[i]) > current_longest_length:
            current_longest_index = i
            current_longest_length = len(di.text_box[i])

    # Ensure all other lines match the length by adding
    for i in range(len(di.text_box)):
        if i != current_longest_index:
            while len(di.text_box[i]) < current_longest_length:
                di.text_box[i] = di.text_box[i] + " "

    update_text_window(di)
    di.file_path = file

    print("t_content")
    for item in di.text_box:
        print(item)


def show_projects(di):
    """
    Display all projects in the /projects folder and allow user to select one.
    """

    file_amount = 0
    projects_path = "projects"
    files = []

    # Print project list

    update_command_window(di, "Here are your available projects:")
    for file in os.listdir(projects_path):
        if file.endswith(".scad"):
            update_command_window(di, (str(file_amount) + " " + file))
            file_amount += 1
            files.append('\\' + projects_path + '\\' + file)

    # Prompt user for file selection
    update_command_window(di, " ")
    update_command_window(di, "Which file would you like to load?")
    update_command_window(di, "Please say a number or 'cancel'")

    run_loop = True

    while run_loop:

        # Get user input
        update_header_box(di, 1)
        user_input = record_audio(di)

        # Commands tree
        if search("cancel", user_input):
            return 0
        else:
            # Check if the selected number is in range of the file array
            selected_file = int(user_input)

            # If the number exists in the file array
            if selected_file < len(files):
                update_command_window(di, "File " + files[selected_file])

                load_file(di, files[selected_file])
                run_loop = False
