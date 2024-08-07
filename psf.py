# Class for PSF models
# Author: Paxson Swierc & Daniel Babnigg

from astropy.io import fits
import os
from region_to_config import input_to_galfit
import subprocess
import shutil

class PSF():
    '''
    Class to track galfit psf model for a given fits file.

    Attributes:
        filter: fits image band
        target_file: path to the target fits file
        output_dir: directory where model outputs are saved
        galfit_path: path to galfit
        target_filename: filename of target
        zero_point: zero point of target image
        config_file: path to galfit configuration file for a point source
        config_output_file: path to fits file outputted by galfit (4 frames)
        model_file: path to fits file with model frame from galfit output
        mask: path to mask fits file for galfit

    Methods:
        write_config: creates galfit config file with ds9 
        visualize: opens up psf model in ds9
        upload_psf: copies uploaded psf model to dir and loads it to instance
        flags: prints flags from galfit model
    '''
    def __init__(self, filter: str, target_file: str, ouput_dir: str,
                 galfit_path: str, target_filename: str, zero_point: float,
                 config_file: str|None =None, config_output_file: str|None =None,
                 model_file: str|None =None, mask: str|None =None):
        self.filter = filter
        self.target_file = target_file
        self.ouput_dir = ouput_dir
        self.galfit_path = galfit_path
        self.target_filename = target_filename
        self.zero_point = zero_point
        self.config_file = config_file
        self.config_output_file = config_output_file
        self.model_file = model_file
        self.mask = mask

    def write_config(self, d) -> None:
        '''
        Creates galfit config and optimizes it, from user inputted ds9 regions.
        Opens ds9 window of target to prompt for region input

        Args:
            d: pyds9 DS9 instance

        Returns: Nothing
        '''
        # Open ds9 window
        d.set("fits new "+self.target_file)
        d.set("tile no")
        d.set("cmap 1 0.5")
        d.set("scale mode 99.5")
        d.set("zoom to fit")
        d.set("mode region")
        # Prompt user to place circle region on star
        d.set("region shape circle")
        input('\nPlace circle for star. Hit enter when region is placed')
        # Prompt user to place box region for area to run model
        d.set("region shape box")
        input('\nPlace box for frame. Hit enter when region is placed')
        psf_regions = d.get("region -system image")
        # Establish filenames
        output_config = self.ouput_dir + self.target_filename + '_psf_config.txt'
        output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
        output_model = self.ouput_dir + self.target_filename + '_psf_model.fits'
        output_mask = self.ouput_dir + self.target_filename + '_psf_mask.fits'
        # Set galfit config file
        input_to_galfit(self.target_file, True, psf_regions, self.zero_point,
                        output_config, output_fits, output_mask, 'none',
                        False, False, False, [0]*4, 'none', 'none')
        self.config_file = output_config
        # Delete old regions
        d.set('region select all')
        d.set('region delete select')
        # Get rid of any old psf models
        if os.path.exists(output_fits):
                os.remove(output_fits)
        # Run galfit
        subprocess.run(['/bin/bash', '-c', str(self.galfit_path.rstrip()+' '+self.config_file)])
        # subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+output_config])
        # Check if galfit ran correctly
        if os.path.exists(output_fits):
            # Remove galfit output file
            os.remove('galfit.01')
            print("\ngalfit run done, loading into DS9...")
            # Load model into ds9
            d.set("mecube new "+output_fits)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")
            # Prompt user to see if model is satisfactory
            done = input('\nAre you satisfied? yes/enter to continue, no to restart, or quit > ')
            if done == 'no':
                # Repeat process if unsatisfied
                self.write_config(d)
            if done != 'quit':
                # Save changes as long as user did not quit out
                self.config_file = output_config
                self.config_output_file = output_fits

                hdul = fits.open(output_fits)
                data = hdul[2].data
                fits.writeto(output_model, data, overwrite=True)

                self.model_file = output_model

        else:
            print('\nGalfit crashed! Please try again\n')

    def optimize_config_(self, d) -> None:
        '''
        Optimizes a galfit model based on config file (TEMP COPY)

        Args:
            d: pyds9 DS9 instance
        
        Returns: Nothing
        '''
        if self.config_file is None:
            print('\nPlease create or upload psf galfit config file first\n')
        else:
            config = open(self.config_file, 'r')
            lines = config.readlines()
            
            comp_num = 0
            comp_type = ""
            for i, line in enumerate(lines):
                # check for a line that contains the start of a component
                if 'Component number:' in line:
                    comp_num += 1
                words = line.split()
                # gets the component type (psf, sersic, sky, etc.)
                if '0)' in line and '=0)' not in line and '10)' not in line:
                    comp_type = words[1]
                if comp_type == 'sky':
                    if 'Z)' in line:
                        lines[i] = "Z) 1\n"
            config.close()
            # Write update to config file
            with open(self.config_file, 'w') as file:
                file.writelines(lines)

            # Get rid of any previous galfit output config files
            if os.path.exists('galfit.01'):
                os.remove('galfit.01')
            # Final output file
            output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
            output_config = self.ouput_dir + self.target_filename + '_psf_config.txt'
            output_model = self.ouput_dir + self.target_filename + '_psf_model.fits'
            # Remove any previous temporary model outputs
            if os.path.exists(output_fits):
                os.remove(output_fits)
            # Run galfit
            # subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+self.config_file])
            # print(str(self.galfit_path.rstrip()+' '+self.config_file))
            subprocess.run(['/bin/bash', '-c', str(self.galfit_path.rstrip()+' '+self.config_file)])
            print('\nFitting finished')
            # Check if galfit was successful
            if os.path.exists(output_fits) and os.path.exists('galfit.01'):
                print("\ngalfit run done, loading into DS9...\n")
                # Open output in ds9
                d.set("mecube new " + output_fits)
                d.set("tile no")
                d.set("cmap 1 0.5")
                d.set("scale mode minmax")
                d.set("mode none")
                d.set("zoom to fit")
                d.set("cube play")

                # Save changes as long as user did not quit out
                self.config_file = output_config
                self.config_output_file = output_fits

                hdul = fits.open(output_fits)
                data = hdul[2].data
                fits.writeto(output_model, data, overwrite=True)

                self.model_file = output_model
            else:
                if os.path.exists(output_fits):
                    print('\nCorrupted output. Check for buffer overflow.\nMay have to do with output directory path or target fits file path being too long\n')
                else:
                    print('\nGalfit crashed. Please edit/remake config file and try again\n')

    def visualize(self, d) -> None:
        '''
        Visualizes psf model using ds9. Will prioritize showing full 4 frames
        from galfit output, but will display only single model frame if only
        that was uploaded.

        Args:
            d: pyds9 DS9 instance
        
        Returns: nothing
        '''
        if self.config_output_file is None and self.model_file is None:
            print('\nPlease upload or create psf model first\n')
        elif self.config_output_file is not None:
            d.set("mecube new "+ self.config_output_file)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")
        elif self.model_file is not None:
            d.set("fits new "+ self.model_file)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")

    def upload_psf(self, filename: str) -> None:
        '''
        Prompts user to upload psf model. Takes full 4 frame image
        and will create a single frame model fits file if so. Also accepts
        the single frame model file.

        Args:
            filename: name of uploaded file

        Returns: Nothing
        '''
        hdul = fits.open(filename)

        output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
        output_model = self.ouput_dir + self.target_filename + '_psf_model.fits'

        if len(hdul) == 1:
            # Copy single frame image
            if filename != output_model:
                shutil.copyfile(filename, output_model)
        else:
            # Copy 4 frame galfit output and make 1 frame model fits file
            if filename != output_fits:
                shutil.copyfile(filename, output_fits)
            self.config_output_file = output_fits
            data = hdul[2].data
            fits.writeto(output_model, data, overwrite=True)
        self.model_file = output_model

    def flags(self) -> None:
        '''
        Finds all model files in the directory, including PSF/full models,
        and prints out flags for each file that give information about
        the galfit optimization process.

        Args: None

        Returns: Nothing
        '''
        # dictionary containing meanings of all possible flags
        flag_dict = {
                    "1": "Maximum number of iterations reached.  Quit out early.",
                    "2": "Suspected numerical convergence error in current solution.",
                    "A-1": "No input data image found. Creating model only.",
                    "A-2": "PSF image not found.  No convolution performed.",
                    "A-3": "No CCD diffusion kernel found or applied.",
                    "A-4": "No bad pixel mask image found.",
                    "A-5": "No sigma image found.",
                    "A-6": "No constraint file found.",
                    "C-1": "Error parsing the constraint file.",
                    "C-2": "Trying to constrain a parameter that is being held fixed.",
                    "H-1": "Exposure time header keyword is missing.  Default to 1 second.",
                    "H-2": "Exposure time is zero seconds.  Default to 1 second.",
                    "H-3": "GAIN header information is missing.",
                    "H-4": "NCOMBINE header information is missing.",
                    "I-1": "Convolution PSF exceeds the convolution box.",
                    "I-2": "Fitting box exceeds image boundary.",
                    "I-3": "Some pixels have infinite ADUs; set to 0.",
                    "I-4": "Sigma image has zero or negative pixels; set to 1e10.",
                    "I-5": "Pixel mask is not same size as data image."
                    }

        if self.config_output_file is None:
            print("\nPlease upload or create psf model first\n")
        else:
            hdulist = fits.open(self.config_output_file)
            galfitheader = hdulist[2].header
            galfit_flags = galfitheader["FLAGS"].split()
            print()
            for flag in galfit_flags:
                print("-",flag_dict[flag])
            print()
