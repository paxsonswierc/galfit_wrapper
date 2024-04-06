# Event runner for galfit wrapper TUI.

import os
import pyds9
from astropy.io import fits
from psf import PSF
from sersic import Sersic
from utils import get_paths, my_filebrowser

def take_action(action: str) -> None:
    '''
    Handles inputs from TUI

    Args:
        action: input command

    Returns: Nothing
    '''
    actions = {'help': help,
               'target visualize': visualize_target,
               'psf create': psf_write_config,
               'psf visualize': psf_visualize,
               'psf upload': psf_upload,
               'sersic create config': sersic_create_config,
               'sersic edit config': sersic_edit_config,
               'sersic optimize config': sersic_optimize,
               'sersic visualize': sersic_visualize,
               'sersic upload config': sersic_upload_config,
               'sersic upload model': sersic_upload_model,
               'mult fits': mult_fits}
    if action not in actions:
        print('Unkown command. Type help for assistance')
    else:
        actions[action]()

def help():
    '''
    Prints out available commands for user
    '''
    text = '''
    Commands:
    quit

    target visualize

    psf create
    psf visualize
    psf upload

    sersic create config
    sersic edit config
    sersic optimize config
    sersic visualize
    sersic upload config
    sersic upload model
    '''
    print(text)

# Functions to execute commands

def visualize_target():
    '''
    Opens target image in ds9
    '''
    d.set("fits new " + target_path)
    d.set("scale mode 99.5")

def psf_write_config():
    '''
    psf create - makes new psf from scratch using regions
    '''
    psf.write_config(d)

def psf_visualize():
    '''
    Opens psf in ds9 if psf exists
    '''
    psf.visualize(d)

def psf_upload():
    '''
    Opens prompt to upload psf fits file, copying it to output dir
    '''
    psf_file = my_filebrowser()
    psf.upload_psf(psf_file)

def sersic_create_config():
    '''
    Create overall config using regions
    '''
    sersic.create_config(d)

def sersic_edit_config():
    '''
    Edit a created or uploaded model config
    '''
    sersic.edit_config(d)

def sersic_optimize():
    '''
    Run existing model config through galfit
    '''
    sersic.optimize_config(d)

def sersic_visualize():
    '''
    Visualize model
    '''
    sersic.visualize(d)

def sersic_upload_config():
    '''
    Uploads model config file, copying it to output dir
    '''
    config_file = my_filebrowser()
    sersic.upload_config(config_file, d)

def sersic_upload_model():
    '''
    Uploads finished model fits file, copying it to output dir
    '''
    model_file = my_filebrowser()
    sersic.upload_model(model_file)

def mult_fits():
    '''
    Specialty function for DELVE data. Multiplies data by 10000 and adjusts
    header
    '''
    data, header = fits.getdata(target_path, header=True)
    header['EXPTIME'] = 1.0
    header['GAIN'] = 1.0
    data = data*10000
    fits.writeto(target_path, data, header, overwrite=True)

if __name__ == '__main__':
    # Commands that if called, trigger ds9 to open
    ds9_commands = ['target visualize', 'psf create', 'psf visualize',
                    'sersic create config', 'sersic edit config',
                    'sersic optimize config', 'sersic visualize',
                    'sersic upload config']
    # Reads in paths from local config file. If none, prompts user for them
    path_to_galfit, path_to_output, galfit_output = get_paths()
    # Prompts user for target fits file to be worked on
    target_path = my_filebrowser()
    if target_path[-5:] != '.fits':
        print('###\nError: please upload .fits type target file\n###')
        quit()
    # Get filename and path to directory for target
    target_filename = target_path.split('/')[-1][:-5]
    path_to_output += target_filename + '/'
    # Check if output directory for this file already exists
    if os.path.exists(path_to_output + '/'):
        # Initialize possible data as None
        psf_config_file = None
        psf_config_output_file = None
        psf_model_file = None
        psf_mask = None
        sersic_config_file = None
        sersic_config_output_file = None
        sersic_mask = None
        # Check for any saved data in output dir and add path for it
        files = os.listdir(path_to_output + '/')
        for file in files:
            if file == target_filename + '_psf_config.txt':
                psf_config_file = path_to_output + file

            if file == target_filename + '_psf.fits':
                psf_config_output_file = path_to_output + file
    
            if file == target_filename + '_psf_model.fits':
                psf_model_file = path_to_output + file

            if file == target_filename + '_psf_mask.fits':
                psf_mask = path_to_output + file

            if file == target_filename + '_config.txt':
                sersic_config_file = path_to_output + file

            if file == target_filename + '_model.fits':
                sersic_config_output_file = path_to_output + file

            if file == target_filename + '_mask.fits':
                sersic_mask = path_to_output + file
        # Initialize psf and sersic objects
        psf = PSF('?', target_path, path_to_output, path_to_galfit,
                  target_filename, psf_config_file,
                  psf_config_output_file, psf_model_file, psf_mask)
        sersic = Sersic('?', target_path, path_to_output, path_to_galfit,
                  target_filename, sersic_config_file,
                  sersic_config_output_file, sersic_mask, psf)
    else:
        # Create output directory and initialize psf/sersic objects empty
        os.mkdir(path_to_output + '/')
        psf = PSF('?', target_path, path_to_output, path_to_galfit,
                  target_filename)
        sersic = Sersic('?', target_path, path_to_output, path_to_galfit,
                  target_filename)

    # Initialize event loop
    print('Welcome to galfit wrapper. Type help for assistance')
    software_open = True
    ds9_open = False
    # Begin event loop
    while software_open:
        action = input(' > ')
        if not ds9_open:
            if action in ds9_commands:
                ds9_open = True
                d = pyds9.DS9()
        if action == ('quit'):
            software_open = False
            if ds9_open:
                d.set('exit')
        else:
            take_action(action)
