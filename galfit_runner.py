# $HOME/galfit/galfit
# $HOME/galfit_outputs
import os
import pyds9
from astropy.io import fits
from psf import PSF
from sersic import Sersic
from utils import get_paths, my_filebrowser

def take_action(action):
    actions = {'help': help,
               'psf create': psf_write_config,
               'psf visualize': psf_visualize,
               'psf upload': psf_upload,
               'target visualize': visualize_target,
               'mult fits': mult_fits}
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

def psf_write_config():
    psf.write_config(d)

def psf_visualize():
    psf.visualize(d)

def psf_upload():
    psf_file = my_filebrowser()
    psf.upload_psf(psf_file)

def visualize_target():
    d.set("fits new "+target_path)
    d.set("scale mode 99.5")

def mult_fits():
    data, header = fits.getdata(target_path, header=True)
    header['EXPTIME'] = 1.0
    header['GAIN'] = 1.0
    data = data*10000
    fits.writeto(target_path, data, header, overwrite=True)

if __name__ == '__main__':
    path_to_galfit, path_to_output, galfit_output = get_paths()

    target_path = my_filebrowser()
    if target_path[-5:] != '.fits':
        print('###\nError: please upload .fits type target file\n###')
        quit()

    target_filename = target_path.split('/')[-1][:-5]
    path_to_output += target_filename + '/'

    if os.path.exists(path_to_output + '/'):
        #TODO auto load everything in
        files = os.listdir(path_to_output + '/')
        config_file = None
        config_output_file = None
        model_file = None
        mask = None
        for file in files:
            if file == target_filename + '_psf_config.txt':
                config_file = path_to_output + file

            if file == target_filename + '_psf.fits':
                config_output_file = path_to_output + file
    
            if file == target_filename + '_psf_model.fits':
                model_file = path_to_output + file

            if file == target_filename + '_psf_mask.fits':
                mask = path_to_output + file

        psf = PSF('?', target_path, path_to_output, path_to_galfit,
                  target_filename, config_file,
                  config_output_file, model_file, mask)
        sersic = Sersic('?')
    else:
        os.mkdir(path_to_output + '/')
        psf = PSF('?', target_path, path_to_output, path_to_galfit,
                  target_filename)
        sersic = Sersic('?')

    software_open = True

    print('Welcome to galfit wrapper. Type help for assistance')

    #test = my_filebrowser()
    d = pyds9.DS9()
    d.set("fits new "+target_path)
    d.set("scale mode 99.5")

    while software_open == True:
        action = input(' > ')
        if action == ('quit'):
            software_open = False
            d.set('exit')
        else:
            take_action(action)