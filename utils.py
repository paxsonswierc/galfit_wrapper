# Util functions for galfit wrapper
# Author: Paxson Swierc

from tkinter.filedialog import askopenfilename, askdirectory 
from tkinter import Tk
import os

def write_path_config() -> None:
    '''
    Prompts input for paths and writes them to path_config.txt
    '''
    # TODO: add error messages/loop to check for existing path
    path_to_galfit = input('Path to your galfit executable? > ')
    path_to_galfit = os.path.abspath(path_to_galfit)

    #path_to_output = input('Folder you would like to save outputs > ')
    # if not os.path.exists(path_to_output):
    #     os.makedirs(path_to_output)
    # path_to_output = os.path.abspath(path_to_output)

    paths_file = open('path_config.txt', 'w')
    paths_file.write(path_to_galfit) #+ '\n' + path_to_output)
    paths_file.close()

def get_paths() -> tuple[str, str, str]:
    '''
    Reads in paths from path_config.txt
    '''
    paths_file = open('path_config.txt', 'w')
    paths = paths_file.readlines()
    # If config empty, prompt input
    if len(paths) == 0:
        write_path_config()
        paths_file = open('path_config.txt')
        paths = paths_file.readlines()

    path_to_galfit = paths[0]#[:-1]
    #path_to_output = paths[1]
    path_to_output = os.path.expanduser('~/gf_out/')
    print(path_to_output)
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
