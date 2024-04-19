# Event runner for galfit wrapper TUI
# Author: Paxson Swierc & Daniel Babnigg

import os
import sys
import time
import shutil
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
               '?': help,
               'h': help,
               'target list': list_target,
               'target l': list_target,
               'tl': list_target,
               'ls': list_target,
               'target visualize': visualize_target,
               'target v': visualize_target,
               'tv': visualize_target,
               'target visualize rgb': visualize_target_rgb,
               'target v rgb': visualize_target_rgb,
               'tv rgb': visualize_target_rgb,
               'change zero point': edit_zero_point,
               'change zpt': edit_zero_point,
               'cz': edit_zero_point,
               'psf create': psf_write_config,
               'psf c': psf_write_config,
               'pc': psf_write_config,
               'psf visualize': psf_visualize,
               'psf v': psf_visualize,
               'pv': psf_visualize,
               'psf flags': psf_flags,
               'psf f': psf_flags,
               'pf': psf_flags,
               'psf upload': psf_upload,
               'psf u': psf_upload,
               'pu': psf_upload,
               'sersic create config': sersic_create_config,
               'sersic cc': sersic_create_config,
               'scc': sersic_create_config,
               'sersic add constraint': sersic_add_constraint,
               'sersic add c': sersic_add_constraint,
               'sac': sersic_add_constraint,
               'sersic remove constraint': sersic_remove_constraint,
               'sersic rm c': sersic_remove_constraint,
               'src': sersic_remove_constraint,
               'sersic edit config': sersic_edit_config,
               'sersic ec': sersic_edit_config,
               'sec': sersic_edit_config,
               'sersic optimize config': sersic_optimize,
               'sersic oc': sersic_optimize,
               'soc': sersic_optimize,
               'sersic visualize': sersic_visualize,
               'sersic v': sersic_visualize,
               'sv': sersic_visualize,
               'sersic visualize rgb': sersic_visualize_rgb,
               'sersic v rgb': sersic_visualize_rgb,
               'sv rgb': sersic_visualize_rgb,
               'sersic flags': sersic_flags,
               'sersic f': sersic_flags,
               'sf': sersic_flags,
               'sersic upload config': sersic_upload_config,
               'sersic uc': sersic_upload_config,
               'suc': sersic_upload_config,
               'sersic upload model': sersic_upload_model,
               'sersic um': sersic_upload_model,
               'sum': sersic_upload_model,
               'sersic upload constraint': sersic_upload_constraint,
               'sersic ucst': sersic_upload_constraint,
               'sucst': sersic_upload_constraint,
               'mult fits': mult_fits}
    if action not in actions:
        print('\nUnkown command. Type help for assistance\n')
    else:
        actions[action]()

def help():
    '''
    Prints out available commands for user
    '''
    text = '''
    Commands:
    quit

    target list
    target visualize
    target visualize rgb

    change zero point

    psf create
    psf visualize
    psf flags
    psf upload

    sersic create config
    sersic edit config
    sersic add constraint
    sersic remove constraint
    sersic optimize config
    sersic visualize
    sersic visualize rgb
    sersic flags
    sersic upload config
    sersic upload model
    sersic upload constraint
    '''
    print(text)

# Functions to execute commands

def list_target():
    '''
    Checks progress in the given directory
    '''
    def get_time(file_name):
        '''
        Given a file path, returns the last modified date/time in nice format
        '''
        time_obj = time.strptime(time.ctime(os.path.getmtime(os.path.join(path_to_output,file_name))))

        return str(time.strftime("%Y-%m-%d %H:%M:%S", time_obj))

    files = os.listdir(path_to_output)
    file_,psfc_,psf_,c_,m_ = False,False,False,False,False
    for file in files:
        if file == target_filename + ".fits":
            file_ = True
        if file == target_filename + '_psf_config.txt':
            psfc_ = True
        if file == target_filename + '_psf.fits':
            psf_ = True
        if file == target_filename + '_config.txt':
            c_ = True
        if file == target_filename + '_model.fits':
            m_ = True
    print("\nCurrently Saved:")
    if file_:
        print('- '+get_time(target_filename+".fits")+'\t'+(target_filename+".fits")+'             '+'original file')
    if psfc_:
        print('- '+get_time(target_filename + "_psf_config.txt")+'\t'+(target_filename + "_psf_config.txt")+'   '+'psf config')
    if psf_:
        print('- '+get_time(target_filename + "_psf.fits")+'\t'+(target_filename + "_psf.fits")+'         '+'psf model FITS')
    if c_:
        print('- '+get_time(target_filename + "_config.txt")+'\t'+(target_filename + "_config.txt")+'       '+'model config')
    if m_:
        print('- '+get_time(target_filename + "_model.fits")+'\t'+(target_filename + "_model.fits")+'       '+'multi-band model FITS')
    print()
    
