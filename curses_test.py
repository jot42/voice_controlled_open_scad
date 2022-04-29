import curses
import subprocess
from re import search

import vcos_commands as commands
from vcos_data import VCOSData as Data

# Initialise all data
data = Data()


def move_cursor(d, v):
    """
    Moves the cursor in the selected direction by the provided number of characters

    Parameters:
    d - selected direction
    v - amount to move the cursor
    """

    for i in range(v):

        if d == "U":
            if i == 1:
                commands.update_command_window(data, "Scroll Up " + str(v))

        if cursor_scroll_v != 0:
            cursor_scroll_v += -1

        elif d == "D":
            if i == 1:
                commands.update_command_window(data, "Scroll Down " + str(v))

        if cursor_scroll_v < data.window_rows - 1 or (cursor_scroll_v + screen_scroll_v) < len(text_box):
            cursor_scroll_v += 1

        elif d == "L":
            if i == 1:
                commands.update_command_window(data, "Scroll Left " + str(v))

    if cursor_scroll_h != 0:
        cursor_scroll_h += -1

    elif d == "R":
        if i == 1:
            commands.update_command_window(data, "Scroll Right " + str(v))

    if cursor_scroll_h < editor_cols:
        cursor_scroll_h += 1

    elif d == "SU":
        print("su trigger")
    if screen_scroll_v > 0:
        screen_scroll_v += -1

    elif d == "SD":
        print("sd trigger")
    if screen_scroll_v < file_line_limit - data.window_rows:
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
        commands.update_command_window(data.window_rows, "Scroll Right Failed")

    update_text_window()


def render_image(file_dir):
    file_dir = file_dir.replace('\\', '/')

    # Blocks the renderer if no file is open
    if file_dir == "":
        commands.update_command_window(data.window_rows, "File not loaded")
    else:
        # Assemble the command to run the renderer
        out_file = '"' + file_dir.replace(".scad", ".png") + '"'
        full_command = ".\\openscad\\openscad.com -o " + "\"" + out_file[2:] + " " + '"' + file_dir[1:] + '"'

        # Run the renderer on the current file and update the command window once complete
        subprocess.run(full_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        commands.update_command_window(data, "Render complete")


def input_parser() -> object:
    """
    A recursive function for input detection
    """

    commands.update_command_window(data, "back at parser")
    response = commands.record_audio(data)
    commands.update_header_box(data, 1)

    try:
        # Exit
        if search("exit", response):
            curses.endwin()
            quit()

        # Add Text
        elif i == 32:
            commands.add_text(data, "@")
            commands.update_text_window(data)

        # Scroll Cursor Left
        elif search("scroll left", response):
            try:
                move_cursor('L', int(commands.text_to_int(response.split("left", 1)[1])))
            except IndexError:
                commands.update_command_window(data.window_rows, "Please specify how far to scroll")

        # Scroll Cursor Right
        elif search("scroll right", response):
            try:
                move_cursor('R', int(commands.text_to_int(response.split("right", 1)[1])))
            except IndexError:
                commands.update_command_window(data.window_rows, "Please specify how far to scroll")

        # Scroll Cursor Up
        elif search("scroll up", response):
            try:
                move_cursor('U', int(commands.text_to_int(response.split("up", 1)[1])))
            except IndexError:
                commands.update_command_window(data.window_rows, "Please specify how far to scroll")

        # Scroll Cursor Down
        elif search("scroll down", response):
            try:
                move_cursor('D', int(commands.text_to_int(response.split("down", 1)[1])))
            except IndexError:
                commands.update_command_window(data.window_rows, "Please specify how far to scroll")

        elif response == 119:
            move_cursor('SU', 1)

        elif response == 115:
            move_cursor('SD', 1)

        elif response == 97:
            move_cursor('SL', 1)

        elif response == 100:
            move_cursor('SR', 1)

        # Enter Key - New Line
        elif response == 10:

            new_text_box = []

            for a in range(len(data.text_box)):
                new_text_box.append(data.text_box[i])

                if a == data.cursor_scroll_v:
                    new_text_box.append("")

            text_box = new_text_box

            commands.update_text_window(data)

        # Load File
        elif search("load", response):
            commands.update_command_window(data, "Load")
            commands.update_command_window(data, " ")
            commands.show_projects(data)

        # Help
        elif search("help", response):
            commands.update_command_window(data, "VCOS Help:")
            commands.update_command_window(data, "'help' - Shows this help window")
            commands.update_command_window(data, "'load' - Starts the loading dialog")
            commands.update_command_window(data, "'scroll [direction] [amount]' - Moves the cursor")
            commands.update_command_window(data, "'screen [direction] [amount]' - Scrolls the text view")
            commands.update_command_window(data, "'render' - Renders the current loaded project in OpenSCAD")

        # Render image
        elif search("render", response):
            render_image(data.file_path)

    except ValueError:
        pass

    input_parser()

    print(data)


# Setup curses runtime
curses.noecho()
curses.cbreak()
curses.start_color()
normalText = curses.A_NORMAL
curses.curs_set(0)
data.screen_main.keypad(True)

# Curses colour pairs
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

# Initialise curses screens

# Main Screen

# Command Interpreter

for i in range(data.window_rows):
    commands.update_command_window(data, "")

data.refresh_screen(0)
data.refresh_screen(1)
data.refresh_screen(2)

commands.update_command_window(data, "Command Interpreter Ready")
commands.update_command_window(data, "Say 'help' for a list of commands")
input_parser()
quit()
