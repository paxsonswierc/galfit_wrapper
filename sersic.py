
from astropy.io import fits
import os
import pyds9
import pyregion
import numpy as np
import math
from region_to_psf import input_to_galfit
import subprocess
import shutil

class Sersic():

    def __init__(self, filter, target_file, ouput_dir, galfit_path,
                 target_filename, config_file=None,
                 config_output_file=None, mask=None,
                 psf=None):
        self.filter = filter
        self.target_file = target_file
        self.ouput_dir = ouput_dir
        self.galfit_path = galfit_path
        self.target_filename = target_filename
        self.config_file = config_file
        self.config_output_file = config_output_file
        self.mask = mask
        self.psf = psf

    def create_config(self, d):
        if self.psf.model_file is None:
            print('Please create or upload psf first')
        else:
            d.set("fits new "+self.target_file)
            d.set("scale mode 99.5")
            d.set("mode region")
            d.set("region shape ellipse")
            input('Place ellipses for galaxies. Hit enter when region is placed\n')
            d.set("region shape point")
            input('Place point for point sources. Hit enter when region is placed\n')
            d.set("region shape box")
            input('Place box for frame. Hit enter when region is placed\n')
            psf_regions = d.get("region")

            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'

            input_to_galfit(self.target_file, False, psf_regions, 32.5,
                            self.config_file, output_fits, output_mask)

            d.set('region select all')
            d.set('region delete select')

            optimize = input('Run galfit for this config? Hit enter for yes, type no otherwise')
            if optimize != 'no':
                self.optimize_config(d)

    def edit_config(self, d):
        assert self.config_file is not None

    def edit_config_text(self):
        assert self.config_file is not None

    def optimize_config(self, d):
        if self.config_file is None:
            print('Please create or upload config file first')
        else:
            subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+self.config_file])
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            print("galfit run done, loading into DS9...")
            d.set("mecube new "+output_fits)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")

            prompt = '''What would you like to do? Enter ->
            1: Save this model and config
            2: Edit the output config of this model (continue process)
            3: Reset from last stage and edit last config'''
            next_step = input(prompt)
            if next_step == '1':
                # os.remove(self.config_file)
                # shutil.copyfile('galfit.01', self.config_file)
                output_fits_final = self.ouput_dir + self.target_filename + 'model.fits'
                os.remove('galfit.01')
                os.rename(output_fits, output_fits_final)
                self.config_output_file = output_fits_final

            if next_step == '2':
                pass
            #     os.remove(self.config_file)
            #     shutil.copyfile('galfit.01', self.config_file)

            # done = input('Are you satisfied? yes/enter to continue, no to restart > ')
            # if done == 'no':
            #     self.write_config(d)
            
            # self.config_file = output_config
            # self.config_output_file = output_fits

            # hdul = fits.open(output_fits)
            # data = hdul[2].data
            # fits.writeto(output_model, data, overwrite=True)

            # self.model_file = output_model

    def visualize(self, d):
        if self.config_output_file is None:
            print('Please upload or create psf model first')
        else:
            d.set("mecube new "+ self.config_output_file)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")

    def upload_config(self, file):
        self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
        if file != self.config_file:
            shutil.copyfile(file, self.config_file)

    def upload_model(self, file):
        self.config_output_file = self.ouput_dir + self.target_filename + '_config.txt'