def visualize_target():
    '''
    Opens target image in ds9
    '''
    d.set("fits new " + target_path)
    d.set("tile no")
    d.set("cmap 1 0.5")
    d.set("scale mode 99.5")
    d.set("zoom to fit")

def visualize_target_rgb():
    '''
    Opens rgb image of target in ds9
    '''
    if os.path.exists(path_to_output + 'rgb_info.txt'):
        r_file, g_file, b_file = open(path_to_output + 'rgb_info.txt', 'r').read().splitlines()[:3]
        sersic.visualize_rgb(r_file, g_file, b_file, True, d)
    else:
        print("\nUpload 3 single-band fits in red, green, blue order\n")
        r_file = my_filebrowser()
        g_file = my_filebrowser()
        b_file = my_filebrowser()
        with open(path_to_output + 'rgb_info.txt', 'w') as rgb_info:
            rgb_info.write(str(r_file)+'\n')
            rgb_info.write(str(g_file)+'\n')
            rgb_info.write(str(b_file)+'\n')
        sersic.visualize_rgb(r_file, g_file, b_file, True, d)

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

def psf_flags():
    '''
    Prints out any flags in existing psf galfit file
    '''
    psf.flags()

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

def sersic_visualize_rgb():
    '''
    Visualize the target rgb vs the model rgb, taking 3 bands as inputs
    '''
    if not os.path.exists(path_to_output + 'rgb_info.txt'):
        print("\nRun target visualize rgb first to get correct scaling\n")
    elif len(open(path_to_output + 'rgb_info.txt', 'r').read().splitlines()) != 9:
        print("\nUpload 3 multi-band model files (*_model.fits) in red, green, blue order\n")
        r_file = my_filebrowser()
        g_file = my_filebrowser()
        b_file = my_filebrowser()
        with open(path_to_output + 'rgb_info.txt', 'a') as rgb_info:
            rgb_info.write(str(r_file)+'\n')
            rgb_info.write(str(g_file)+'\n')
            rgb_info.write(str(b_file))
        sersic.visualize_rgb(r_file, g_file, b_file, False, d)
    else:
        r_file, g_file, b_file = open(path_to_output + 'rgb_info.txt', 'r').read().splitlines()[6:9]
        sersic.visualize_rgb(r_file, g_file, b_file, False, d)

def sersic_flags():
    '''
    Prints out any flags in existing model galfit file
    '''
    sersic.flags()

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
    ds9_commands = ['target visualize', 'target v', 'tv',
                    'target visualize rgb', 'target v rgb', 'tv rgb',
                    'psf create', 'psf c', 'pc',
                    'psf visualize', 'psf v', 'pv',
                    'sersic create config', 'sersic cc', 'scc',
                    'sersic edit config', 'sersic ec', 'sec',
                    'sersic optimize config', 'sersic oc', 'soc',
                    'sersic visualize', 'sersic v', 'sv',
                    'sersic visualize rgb', 'sersic v rgb', 'sv rgb',
                    'sersic upload config', 'sersic uc', 'suc']
    # Reads in paths from local config file. If none, prompts user for them
    path_to_galfit, path_to_output, galfit_output = get_paths()

    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            # Checks for input path to target
            target_path = sys.argv[1]
        else:
            print('\nPlease input a valid target path!\n')
            quit()
    else:
        # Prompts user for target fits file to be worked on
        print("\nPlease choose .fits type target file\n")
        target_path = my_filebrowser()
    if target_path[-5:] != '.fits':
        print('\nError: please upload .fits type target file\n')
        quit()
    # Make path to directory for target
    target_filename = os.path.basename(target_path)[:-5]
    path_to_output = os.path.join(path_to_output, target_filename, '')
    # Check if output directory for this file already exists
    if not os.path.exists(path_to_output):
        # Should only happen when user manually changes path_config.txt
        os.makedirs(path_to_output)
    # Copy target file to output dir
    if not os.path.exists(path_to_output + os.path.basename(target_path)):
        shutil.copyfile(target_path, path_to_output + os.path.basename(target_path))
    target_path = path_to_output + os.path.basename(target_path)
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
    print('\nWelcome to galfit wrapper. Type help for assistance\n')
    software_open = True
    ds9_open = False
    # Begin event loop
    while software_open:
        action = input(' > ')
        if not ds9_open:
            if action in ds9_commands:
                ds9_open = True
                d = pyds9.DS9()
                d.set("frame delete all")
        if action == ('quit') or action == ('exit'):
            software_open = False
            if ds9_open:
                d.set('exit')
        else:
            take_action(action)
