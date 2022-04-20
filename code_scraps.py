# Find the longest line in the file
    for i in range(len(text_box)):
        if len(text_box[i]) > current_longest_length:
            current_longest_index = i
            current_longest_length = len(text_box[i])

    # Ensure all other lines match the length by adding
    for i in range(len(text_box)):
        if i != current_longest_index:
            while len(text_box[i]) < current_longest_length:
                text_box[i] = text_box[i] + " "




def load_file():
    f = open(os.getcwd() + "\\projects\\example_3.scad", "r")

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

    if update_text_window():
        update_command_window(editor_rows, "load")