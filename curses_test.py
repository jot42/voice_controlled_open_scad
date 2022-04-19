import curses
import os
import platform
import traceback



def fit_to_screen():
    """
    Modifies text information to fit to the curses screen

    Parameters:
        None

    Returns:
        None
    """


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

# System variables
VERSION = '0.0.1'  # Version number, as a constant

command_log = []
text_box = []

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

container_rows = border_rows - 2
container_cols = border_cols - 2

# Main Screen
screen_main.addstr(0, 0, "#----------------------------------------------------------#")
screen_main.addstr(1, 0,
                   "| VCOS-" + OS_IDENTIFIER + ' ' + VERSION + " | " + " Press 'h' or say 'help' for command help |")
screen_main.addstr(2, 0, "#----------------------------------------------------------#")

screen_main.addstr(3, 0, "Commands:")

# Command Interpreter
screen_border_commands = curses.newwin(border_rows, 37, 4, 0)
screen_container_commands = screen_main.subwin(container_rows, 35, 5, 1)

screen_border_commands.box()

# Textbox
screen_border_editor = screen_main.subwin(border_rows, border_cols, 4, 37)
screen_container_editor = screen_main.subwin(container_rows, container_cols, 5, 38)

screen_border_editor.box()

screen_main.refresh()
screen_border_commands.refresh()
screen_border_editor.refresh()


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
    # Manages text on the text screen

    # Parameters
    # None

    # Return
    # None

    # Required global variables
    global screen_scroll_h
    global screen_scroll_v
    global cursor_scroll_h
    global cursor_scroll_v

    loop = 0
    loop_2 = 0

    temp_string = ""
    textbox_formatted = []

    # Add trailing spaces to enable effective scrolling
    current_longest_index = 0
    current_longest_length = 0

    for i in range(len(text_box)):
        if len(text_box[i]) > current_longest_length:
            current_longest_index = i
            current_longest_length = len(text_box[i])

    for i in range(len(text_box)):
        if i != current_longest_index:
            while len(text_box[i]) < current_longest_length:
                text_box[i] = text_box[i] + " "

    # Print text box information to screen
    try:

        # update_text_window(window_rows,window_cols - 2, text_box)
        print("Max Line Length: ", str(container_cols), "Total Lines: ", str(container_rows))
        for rows in range(container_rows - 1):
            lp = str(rows)
            cl = str(len(text_box[rows]))

            print("Print Progress: Line ", lp, ", Column Length: ", cl)
            temp_string = text_box[screen_scroll_v + rows][screen_scroll_h:container_cols + screen_scroll_h]
            screen_container_editor.addstr(rows, 0, temp_string[screen_scroll_h:container_cols], curses.color_pair(1))
            screen_container_editor.refresh()

        # screen_container_editor.addstr(cursor_scroll_v , cursor_scroll_h," ", curses.A_BLINK)

        screen_border_editor.box()
        screen_border_editor.addstr(border_rows - 1, 1, str(cursor_scroll_v) + '/' + str(cursor_scroll_h))

        if cursor_scroll_v > len(text_box):
            cursor_scroll_v += -1

        elif cursor_scroll_h == len(text_box[cursor_scroll_v]):
            cursor_scroll_h += -1

        screen_container_editor.addstr(cursor_scroll_v, cursor_scroll_h,
                                       text_box[cursor_scroll_v + screen_scroll_v][cursor_scroll_h + screen_scroll_h],
                                       curses.A_BLINK)

        screen_border_editor.refresh()
        return True

    except curses.error:
        update_command_window(container_rows, "FUCK FUCK")
        print("Fuck")

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

        for i in range(len(t) + (len(text_box[cursor_scroll_v]) - 1)):

            if i == cursor_scroll_h:
                for item in t:
                    new_string = new_string + item

            current_char = text_box[cursor_scroll_v + screen_scroll_v][i + screen_scroll_h]
            new_string = new_string + current_char

        text_box[cursor_scroll_v] = new_string

        for i in range(len(t)):
            cursor_scroll_h += 1
            update_text_window()

    except Exception as e:
        update_command_window(container_rows, "No file loaded, or internal buffer problem")
        traceback.print_exc()


def move_cursor(d, v):
    # Moves the cursor in the selected direction by the provided number of characters

    # Parameters:
    # d - selected direction
    # v - amount to move the cursor

    global cursor_scroll_h
    global cursor_scroll_v

    global screen_scroll_h
    global screen_scroll_v

    for i in range(v):

        if d == 'U':
            update_command_window(container_rows, "Scroll Up   ")

            if cursor_scroll_v != 0:
                cursor_scroll_v += -1

        elif d == 'D':
            update_command_window(container_rows, "Scroll Down")

            if cursor_scroll_v < container_rows - 1:
                cursor_scroll_v += 1

        elif d == 'L':
            update_command_window(container_rows, "Scroll Left")

            if cursor_scroll_h != 0:
                cursor_scroll_h += -1

        elif d == 'R':

            update_command_window(container_rows, "Scroll Right")

            if cursor_scroll_h < container_cols:
                cursor_scroll_h += 1

        elif d == 'SU':

            if screen_scroll_v > 0:
                screen_scroll_v += -1

        elif d == 'SD':

            if screen_scroll_v < border_rows - len(text_box):
                screen_scroll_v += 1

        elif d == 'SL':
            if screen_scroll_h > 0:
                screen_scroll_h += -1

        elif d == 'SR':
            if screen_scroll_h < border_cols - len(text_box[0]):
                screen_scroll_h += 1

        update_text_window()


def load_file():
    f = open(os.getcwd() + "\\projects\\example_3.scad", "r")

    text_box.clear()

    # Add contents of file to the textbox buffer

    for line in f:
        text_box.append(line)

    while len(text_box) <= container_rows:
        text_box.append(" ")

    for row in range(len(text_box) - 1):
        text_box[row].replace('\t', ' ')
        text_box[row].replace('\n', ' ')

        while len(text_box[row]) < container_cols:
            text_box[row] += " "

    if update_text_window():
        update_command_window(container_rows, "load")


def input_parser():
    # A recursive function for keypress detection

    # Parameters
    # None

    # Returns
    # None

    i = screen_main.getch()
    global cursor_scroll_h
    global cursor_scroll_v

    global screen_scroll_h
    global screen_scroll_v

    global text_box

    # Auto Resize Key
    if i == curses.KEY_RESIZE:
        pass

    # Escape Key
    elif i == 27:
        curses.endwin()
        quit()

    # Space Key
    elif i == 32:
        add_text("@")
        update_text_window()

    # Space Key
    elif i == 48:
        update_text_window()

    # 1 Key
    elif i == 49:
        None

    # Left Arrow Key
    elif i == curses.KEY_LEFT:
        move_cursor('L', 1)

    # Right Arrow Key
    elif i == curses.KEY_RIGHT:
        move_cursor('R', 1)

    elif i == curses.KEY_UP:
        move_cursor('U', 1)

    elif i == curses.KEY_DOWN:
        move_cursor('D', 1)

    elif i == 97:
        move_cursor('SU', 1)

    elif i == 98:
        move_cursor('SD', 1)

    elif i == 99:
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

    # DEBUG
    # L Key - Load File
    elif i == 108:
        load_file()

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


input_parser()

quit()
