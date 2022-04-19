from email.headerregistry import ContentTransferEncodingHeader
import os
import json
import pandas as pd

if __name__ == "__main__":
    pass  

def parse_config_entry(line):
    char_buffer = ""
    config_dict_key = ""
    config_dict_value = ""

    for char in line:
        if char == ':':
            config_dict_key = char_buffer.replace(" ","")
            char_buffer = ""

        if char != "\"":
            char_buffer = char_buffer + char

    config_dict_value = char_buffer.replace(":","").replace(",","").strip()

    return (config_dict_key, config_dict_value)

def config_mode():
    
    #Menu Loop
    run_menu = True

    print("System Information")
    if os.name == "nt":
        print("OS: Windows")
    elif os.name == "posix":
        print("OS: UNIX")

    while(run_menu):
        print("")
        print("Voice Controlled OpenSCAD Configuration Menu")
        print("1. Change Deepspeech settings")
        print("2. Run Voice Controlled OpenSCAD")
        print("3. Quit")
        print("")
        user_option = input('>')

        if user_option == '1':
            config = open('deepspeech-server/server-config.json')
            config_dict = {}

            for line in config:
                if line.startswith("    \"model\""):
                    option = parse_config_entry(line)
                    config_dict[option[0]] = option[1]

                if line.startswith("    \"scorer\""):
                    option = parse_config_entry(line)
                    config_dict[option[0]] = option[1]

                if line.startswith("      \"host\""):
                    option = parse_config_entry(line)
                    config_dict[option[0]] = option[1]

                if line.startswith("      \"port\""):
                    option = parse_config_entry(line)
                    config_dict[option[0]] = option[1]

                if line.startswith("      \"request_max_size\""):
                    option = parse_config_entry(line)
                    config_dict[option[0]] = option[1]


            print("The following settings are available:")
            for item in config_dict:
                print("-", item)

            print("q : Return to menu\n")

            #Run deepspeech config menu
            while(run_menu):
                print("DEBUG: Dict length = ", len(config_dict))
                print("please select an option:")
                user_option = input(">").lower()
                print(user_option)

                try:
                    if user_option == "q":
                        run_menu = False
                    else:
                        if user_option in config_dict:
                            print(config_dict[user_option])
                        else:
                            print("Invalid Option")
                except:
                    print()

            #Reenable menu loop var after deepspeech config exit
            run_menu = True
            
        elif user_option == '2':
            print("Running VCOS")

        elif user_option == '3':
            
            while(run_menu):
                user_save = input("Do you want to save changes? (y/n)")
                if user_save == 'y' or user_save == 'Y':
                    print('saving')
                    quit()
                if user_save == 'n' or user_save == 'N':
                    print('not saving')
                    quit()