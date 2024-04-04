# $HOME/galfit/galfit
# $HOME/galfit_outputs
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory 
import os
from psf import PSF
from sersic import Sersic

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

def write_path_config():
    path_to_galfit = input('Path to your galfit executable? > ')
    path_to_output = input('Folder you would like to save outputs > ')
    paths_file = open('path_config.txt', 'w')
    paths_file.write(path_to_galfit + '\n' + path_to_output)
    paths_file.close()

def take_action(action):
    actions = {'help': help}
    if action not in actions:
        print('Unkown command. Type help for assistance')
    else:
        actions[action]()

def help():
    text = '''
    Commands:
    quit
    
    
    TODO
    psf
        upload config
        upload finished model
        create config
        edit config (direct/galfit)
        optimize config
        visualize
    sersic
        upload psf
        upload config
        create config
        edit config (direct/galfit)
        optimize config
        visualize
    '''
    print(text)

def my_filebrowser():
    root = Tk()
    root.withdraw()
    filename = askopenfilename()
    # print(type(filename))
    # root.quit()
    # root.destroy()
    return filename

if __name__ == '__main__':
    path_to_galfit, path_to_output, galfit_output = get_paths()

    target_path = my_filebrowser()
    if target_path[-5:] != '.fits':
        print('###\nError: please upload .fits type target file\n###')
        quit()

    target_filename = target_path.split('/')[-1][:-5]

    if os.path.exists(path_to_output + target_filename + '/'):
        pass #TODO auto load everything in
        psf = PSF('?')
        sersic = Sersic('?')
    else:
        os.mkdir(path_to_output + target_filename + '/')

    path_to_output += target_filename + '/'

    software_open = True

    print('Welcome to galfit wrapper. Type help for assistance')

    test = my_filebrowser()

    while software_open == True:
        print(test, target_path)
        action = input(' > ')
        if action == ('quit'):
            software_open = False
        else:
            take_action(action)