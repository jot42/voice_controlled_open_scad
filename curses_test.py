import curses
from re import search

import libs.vcos_commands as commands


def input_parser():
    """
    A function that serves as the main loop for the program
    """

    response = commands.symbol_translate(commands.record_audio())
    commands.update_header_box(2)

    try:
        if not response == "":

            # Help
            if search("help", response):
                commands.update_command_window("VCOS Help:")
                commands.update_command_window("'help' - Shows this help window")
                commands.update_command_window("'exit' - Exits this program")
                commands.update_command_window("'load' - Starts the loading dialog")
                commands.update_command_window("'create file' - Starts the new file dialog")
                commands.update_command_window("'scroll [direction] [amount]' - Moves the cursor")
                commands.update_command_window("'screen [direction] [amount]' - Scrolls the text view")
                commands.update_command_window("'insert text [phrase]' - Inserts the spoken text")
                commands.update_command_window("'render' - Renders the current loaded project in OpenSCAD")
                commands.update_command_window("")
                commands.update_command_window("Ready.")
                commands.update_command_window("")

            # Exit
            elif search("exit", response):
                curses.endwin()
                quit()

            # Load File
            elif search("load", response):
                commands.update_command_window("Load")
                commands.update_command_window("")
                commands.load_file_dialog()
                commands.update_command_window("Ready.")
                commands.update_command_window("")

            # Create File
            elif search("create file", response):
                commands.update_command_window("Create File")
                commands.update_command_window("")
                commands.create_new_file_dialog()
                commands.update_command_window("Ready.")
                commands.update_command_window("")

            # Scroll Cursor Left
            elif search("scroll left", response):
                try:
                    commands.move_cursor('L', int(commands.symbol_translate(response.split("left", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Cursor Right
            elif search("scroll right", response):
                try:
                    commands.move_cursor('R', int(commands.symbol_translate(response.split("right", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Cursor Up
            elif search("scroll up", response):
                try:
                    commands.move_cursor('U', int(commands.symbol_translate(response.split("up", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Cursor Down
            elif search("scroll down", response):
                try:
                    commands.move_cursor('D', int(commands.symbol_translate(response.split("down", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Screen Left
            elif search("screen left", response):
                try:
                    commands.move_cursor('SL', int(commands.symbol_translate(response.split("left", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Screen Right
            elif search("screen right", response):
                try:
                    commands.move_cursor('SR', int(commands.symbol_translate(response.split("right", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Screen Up
            elif search("screen up", response):
                try:
                    commands.move_cursor('SU', int(commands.symbol_translate(response.split("up", 1)[1])), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Scroll Screen Down
            elif search("screen down", response):
                try:
                    commands.move_cursor('SD', commands.symbol_translate(response.split("down", 1)[1]), True)
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to scroll")

            # Add Text
            elif search("insert text", response):
                try:
                    commands.update_command_window("Insert Text")
                    commands.add_text(response.split("text ", 1)[1])

                except IndexError:
                    commands.update_command_window("Please specify the text to add")

                commands.update_command_window("Ready.")
                commands.update_command_window("")

            # Remove Text
            elif search("backspace", response):
                try:
                    commands.remove_text(int(commands.symbol_translate(response.split("backspace", 1)[1])))
                    commands.update_command_window("Ready.")
                    commands.update_command_window("")
                except IndexError:
                    commands.update_command_window("Please specify how far to backspace")

            # Insert New Line
            elif search("insert line", response):
                commands.update_command_window("Insert Line")
                commands.update_command_window("")
                commands.insert_new_line()
                commands.update_command_window("Ready.")
                commands.update_command_window("")

            # Delete Line
            elif search("delete line", response):
                commands.update_command_window("Delete Line")
                commands.update_command_window("")
                commands.remove_line()
                commands.update_command_window("Ready.")
                commands.update_command_window("")

            # Render image
            elif search("render", response):
                commands.update_command_window("Rendering Project")
                commands.update_command_window("")
                commands.render_image(commands.data.scad_file_path)
                commands.update_command_window("Ready.")
                commands.update_command_window("")

            elif search("save", response):
                commands.update_command_window("Saving Project")
                commands.update_command_window("")
                commands.save_file()

    except ValueError:
        pass


if __name__ == "__main__":
    # Setup curses runtime
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    normalText = curses.A_NORMAL
    curses.curs_set(0)
    commands.data.screen_main.keypad(True)

    # Curses colour pairs
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

    commands.data.screen_main.refresh()
    commands.data.screen_border_commands.refresh()
    commands.data.screen_border_editor.refresh()

    commands.update_header_box(0)
    commands.update_command_window("Calibrating your microphone, please wait")
    commands.calibrate_audio()

    commands.update_command_window("Ready.")
    commands.update_command_window("Say 'help' for a list of commands")
    commands.update_command_window("")

    while True:
        input_parser()
