# Class for sersic models
# Author: Paxson Swierc & Daniel Babnigg

from astropy.io import fits
import os
from region_to_config import input_to_galfit
import subprocess
import shutil

class Sersic():
    '''
    Class to track galfit sersic model for a given fits file.

    Attributes:
        filter: fits image band
        target_file: path to the target fits file
        output_dir: directory where model outputs are saved
        galfit_path: path to galfit
        target_filename: filename of target
        zero_point: zero point of target image
        config_file: path to galfit configuration file for a point source
        config_output_file: path to fits file outputted by galfit (4 frames)
        mask: path to mask fits file for galfit
        constraint_file: path to constraint file for galfit
        psf: instance of psf class

    Methods:
        create_config: creates galfit config file with ds9 
        edit_config: allows editing of current config with ds9
        optimize_config: runs galfit for current config file
        visualize: opens up psf model in ds9
        upload_config: copies uploaded config to dir and loads it to instance
        upload_model: copies uploaded model to dir and loads it to instance
        upload_constraint: copies uploaded constraint to dir and loads it
        config_to_region: converts current config file back into ds9 regions
        add_constraint: creates a galfit constraint file
        remove_constraint: removes a galfit constraint file
        flags: prints flags from galfit model
    '''
    def __init__(self, filter: str, target_file: str, ouput_dir: str,
                 galfit_path: str, target_filename: str, zero_point: float,
                 config_file: str|None =None, config_output_file: str|None =None,
                 mask: str|None =None, constraint: str|None =None, psf=None):
        self.filter = filter
        self.target_file = target_file
        self.ouput_dir = ouput_dir
        self.galfit_path = galfit_path
        self.target_filename = target_filename
        self.zero_point = zero_point
        self.config_file = config_file
        self.config_output_file = config_output_file
        self.mask = mask
        if constraint is None:
            self.constraint_file = 'none'
        else:
            self.constraint_file = constraint
        self.psf = psf

    def create_config(self, d) -> None:
        '''
        Creates galfit config and optimizes it, from user inputted ds9 regions.
        Opens ds9 window of target to prompt for region input

        Args:
            d: pyds9 DS9 instance

        Returns: Nothing
        '''
        if self.psf.model_file is None:
            print('Please create or upload psf first')
        else:
            # Open target in ds9
            d.set("fits new "+self.target_file)
            d.set("scale mode 99.5")
            d.set("mode region")
            # Prompt user to place ellipse region for galaxies
            d.set("region shape ellipse")
            input('Place ellipses for galaxies. Hit enter when region is placed\n')
            # Prompt user to place point region for psf component
            d.set("region shape point")
            input('Place point for point sources. Hit enter when region is placed\n')
            d.set("region shape box")
            input('Place box for frame. Hit enter when region is placed\n')
            regions = d.get("region")
            # Establish filenames
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'
            # Set galfit config file
            input_to_galfit(self.target_file, False, regions, self.zero_point,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, False, False, False, [0]*4,
                            self.constraint_file)
            # Get rid of regions
            d.set('region select all')
            d.set('region delete select')
            # Optimize with galfit config
            optimize = input('Run galfit for this config? Hit enter for yes, type no otherwise > ')
            if optimize != 'no':
                self.optimize_config(d)

    def edit_config(self, d) -> None:
        '''
        Reopens config file as regions as ds9 to be edited

        Args:
            d: pyds9 DS9 instnce

        Returns: Nothing
        '''
        if self.config_file is None:
            print('Please create config file first')
        else:
            # Open target in ds9
            d.set("fits new "+self.target_file)
            d.set("scale mode 99.5")
            d.set("mode region")
            # Ask for manual edits first
            input(f'Please make any manual edits to config text file located at {self.config_file} first. Hit enter to continue')
            # Load in regions
            box, mags, psf_mags, sky_info = self.config_to_region(d)
            d.set("region shape ellipse")
            # Constrained changes
            input(f'Make any changes to existing regions (these changes will be constrained). Hit enter to continue')
            # Add constraing based on input
            add_constraint = input('Add constraint? Hit enter for yes, type no otherwise > ')
            if add_constraint == 'no':
                self.remove_constraint()
            else:
                self.add_constraint()
            # Give option to add new regions
            input('Add any new regions now (these will not be constrained). Hit enter to continue')
            # Get regions
            regions = d.get("region")
            # Establish output files
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'
            # Write to galfit config file
            input_to_galfit(self.target_file, False, regions, self.zero_point,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, box, mags, psf_mags, sky_info,
                            self.constraint_file)
            # Optimize with new config file
            self.optimize_config(d)

    def optimize_config(self, d) -> None:
        '''
        Optimizes a galfit model based on config file

        Args:
            d: pyds9 DS9 instance
        
        Returns: Nothing
        '''
        if self.config_file is None:
            print('Please create or upload config file first')
        else:
            # Get rid of any previous galfit output config files
            if os.path.exists('galfit.01'):
                os.remove('galfit.01')
            # Final output file
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            # Remove any previous temporary model outputs
            if os.path.exists(output_fits):
                os.remove(output_fits)
            # Run galfit
            subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+self.config_file])
            print('Fitting finished')
            # Check if galfit was successful
            if os.path.exists(output_fits) and os.path.exists('galfit.01'):
                print("galfit run done, loading into DS9...")
                # Open output in ds9
                d.set("mecube new " + output_fits)
                d.set("scale mode minmax")
                d.set("mode none")
                d.set("zoom to fit")
                d.set("cube play")
                # Prompt next decision to user. Any other input exits loop
                prompt = '''What would you like to do? Enter ->
1: Save this model and config
2: Edit the output config of this model (continue process)
3: Reset from last stage and edit last config
 > '''
                next_step = input(prompt)
                if next_step == '1':
                    # Save the model and config
                    output_fits_final = self.ouput_dir + self.target_filename + '_model.fits'
                    os.remove('galfit.01')
                    os.rename(output_fits, output_fits_final)
                    self.config_output_file = output_fits_final

                elif next_step == '2':
                    # Replace this config with galfit output config
                    os.remove(self.config_file)
                    shutil.copyfile('galfit.01', self.config_file)
                    os.remove('galfit.01')
                    # Continue editing loop
                    self.edit_config(d)

                elif next_step == '3':
                    # Remove galfit output config and go back to editing
                    os.remove('galfit.01')
                    # Continue editing loop
                    self.edit_config(d)

            else:
                if os.path.exists(output_fits):
                    print('Corrupted output. Check for buffer overflow.\nMay have to do with output directory path or target fits file path being too long.')
                else:
                    print('Galfit crashed. Please edit/remake config file and try again.')

    def visualize(self, d) -> None:
        '''
        Visualizes sersic model using ds9

        Args: 
            d: pyds9 DS9 instance

        Returns: Nothing
        '''
        if self.config_output_file is None:
            print('Please upload or create sersic model first')
        else:
            d.set("mecube new "+ self.config_output_file)
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")

    def upload_config(self, file: str, d) -> None:
        '''
        Prompts user to upload config file and copies it to output dir

        Args:
            file: path to upload file

        Returns: Nothing
        '''
        if self.psf.model_file is None:
            print('Please create or upload psf first')
        else:
            # Update config filename
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            if file != self.config_file:
                shutil.copyfile(file, self.config_file)
            # Convert config to regions to get info on box size
            box, mags, psf_mags, sky_info = self.config_to_region(d)

            regions = d.get("region")
            # Establish filenames
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'
            # Write new galfit config (to update filenames in the uploaded)
            input_to_galfit(self.target_file, False, regions, self.zero_point,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, box, mags, psf_mags, sky_info,
                            self.constraint_file)

    def upload_model(self, file: str) -> None:
        '''
        Prompts user to upload already completed model file. This would be for
        visualization purposes generally. Makes a copy of the file in
        output directory

        Args:
            file: path to upload file

        Returns: Nothing
        '''
        self.config_output_file = self.ouput_dir + self.target_filename + '_config.txt'
        if file != self.config_output_file:
            shutil.copyfile(file, self.config_output_file)

    def upload_constraint(self, file: str) -> None:
        '''
        Uploads constraint and copies the file to output directory

        Args:
            file: path to upload file

        Returns: Nothing
        '''
        self.constraint_file = self.ouput_dir + self.target_filename + '_constraint.txt'
        if file != self.constraint_file:
            shutil.copyfile(file, self.constraint_file)

        # Update config file
        with open(self.config_file, 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if 'G)' in line:
                lines[i] = f'G) {self.constraint_file}\n'
        with open(self.config_file, 'w') as file:
            file.writelines(lines)

    def config_to_region(self, d) -> tuple[list[int], list[float]]:
        '''
        Converts a galfit config file into ds9 regions
        '''
        # TODO: add magnitude memory for psf components
        assert self.config_file is not None
        # Open target file into ds9
        d.set("fits new "+self.target_file)
        d.set("scale mode 99.5")
        # Keep track of magnitudes of all components
        magnitudes = []
        psf_magnitudes = []
        sky_info = [0, 0, 0, 0]
        config = open(self.config_file, 'r')
        lines = config.readlines()

        for i, line in enumerate(lines):
            # Check for sersic component
            if 'sersic' in line and 'sersic,' not in line:
                for component_line in lines[i+1:]:
                    words = component_line.split()
                    if '1)' in component_line:
                        # Get position info
                        x = float(words[1])
                        y = float(words[2])
                    elif '3)' in component_line:
                        # Get magnitude info
                        magnitudes.append(float(words[1]))
                    elif '4) ' in component_line and '=4)' not in component_line:
                        # Get effective radius
                        a = float(words[1])
                    elif '9)' in component_line:
                        # Get axis ratio
                        b_over_a = float(words[1])
                        b = b_over_a * a
                    elif '10)' in component_line:
                        # Get angle
                        angle = float(words[1])
                        if angle >= 270:
                            angle -= 90
                        else:
                            angle += 90
                    if '0)' in component_line or component_line == lines[-1]:
                        # Set ellipse region
                        d.set(f'region command "ellipse {x} {y} {a} {b} {angle}"')
                        break
            # Check for psf component
            if '0) psf' in line:
                for component_line in lines[i+1:]:
                    words = component_line.split()
                    if '1)' in component_line:
                        # Get position info
                        x = float(words[1])
                        y = float(words[2])
                    elif '3)' in component_line:
                        # Get magnitude info
                        psf_magnitudes.append(float(words[1]))
                    if '0)' in component_line or component_line == lines[-1]:
                        # Set region
                        d.set(f'region command "point {x} {y}"')
                        break
            if '0) sky' in line:
                for component_line in lines[i+1:]:
                    words = component_line.split()
                    if '1)' in component_line:
                        sky_info[3] = float(words[1])
                    elif '2)' in component_line:
                        sky_info[0] = float(words[1])
                        sky_info[2] = int(words[2])
                    elif '3)' in component_line:
                        sky_info[1] = float(words[1])
                        sky_info[2] = int(words[2])
                    if '0)' in component_line or component_line == lines[-1]:
                        break
                    
            if 'H)' in line:
                words = line.split()
                # Save box information
                x_min = int(words[1])
                x_max = int(words[2])
                y_min = int(words[3])
                y_max = int(words[4])
            if 'I)' in line:
                words = line.split()
                # Save box information
                x_center = int(words[1])
                y_center = int(words[2])

        config.close()
        return [x_min, x_max, y_min, y_max, x_center, y_center],\
                magnitudes, psf_magnitudes, sky_info
    
    def add_constraint(self) -> None:
        '''
        Creates constraint file for galfit config and adds it to config file

        Args: None

        Returns: Nothing
        '''
        if self.config_file is None:
                print('Please create or upload galfit config file first')
        else:
            self.constraint_file = self.ouput_dir + self.target_filename + '_constraint.txt'

            config = open(self.config_file, 'r')
            lines = config.readlines()
            
            constraint_lines = []
            comp_num = 0
            comp_type = ""
            for i, line in enumerate(lines):
                # check for a line that contains the start of a component
                if 'Component number:' in line:
                    comp_num += 1
                words = line.split()
                # gets the component type (psft, sersic, sky, etc.)
                if '0)' in line and '=0)' not in line and '10)' not in line:
                    comp_type = words[1]
                # excludes sky component type in constraints (and other unsupported types)
                if comp_type == 'psf' or comp_type == 'sersic' or comp_type == 'moffat':
                    # constraints the x and y to +/- 1 pixels
                    if '1)' in line:
                        constraint_lines.append(f"{comp_num} x -1 1")
                        constraint_lines.append(f"{comp_num} y -1 1")
                    # constraints the magnitude to +/- 4 apparent magnitudes
                    elif '3) ' in line:
                        constraint_lines.append(f"{comp_num} 3 -4 4")
                    # excludes psf component type, since other constraints don't apply
                    if comp_type == 'sersic' or comp_type == 'moffat':
                        # constraints the FWHM by +/- 10% of value
                        if '4) ' in line:
                            a = float(words[1])
                            constraint_lines.append(f"{comp_num} 4 -{0.1*a:.5f} {0.1*a:.5f}")
                        # constraints the sersic index/moffat powerlaw to +/- 10% of value
                        if '5) ' in line:
                            index = float(words[1])
                            constraint_lines.append(f"{comp_num} 5 -{0.1*index:.5f} {0.1*index:.5f}")
                        # constraints the axis ratio to +/- 10% of value
                        elif '9) ' in line:
                            b_over_a = float(words[1])
                            constraint_lines.append(f"{comp_num} 9 -{0.1*b_over_a:.5f} {0.1*b_over_a:.5f}")
                        # constraints the rotation to +/- 5 degrees
                        elif '10) ' in line:
                            constraint_lines.append(f"{comp_num} 10 -5 5")
                # Add constraint to config
                if 'G)' in line:
                    lines[i] = f'G) {self.constraint_file}\n'
            config.close()
            # Write update to config file
            with open(self.config_file, 'w') as file:
                file.writelines(lines)
            # creates a text file from list of constraints     
            constraint_contents = "\n".join(constraint_lines)
            with open(self.constraint_file, 'w') as h:
                h.write("\n".join(constraint_lines))

    def remove_constraint(self) -> None:
        '''
        Removes constraint file

        Args: None

        Returns: Nothing
        '''
        if self.constraint_file != 'none':

            if os.path.exists(self.constraint_file):
                os.remove(self.constraint_file)
            self.constraint_file = 'none'

        if self.config_file is None:
            print('Please create or upload galfit config file first')
        else:
            # Update config file
            with open(self.config_file, 'r') as file:
                lines = file.readlines()
            for i, line in enumerate(lines):
                if 'G)' in line:
                    lines[i] = 'G) none\n'
            with open(self.config_file, 'w') as file:
                file.writelines(lines)

    def flags(self) -> None:
        '''
        Prints out flags for sersic model that give information about
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
            print("Please upload or create sersic model first")
        else:
            hdulist = fits.open(self.config_output_file)
            galfitheader = hdulist[2].header
            galfit_flags = galfitheader["FLAGS"].split()
            for flag in galfit_flags:
                print("-",flag_dict[flag])
            print()