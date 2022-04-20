import curses
import os
import platform
import traceback
import speech_recognition as sr
from re import search

"""
NOTE: make scrolling on textbox limited to line/column count or screen height/width (whichever is lower)
      make scrolling the screen separate from scrolling the cursor
      ensure any screen scrolling stops at the last column/line if it were to overflow the size of the text box
      
      when adding lines to the array, ensure that the last character is a space, if it isn't already
      
      IDEA 2:
      create loop with a range() of the line/array length
      
      print (with scroll offset) to end of screen (with an 'if' check)
      
      if check will ensure that 
      
      when printing text, check if the string could fit into the buffer.
      if it can, then there is no more need to edit, so limit the cursor to text length
      
      if it is too big, offset the text addition by the scrolling value, 
      
      when printing text, have a loop that counts to the column size, 
      
      IDEA 3:
      tie screen scrolling values to the length of the strings.
      
      This means that if there is no more text in the line to scroll to, prevent
      the scrolling from taking place.
      
      This could be done with a len() check or to return when an exception
      is triggered. 

      create function to check if the screen can be scrolled, return false
      if exception is thrown, and return true if not.
"""

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
        return word


# System variables
VERSION = '0.0.1'  # Version number, as a constant

command_log = []
text_box = []

# The preset limit for file sizes
file_column_limit = 1000
file_line_limit = 1000

cursor_scroll_h = 0
cursor_scroll_v = 0

screen_scroll_h = 0
screen_scroll_v = 0

# Determine user operating system
if platform.system() == 'Linux':
    OS_IDENTIFIER = "L"
elif platform.system() == 'Darwin':
    OS_IDENTIFIER = "M"
elif platform.system() == "Windows":
    OS_IDENTIFIER = "W"

# Setup curses runtime
screen_main = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
screen_main.keypad(True)
normalText = curses.A_NORMAL
curses.curs_set(0)
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)

# Initialise curses screens

# Get sub window size
r, c = screen_main.getmaxyx()
border_rows = int(r - 4)
border_cols = int(c - 37)

editor_rows = border_rows - 2
editor_cols = border_cols - 2


def update_header_box(state):
    """
    Updates the header to show current speech recognition engine state

    Parameters:
        state - The current state of the sr engine

    Returns:
        Nothing
    """

    states = ["Starting  ",
              "Listening ",
              "Processing"]

    screen_main.addstr(0, 0, "┌──────────────────────────────────┐")
    screen_main.addstr(1, 0, "│ VCOS-" + OS_IDENTIFIER + ' ' + VERSION + " │ " + "State: " + states[state] + " │")
    screen_main.addstr(2, 0, "└──────────────────────────────────┘")

    screen_main.addstr(3, 0, "Commands:")
    screen_main.addstr(3, 37, "Text:")

    screen_main.refresh()


# Main Screen
update_header_box(0)

# Command Interpreter
screen_border_commands = curses.newwin(border_rows, 37, 4, 0)
screen_container_commands = screen_main.subwin(editor_rows, 35, 5, 1)

screen_border_commands.box()

# Textbox
screen_border_editor = screen_main.subwin(border_rows, border_cols, 4, 37)
screen_container_editor = screen_main.subwin(editor_rows, editor_cols, 5, 38)

screen_border_editor.box()

screen_main.refresh()
screen_border_commands.refresh()
screen_border_editor.refresh()


def record_audio():
    """
    Records user input and returns it to calling function.
    """

    rec = sr.Recognizer()

    with sr.Microphone() as source:
        update_header_box(1)
        audio = rec.listen(source)

        try:
            # Return the detected speech as a string.
            update_header_box(2)
            return rec.recognize_google(audio).lower()

        # Avoids the program crashing if the recognition failed
        except sr.UnknownValueError as e:
            return ""


def update_command_window(sh, nc):
    # Manages text to the command screen

    # Parameters
    # sh = screen height as int
    # nc = new command to be added
    # ch = current command history

    # Return
    # None

    # Add the new command to the list
    command_log.append(nc)

    loop = 0

    if sh > len(command_log):
        for item in command_log:
            screen_container_commands.addstr(loop, 0, item)
            loop = loop + 1
    else:
        dif = len(command_log) - sh
        loop_2 = 0

        for item in command_log:
            if loop_2 < dif:
                loop_2 = loop_2 + 1
                pass
            else:
                screen_container_commands.addstr(loop, 0, item)
                loop = loop + 1
                loop_2 = loop_2 + 1

    screen_container_commands.refresh()


