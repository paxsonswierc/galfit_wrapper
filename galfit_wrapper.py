# Event runner for galfit wrapper TUI
# Author: Paxson Swierc

import os
import sys
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
               'change zero point': edit_zero_point,
               'psf create': psf_write_config,
               'psf visualize': psf_visualize,
               'psf upload': psf_upload,
               'psf flags': psf_flags,
               'sersic create config': sersic_create_config,
               'sersic add constraint': sersic_add_constraint,
               'sersic remove constraint': sersic_remove_constraint,
               'sersic edit config': sersic_edit_config,
               'sersic optimize config': sersic_optimize,
               'sersic visualize': sersic_visualize,
               'sersic upload config': sersic_upload_config,
               'sersic upload model': sersic_upload_model,
               'sersic upload constraint': sersic_upload_constraint,
               'sersic flags': sersic_flags,
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

    change zero point

    psf create
    psf visualize
    psf upload
    psf flags

    sersic create config
    sersic edit config
    sersic add constraint
    sersic remove constraint
    sersic optimize config
    sersic visualize
    sersic upload config
    sersic upload model
    sersic upload constraint
    sersic flags
    '''
    print(text)

# Functions to execute commands

def visualize_target():
    '''
    Opens target image in ds9
    '''
    d.set("fits new " + target_path)
    d.set("scale mode 99.5")

def edit_zero_point():
    '''
    Changes zero point saved in file
    '''
    zero_point = input('What is the zero point of the image? Input number and hit enter > ')
    # Write to zero point file for future reference
    zero_point_file = open(path_to_output + 'zero_point.txt', 'w')
    zero_point_file.write(zero_point)
    zero_point_file.close()
    zero_point = float(zero_point)
    psf.zero_point = zero_point
    sersic.zero_point = zero_point

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

def psf_flags():
    '''
    Prints out any flags in existing psf galfit file
    '''
    psf.flags()

def sersic_create_config():
    '''
    Create overall config using regions
    '''
    sersic.create_config(d)

def sersic_add_constraint():
    '''
    Creates constraint file for sersic config
    '''
    sersic.add_constraint()

def sersic_remove_constraint():
    '''
    Removes constraint file for sersic config
    '''
    sersic.remove_constraint()

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

def sersic_upload_constraint():
    '''
    Uploads constraint txt file, copying it to output dir
    '''
    constraint_file = my_filebrowser()
    sersic.upload_constraint(constraint_file)

def sersic_flags():
    '''
    Prints out any flags in existing model galfit file
    '''
    sersic.flags()

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

    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            # Checks for input path to target
            target_path = sys.argv[1]
        else:
            print('Please input a valid target path!')
            quit()
    else:
        # Prompts user for target fits file to be worked on
        target_path = my_filebrowser()
    if target_path[-5:] != '.fits':
        print('###\nError: please upload .fits type target file\n###')
        quit()
    # Make path to directory for target
    target_filename = os.path.basename(target_path)[:-5]
    path_to_output = os.path.join(path_to_output, target_filename, '')
    # Check if output directory for this file already exists
    if not os.path.exists(path_to_output):
        # Should only happen when user manually changes path_config.txt
        os.makedirs(path_to_output)
    # Initialize possible data as None
    psf_config_file = None
    psf_config_output_file = None
    psf_model_file = None
    psf_mask = None
    sersic_config_file = None
    sersic_config_output_file = None
    sersic_constraint = None
    sersic_mask = None
    # Check for zero point file
    if not os.path.exists(path_to_output + 'zero_point.txt'):
        zero_point = input('What is the zero point of the image? Input number and hit enter > ')
        # Write to zero point file for future reference
        zero_point_file = open(path_to_output + 'zero_point.txt', 'w')
        zero_point_file.write(zero_point)
        zero_point_file.close()
        zero_point = float(zero_point)
    else:
        # Load in zero point info
        zero_point_file = open(path_to_output + 'zero_point.txt')
        zero_point = zero_point_file.readlines()
        zero_point = float(zero_point[0])
    # Check for any saved data in output dir and add path for it
    files = os.listdir(path_to_output)
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

        if file == target_filename + '_constraint.txt':
            sersic_constraint = path_to_output + file

        if file == target_filename + '_mask.fits':
            sersic_mask = path_to_output + file
        
    # Initialize psf and sersic objects
    psf = PSF('?', target_path, path_to_output, path_to_galfit,
                target_filename, zero_point, psf_config_file,
                psf_config_output_file, psf_model_file, psf_mask)
    sersic = Sersic('?', target_path, path_to_output, path_to_galfit,
                target_filename, zero_point, sersic_config_file,
                sersic_config_output_file, sersic_mask, sersic_constraint, psf)

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
