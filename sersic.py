
from astropy.io import fits
import os
import pyds9
import pyregion
import numpy as np
import math
from region_to_config import input_to_galfit
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
            regions = d.get("region")

            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'

            input_to_galfit(self.target_file, False, regions, 32.5,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, False)

            d.set('region select all')
            d.set('region delete select')

            optimize = input('Run galfit for this config? Hit enter for yes, type no otherwise')
            if optimize != 'no':
                self.optimize_config(d)

    def edit_config(self, d):
        if self.config_file is None:
            print('Please create config file first')
        else:
            d.set("fits new "+self.target_file)
            d.set("scale mode 99.5")
            d.set("mode region")
            box = self.config_to_region(d)
            d.set("region shape ellipse")
            input('Make any wanted changes. Hit enter to optimize')

            regions = d.get("region")

            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'

            input_to_galfit(self.target_file, False, regions, 32.5,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, box)

            self.optimize_config(d)

    def edit_config_text(self):
        assert self.config_file is not None

    def optimize_config(self, d):
        if self.config_file is None:
            print('Please create or upload config file first')
        else:
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            if os.path.exists(output_fits):
                os.remove(output_fits)
            subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+self.config_file])
            print('Fitting finished')
            if os.path.exists(output_fits):
                print("galfit run done, loading into DS9...")
                d.set("mecube new " + output_fits)
                d.set("scale mode minmax")
                d.set("mode none")
                d.set("zoom to fit")
                d.set("cube play")

                prompt = '''What would you like to do? Enter ->
1: Save this model and config
2: Edit the output config of this model (continue process)
3: Reset from last stage and edit last config
 > '''
                next_step = input(prompt)
                if next_step == '1':
                    # os.remove(self.config_file)
                    # shutil.copyfile('galfit.01', self.config_file)
                    output_fits_final = self.ouput_dir + self.target_filename + '_model.fits'
                    os.remove('galfit.01')
                    os.rename(output_fits, output_fits_final)
                    self.config_output_file = output_fits_final

                if next_step == '2':
                    os.remove(self.config_file)
                    shutil.copyfile('galfit.01', self.config_file)
                    #os.rename(self.ouput_dir + 'galfit.01', self.config_file)
                    os.remove('galfit.01')
                    self.edit_config(d)

                if next_step == '3':
                    os.remove('galfit.01')
                    self.edit_config(d)
                    #self.optimize_config(d)

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
            else:
                print('Galfit crashed. Please edit/remake config file and try again.')

    def visualize(self, d):
        if self.config_output_file is None:
            print('Please upload or create psf model first')
        else:
            d.set("mecube new "+ self.config_output_file)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")

    def upload_config(self, file, d):
        if self.psf.model_file is None:
            print('Please create or upload psf first')
        else:
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            if file != self.config_file:
                shutil.copyfile(file, self.config_file)
            box = self.config_to_region(d)

            regions = d.get("region")

            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'

            input_to_galfit(self.target_file, False, regions, 32.5,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, box)

    def upload_model(self, file):
        self.config_output_file = self.ouput_dir + self.target_filename + '_config.txt'
        if file != self.config_output_file:
            shutil.copyfile(file, self.config_output_file)

    def config_to_region(self, d):
        assert self.config_file is not None

        d.set("fits new "+self.target_file)
        d.set("scale mode 99.5")

        config = open(self.config_file, 'r')
        lines = config.readlines()

        for i, line in enumerate(lines):
            if 'sersic' in line and 'sersic,' not in line:
                for component_line in lines[i+1:]:
                    words = component_line.split()
                    if '1)' in component_line:
                        x = float(words[1])
                        y = float(words[2])
                    elif '4) ' in component_line and '=4)' not in component_line:
                        a = float(words[1])
                    elif '9)' in component_line:
                        b_over_a = float(words[1])
                        b = b_over_a * a
                    elif '10)' in component_line:
                        angle = float(words[1])
                        if angle >= 270:
                            angle -= 90
                        else:
                            angle += 90
                    if '0)' in component_line or component_line == lines[-1]:
                        d.set(f'region command "ellipse {x} {y} {a} {b} {angle}"')
                        break
            if '0) psf' in line:
                for component_line in lines[i+1:]:
                    words = component_line.split()
                    if '1)' in component_line:
                        x = float(words[1])
                        y = float(words[2])
                    if '0)' in component_line or component_line == lines[-1]:
                        d.set(f'region command "point {x} {y}"')
                        break
            if 'H)' in line:
                words = line.split()
                x_min = int(words[1])
                x_max = int(words[2])
                y_min = int(words[3])
                y_max = int(words[4])
            if 'I)' in line:
                words = line.split()
                x_center = int(words[1])
                y_center = int(words[2])

        config.close()

        return [x_min, x_max, y_min, y_max, x_center, y_center]