def update_text_window():
    """
    Updates and fits the content to the screen
    """

    # Required global variables
    global screen_scroll_h
    global screen_scroll_v
    global cursor_scroll_h
    global cursor_scroll_v

    # Print text box information to screen
    try:

        # update_text_window(window_rows,window_cols - 2, text_box)
        print("Max Line Length: ", str(editor_cols), "Total Lines: ", str(editor_rows))

        # If the editor window is taller than the textbox
        if editor_rows - 1 > len(text_box):

            # Draw the rows
            for rows in range(len(text_box)):
                temp_string = text_box[screen_scroll_v + rows][screen_scroll_h:len(text_box[screen_scroll_v + rows])]
                for char in range(len(text_box[rows])):
                    if char == editor_cols:
                        break
                    else:
                        temp_string = text_box[screen_scroll_v + rows][char]
                        screen_container_editor.addstr(rows, char, temp_string, curses.color_pair(1))

        # Of the editor window size is smaller than the textbox
        else:
            for rows in range(editor_rows - 1):

                # print("Print Progress: Line ", lp, ", Column Length: ", cl)
                temp_string = text_box[screen_scroll_v + rows][screen_scroll_h:editor_cols + screen_scroll_h]
                screen_container_editor.addstr(rows, 0, temp_string, curses.color_pair(1))
                screen_container_editor.refresh()

        # screen_container_editor.addstr(cursor_scroll_v , cursor_scroll_h," ", curses.A_BLINK)

        screen_border_editor.box()
        screen_border_editor.addstr(border_rows - 1, 1, str(cursor_scroll_v + screen_scroll_v) + '/' + str(
            cursor_scroll_h + screen_scroll_h))

        if cursor_scroll_v > len(text_box):
            cursor_scroll_v += -1

        elif cursor_scroll_h == len(text_box[cursor_scroll_v]):
            cursor_scroll_h += -1

        screen_container_editor.addstr(cursor_scroll_v, cursor_scroll_h,
                                       text_box[cursor_scroll_v + screen_scroll_v][cursor_scroll_h + screen_scroll_h],
                                       curses.A_BLINK)

        screen_border_editor.refresh()
        return True

    except curses.error as e:
        update_command_window(editor_rows, "Textbox Error")
        print(e)

    except IndexError as e:
        traceback.print_exc()
        quit()
        # text_box[screen_scroll_v + cursor_scroll_v] += " "
        # update_text_window()


def add_text(t):
    # Adds text to the text_box array

    # Parameters
    # t - text to add to the array

    global cursor_scroll_h
    global cursor_scroll_v

    global screen_scroll_h
    global screen_scroll_v

    try:
        current_char = ''
        new_string = ""
        loop = 0 + screen_scroll_h

        # Loop through string to inject the new text
        for i in range(len(t) + (len(text_box[cursor_scroll_v + screen_scroll_v]) - 1)):

            if i < len(t):
                text_box[cursor_scroll_v + screen_scroll_v] = text_box[cursor_scroll_v + screen_scroll_v] + " "

            if i == cursor_scroll_h + screen_scroll_h:
                for item in t:
                    new_string = new_string + item

            current_char = text_box[cursor_scroll_v + screen_scroll_v][i]
            new_string = new_string + current_char

        text_box[cursor_scroll_v + screen_scroll_v] = new_string

        for i in range(len(t)):
            cursor_scroll_h += 1
            update_text_window()

    except Exception as e:
        update_command_window(editor_rows, "No file loaded, or internal buffer problem")
        traceback.print_exc()


def move_cursor(d, v):
    """
    Moves the cursor in the selected direction by the provided number of characters

    Parameters:
        d - selected direction
        v - amount to move the cursor
    """



    global cursor_scroll_h
    global cursor_scroll_v

    global screen_scroll_h
    global screen_scroll_v

    for i in range(v):



        if d == "U":
            if i == 1:
                update_command_window(editor_rows, "Scroll Up " + str(v))

            if cursor_scroll_v != 0:
                cursor_scroll_v += -1

        elif d == "D":
            if i == 1:
                update_command_window(editor_rows, "Scroll Down " + str(v))

            if cursor_scroll_v < editor_rows - 1 or (cursor_scroll_v + screen_scroll_v) < len(text_box):
                cursor_scroll_v += 1

        elif d == "L":
            if i == 1:
                update_command_window(editor_rows, "Scroll Left " + str(v))

            if cursor_scroll_h != 0:
                cursor_scroll_h += -1

        elif d == "R":
            if i == 1:
                update_command_window(editor_rows, "Scroll Right " + str(v))

            if cursor_scroll_h < editor_cols:
                cursor_scroll_h += 1

        elif d == "SU":
            print("su trigger")
            if screen_scroll_v > 0:
                screen_scroll_v += -1

        elif d == "SD":
            print("sd trigger")
            if screen_scroll_v < file_line_limit - editor_rows:
                screen_scroll_v += 1

        elif d == "SL":
            print("sl trigger")
            if screen_scroll_h > 0:
                screen_scroll_h += -1

        elif d == "SR":
            print("sr trigger")
            if screen_scroll_h < file_column_limit - editor_cols:
                screen_scroll_h += 1
            else:
                update_command_window(editor_rows, "Scroll Right Failed")

        update_text_window()


