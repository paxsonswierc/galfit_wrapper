from tkinter.filedialog import askopenfilename, askdirectory 
from tkinter import Tk

def write_path_config():
    path_to_galfit = input('Path to your galfit executable? > ')
    path_to_output = input('Folder you would like to save outputs > ')
    paths_file = open('path_config.txt', 'w')
    paths_file.write(path_to_galfit + '\n' + path_to_output)
    paths_file.close()

def get_paths():
    paths_file = open('path_config.txt')
    paths = paths_file.readlines()

    if len(paths) == 0:
        write_path_config()
        paths_file = open('path_config.txt')
        paths = paths_file.readlines()

    path_to_galfit = paths[0][:-1]
    path_to_output = paths[1]

    for i in range(len(path_to_galfit)):
        if path_to_galfit[-1*i - 1] == '/':
            galfit_output = path_to_galfit[:-i]
            break
    
    if path_to_output[-1] != '/':
        path_to_output += '/'

    return path_to_galfit, path_to_output, galfit_output

def my_filebrowser():
    root = Tk()
    root.withdraw()
    filename = askopenfilename()
    # print(type(filename))
    # root.quit()
    # root.destroy()
    return filename

