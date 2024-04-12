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
        d.set("scale mode 99.5")
        d.set("mode region")
        # Prompt user to place point region on star
        d.set("region shape point")
        input('Place point for star. Hit enter when region is placed\n')
        # Prompt user to place box region for area to run model
        d.set("region shape box")
        input('Place box for frame. Hit enter when region is placed\n')
        psf_regions = d.get("region")
        # Establish filenames
        output_config = self.ouput_dir + self.target_filename + '_psf_config.txt'
        output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
        output_model = self.ouput_dir + self.target_filename + '_psf_model.fits'
        output_mask = self.ouput_dir + self.target_filename + '_psf_mask.fits'
        # Set galfit config file
        input_to_galfit(self.target_file, True, psf_regions, self.zero_point,
                        output_config, output_fits, output_mask, 'none',
                        False, False)
        # Delete old regions
        d.set('region select all')
        d.set('region delete select')
        # Get rid of any old psf models
        if os.path.exists(output_fits):
                os.remove(output_fits)
        # Run galfit
        subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+output_config])
        # Check if galfit ran correctly
        if os.path.exists(output_fits):
            # Remove galfit output file
            os.remove('galfit.01')
            print("galfit run done, loading into DS9...")
            # Load model into ds9
            d.set("mecube new "+output_fits)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")
            # Prompt user to see if model is satisfactory
            done = input('Are you satisfied? yes/enter to continue, no to restart, or quit > ')
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
            print('Galfit crashed! Please try again')

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
            print("Please upload or create psf model first")
        else:
            hdulist = fits.open(self.config_output_file)
            galfitheader = hdulist[2].header
            galfit_flags = galfitheader["FLAGS"].split()
            for flag in galfit_flags:
                print("-",flag_dict[flag])
            print()