def load_file(file):
    """
    Loads the contents of the named file into memory

    Parameters:
        file - The file to be loaded
    """
    f = open(os.getcwd() + file, "r")

    text_box.clear()

    # Add contents of file to the textbox buffer
    for line in f:
        text_box.append(line)

    while len(text_box) < file_line_limit:
        text_box.append(" ")

    # Replace all instances of new lines and tabs with spaces
    for row in range(file_line_limit):

        text_box[row] = text_box[row].replace('\t', ' ')
        text_box[row] = text_box[row].replace('\n', ' ')

        while len(text_box[row]) < file_column_limit:
            text_box[row] += " "

    # Add trailing spaces to enable effective scrolling
    current_longest_index = 0
    current_longest_length = 0

    for i in range(len(text_box)):
        if len(text_box[i]) > current_longest_length:
            current_longest_index = i
            current_longest_length = len(text_box[i])

    # Ensure all other lines match the length by adding
    for i in range(len(text_box)):
        if i != current_longest_index:
            while len(text_box[i]) < current_longest_length:
                text_box[i] = text_box[i] + " "

    update_text_window()


def show_projects():
    """
    Display all projects in the /projects folder and allow user to select one.
    """

    file_amount = 0
    file_path = "projects"
    files = []

    # Print project list
    update_command_window(editor_rows, "Load")
    update_command_window(editor_rows, " ")
    update_command_window(editor_rows, "Here are your available projects:")
    for file in os.listdir(file_path):
        if file.endswith(".scad"):
            update_command_window(editor_rows, (str(file_amount) + " " + file))
            file_amount += 1
            files.append('\\' + file_path + '\\' + file)

    # Prompt user for file selection
    update_command_window(editor_rows, " ")
    update_command_window(editor_rows, "Which file would you like to load?")
    update_command_window(editor_rows, "Please say a number or 'cancel'")

    run_loop = True

    while run_loop:
        try:
            # Get user input
            update_header_box(1)
            user_input = record_audio()

            # Commands tree
            if search("cancel", user_input):
                return 0
            else:
                # Check if the selected number is in range of the file array
                selected_file = int(user_input)

                # If the number exists in the file array
                if selected_file < len(files):
                    update_command_window(editor_rows, "File " + files[selected_file])

                    load_file(files[selected_file])
                    run_loop = False
        except Exception:
            traceback.print_exc()
            quit()


def input_parser():
    """
    A recursive function for input detection
    """

    i = record_audio()
    print(i)
    update_header_box(2)

    global cursor_scroll_h
    global cursor_scroll_v

    global screen_scroll_h
    global screen_scroll_v

    global text_box

    if i is not None:

        # Auto Resize Key
        if i == curses.KEY_RESIZE:
            pass

        # Escape Key
        elif search("exit", i):
            curses.endwin()
            quit()

        # Space Key
        elif i == 32:
            add_text("@")
            update_text_window()

        # Left Arrow Key
        elif search("scroll left", i):
            try:
                move_cursor('L', int(text_to_int(i.split("left", 1)[1])))
            except IndexError:
                update_command_window(editor_rows, "Please specify how far to scroll")

        # Right Arrow Key
        elif search("scroll right", i):
            try:
                move_cursor('R', int(text_to_int(i.split("right", 1)[1])))
            except IndexError:
                update_command_window(editor_rows, "Please specify how far to scroll")

        elif search("scroll up", i):
            try:
                move_cursor('U', int(text_to_int(i.split("up", 1)[1])))
            except IndexError:
                update_command_window(editor_rows, "Please specify how far to scroll")

        elif search("scroll down", i):
            try:
                move_cursor('D', int(text_to_int(i.split("down", 1)[1])))
            except IndexError:
                update_command_window(editor_rows, "Please specify how far to scroll")

        elif i == 119:
            move_cursor('SU', 1)

        elif i == 115:
            move_cursor('SD', 1)

        elif i == 97:
            move_cursor('SL', 1)

        elif i == 100:
            move_cursor('SR', 1)

            # Enter Key - New Line
        elif i == 10:

            new_text_box = []

            for i in range(len(text_box)):
                new_text_box.append(text_box[i])

                if i == cursor_scroll_v:
                    new_text_box.append("")

            text_box = new_text_box

            update_text_window()

        # Load File
        elif search("load", i):
            show_projects()

        # R Key
        """
        elif i == 114:
    
            for char in "render":
                screen_items["command_entity"].do_command(char)
    
            #screen_items["command_entity"].do_command("\n")
            #screen_items["command_container"].refresh()
    
        # H Key
        elif i == 104:
            update_command_window(window_rows, "VCOS Help:")
            update_command_window(window_rows, "'load' or 'l' - Shows this help window")
            update_command_window(window_rows, "'scroll [direction] [amount]' - Scrolls the text view")
            update_command_window(window_rows, "'render' or 'r' - Renders the current loaded project in OpenSCAD")
        """
    input_parser()


update_command_window(editor_rows, "Command Interpreter Ready")
update_command_window(editor_rows, "Say 'help' for a list of commands")
input_parser()

quit()
