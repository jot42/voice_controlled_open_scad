import curses
import platform


class VCOSData:
    # System variables
    version = '0.0.1'

    # Determine user operating system
    if platform.system() == 'Linux':
        os_id = "L"
    elif platform.system() == 'Darwin':
        os_id = "M"
    elif platform.system() == "Windows":
        os_id = "W"

    # Scrolling Values
    cursor_scroll_h = 0
    cursor_scroll_v = 0
    screen_scroll_h = 0
    screen_scroll_v = 0

    # Text Buffers
    command_log = []
    text_box = []

    # The preset limit for file sizes
    file_column_limit = 1000
    file_line_limit = 1000

    # Initialise main screen
    screen_main = curses.initscr()

    # Window Sizes

    # Get sub-window size and assign border size
    r, c = screen_main.getmaxyx()
    border_rows = int(r - 4)
    border_cols = int(c - 59)

    # Set sub-window size based on border size
    window_rows = border_rows - 2
    command_cols = 57
    editor_cols = border_cols - 2

    # Screen Data
    screen_border_commands = curses.newwin(border_rows, command_cols + 2, 4, 0)
    screen_container_commands = screen_main.subwin(window_rows, command_cols, 5, 1)

    # Initialise Sub-window Data
    screen_border_editor = curses.newwin(border_rows, border_cols, 4, command_cols + 2)
    screen_container_editor = screen_main.subwin(window_rows, editor_cols, 5, command_cols + 3)

    # Create borders for text boxes
    screen_border_commands.box()
    screen_border_editor.box()

    # File handling
    scad_file_path = ''  # Used to pass to the OpenSCAD renderer
    project_file_path = ''  # Used to load and save the current project
