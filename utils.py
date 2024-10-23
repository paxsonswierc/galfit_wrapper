# Util functions for galfit wrapper
# Authors: Paxson Swierc & Daniel Babnigg

import tkinter as tk
from tkinter.filedialog import askopenfilename 
from tkinter import Tk
from tkinter import filedialog
import os
import sys

def write_path_config() -> None:
    '''
    Prompts input for paths and writes them to path_config.txt
    '''
    # TODO: add error messages/loop to check for existing path
    path_to_galfit = input('Path to your galfit executable? > ')
    path_to_galfit = os.path.abspath(path_to_galfit)

    paths_file = open('path_config.txt', 'w')
    paths_file.write(path_to_galfit)
    paths_file.close()

def get_paths() -> tuple[str, str, str]:
    '''
    Reads in paths from path_config.txt
    '''
    if not os.path.exists('galfit_wrapper.py'):
        print("you must run galfit wrapper from the dircetory that contains the galfit_wrapper.py file.")
        sys.exit()
    if not os.path.exists('path_config.txt'):
        paths_file = open('path_config.txt', 'w')
        paths_file.close()
    paths_file = open('path_config.txt')
    paths = paths_file.readlines()
    # If config empty, prompt input
    if len(paths) == 0:
        write_path_config()
        paths_file = open('path_config.txt')
        paths = paths_file.readlines()

    path_to_galfit = paths[0]
    path_to_output = os.path.expanduser('~/gf_out/')
    if not os.path.exists(path_to_output):
        os.makedirs(path_to_output)
    # Get directory where galfit will dump config files
    galfit_output = os.path.dirname(path_to_galfit)
    # TODO add os way to do this
    # Add slash to end of path to output
    path_to_output = os.path.join(path_to_output, '')

    return path_to_galfit, path_to_output, galfit_output

def my_filebrowser():
    '''
    Opens GUI file explorer to choose path to file
    '''
    root = Tk()
    root.withdraw()
    filename = askopenfilename()
    return filename

def open_textfile(path_to_file):
    '''
    Opens GUI text editor
    '''
    # saves file (overwrites) then quits window
    def save_file():
        with open(path_to_file, "w") as file:
            file.write(text_widget.get("1.0", tk.END))
        root.after(1, root.destroy())
        root.quit()

    # initializes GUI
    root = Tk()
    root.title("Text Editor")

    # prepares GUI for input of text file
    text_widget = tk.Text(root, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True)

    # opens given file in GUI
    with open(path_to_file, "r") as file:
        text_widget.delete(1.0,tk.END)
        text_widget.insert(tk.END,file.read())

    # adds a button to save file after edits
    save_button = tk.Button(root, text="Save", command=save_file)
    save_button.pack(side=tk.LEFT,padx=5,pady=5)

    # starts the tkinter loop (ends once file is saved)
    root.mainloop()