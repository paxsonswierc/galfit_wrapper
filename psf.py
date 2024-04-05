# Base class for PSF
from astropy.io import fits
import os
import pyds9
import pyregion
import numpy as np
import math
from region_to_config import input_to_galfit
import subprocess
import shutil

class PSF():

    def __init__(self, filter, target_file, ouput_dir, galfit_path,
                 target_filename, config_file=None,
                 config_output_file=None, model_file=None, mask=None):
        self.filter = filter
        self.target_file = target_file
        self.ouput_dir = ouput_dir
        self.galfit_path = galfit_path
        self.target_filename = target_filename
        self.config_file = config_file
        self.config_output_file = config_output_file
        self.model_file = model_file
        self.mask = mask

    def write_config(self, d):
        d.set("fits new "+self.target_file)
        d.set("scale mode 99.5")
        d.set("mode region")
        d.set("region shape point")
        input('Place point for star. Hit enter when region is placed\n')
        d.set("region shape box")
        input('Place box for frame. Hit enter when region is placed\n')
        psf_regions = d.get("region")

        output_config = self.ouput_dir + self.target_filename + '_psf_config.txt'
        output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
        output_model = self.ouput_dir + self.target_filename + '_psf_model.fits'
        output_mask = self.ouput_dir + self.target_filename + '_psf_mask.fits'

        input_to_galfit(self.target_file, True, psf_regions, 32.5,
                        output_config, output_fits, output_mask)

        d.set('region select all')
        d.set('region delete select')

        subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+output_config])
        os.remove('galfit.01')

        print("galfit run done, loading into DS9...")
        d.set("mecube new "+output_fits)
        d.set("scale mode minmax")
        d.set("mode none")
        d.set("zoom to fit")
        d.set("cube play")

        done = input('Are you satisfied? yes/enter to continue, no to restart > ')
        if done == 'no':
            self.write_config(d)
        
        self.config_file = output_config
        self.config_output_file = output_fits

        hdul = fits.open(output_fits)
        data = hdul[2].data
        fits.writeto(output_model, data, overwrite=True)

        self.model_file = output_model

    def visualize(self, d):
        if self.config_output_file is None and self.model_file is None:
            print('Please upload or create psf model first')
        elif self.config_output_file is not None:
            d.set("mecube new "+ self.config_output_file)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")
        elif self.model_file is not None:
            d.set("fits new "+ self.model_file)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")

    def upload_psf(self, filename):
        hdul = fits.open(filename)

        output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
        output_model = self.ouput_dir + self.target_filename + '_psf_model.fits'

        if len(hdul) == 1:
            if filename != output_model:
                shutil.copyfile(filename, output_model)
        else:
            if filename != output_fits:
                shutil.copyfile(filename, output_fits)
            self.config_output_file = output_fits
            data = hdul[2].data
            fits.writeto(output_model, data, overwrite=True)
        self.model_file = output_model
