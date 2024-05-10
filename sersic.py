# Class for sersic models
# Author: Paxson Swierc & Daniel Babnigg

from astropy.io import fits
import os
from region_to_config import input_to_galfit
from utils import open_textfile
import subprocess
import shutil
import pyregion

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
        produce_config: runs galfit for current config file with -o2 after region property edits
        visualize: opens up sersic model in ds9
        visualize_rgb: opens up target and model rgb images in ds9
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
            print('\nPlease create or upload psf first\n')
        else:
            # Open target in ds9
            d.set("fits new "+self.target_file)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode 99.5")
            d.set("zoom to fit")
            d.set("mode region")
            # Prompt user to place ellipse region for galaxies
            d.set("region shape ellipse")
            input('\nPlace ellipses for galaxies. Hit enter when region is placed')
            # Prompt user to place point region for psf component
            d.set("region shape point")
            input('\nPlace point for point sources. Hit enter when region is placed')
            d.set("region shape box")
            input('\nPlace box for frame. Hit enter when region is placed')
            regions = d.get("region -system image")
            # Establish filenames
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'
            # Set galfit config file
            constraint = 'none'
            # if self.constraint_file is None:
            #     constraint = 'none'
            # else:
            #     constraint = self.constraint_file
            input_to_galfit(self.target_file, False, regions, self.zero_point,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, False, False, False, [0]*4,
                            constraint, [])
            # Get rid of regions
            d.set('region select all')
            d.set('region delete select')
            # Optimize with galfit config
            optimize = input('\nRun galfit for this config? Hit enter for yes, type no otherwise > ')
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
            print('\nPlease create config file first\n')
        else:
            # Open target in ds9
            d.set("fits new "+self.target_file)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode 99.5")
            d.set("zoom to fit")
            d.set("mode region")
            box, mags, psf_mags, sky_info, bending = self.config_to_region(d)
            # Ask for manual edits first
            open_editor = input('\nWould you like to edit the config text file manually? Any removal of components should be done manually. Type yes or hit enter to skip > ')
            if open_editor == 'yes' or open_editor == 'y':
                open_textfile(self.config_file)
                # Load in regions again
                box, mags, psf_mags, sky_info, bending = self.config_to_region(d)

            d.set("region shape ellipse")
            # Constrained changes
            input('\nMake changes to existing regions and add any new regions you may want to constrain. Hit enter to continue')
            # Add constraint based on input
            add_constraint = input('\nUse constraint? Hit enter for yes, type no otherwise > ')
            if add_constraint == 'no':
                self.remove_constraint()
            else:
                if self.constraint_file is not None and os.path.exists(self.constraint_file):
                    use_exist_cst = input('\nReplace current constraint? Hit enter to create new constraint, type no to use existing constraint > ')
                    if use_exist_cst != 'no':
                        self.add_constraint()
                else:
                    self.add_constraint()
            # Give option to add new regions
            input('\nAdd any new regions you do NOT want to constrain. Hit enter to continue')
            # Get regions
            regions = d.get("region -system image")
            # Establish output files
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'
            # Write to galfit config file
            if self.constraint_file is None:
                constraint = 'none'
            else:
                constraint = self.constraint_file
            input_to_galfit(self.target_file, False, regions, self.zero_point,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, box, mags, psf_mags, sky_info,
                            constraint, bending)
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
            print('\nPlease create or upload config file first\n')
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
            # subprocess.run(['/bin/bash', '-c', self.galfit_path+" "+self.config_file])
            subprocess.run(['/bin/bash', '-c', str(self.galfit_path+' '+self.config_file)])
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
                # Prompt next decision to user. Any other input exits loop
                prompt = '''What would you like to do? Enter ->
1: Save this model and config
2: Edit the output config of this model (continue process)
3: Reset from last stage and edit last config
 > '''
                next_step = input(prompt)
                if next_step == '1':
                    # Save the model and config
                    # Replace this config with galfit output config
                    os.remove(self.config_file)
                    shutil.copyfile('galfit.01', self.config_file)
                    os.remove('galfit.01')
                    # save the model
                    output_fits_final = self.ouput_dir + self.target_filename + '_model.fits'
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
                    print('\nCorrupted output. Check for buffer overflow.\nMay have to do with output directory path or target fits file path being too long\n')
                else:
                    print('\nGalfit crashed. Please edit/remake config file and try again\n')

    def produce_config(self, d) -> None:
        '''
        Produces a galfit model based on config file using -o2 flag; no optimization

        Args:
            d: pyds9 DS9 instance
        
        Returns: Nothing
        '''
        if self.config_file is None:
            print('\nPlease create or upload config file first\n')
        else:
            # Open target in ds9
            d.set("fits new "+self.target_file)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode 99.5")
            d.set("zoom to fit")
            d.set("mode region")
            _ = self.config_to_region(d)
            
            print('\nDO NOT edit/delete/add regions except for chaning source/background properties')
            input('\nChange regions\' properties to background to not include in model. Hit enter to continue')
            regions = d.get("region -system image")

            # Establish output files
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            
            regions = pyregion.parse(regions)
            reg_list = []
            inc_list = []
            for region in regions:
                if "background" in region.__dict__["attr"][0]:
                    reg_list.append(str(region.__dict__["attr"][1]["text"]))
                    inc_list.append(0)
                else:
                    reg_list.append(str(region.__dict__["attr"][1]["text"]))                    
                    inc_list.append(1)

            with open(self.config_file, 'r') as config:
                lines = config.readlines()
                temp_lines = []
                in_comp = False
                for i, line in enumerate(lines):
                    if 'Component number:' in line and 'sky' not in lines[i+1]:
                        comp_num = str(int(line.split()[3]))
                        in_comp = True
                    if in_comp and 'Z)' in line:
                        temp_lines.append(f"Z) {inc_list[reg_list.index(comp_num)]}")
                        in_comp = False
                    else:
                        temp_lines.append(line)

            # Write update to config file
            with open(self.ouput_dir + 'config_temp.txt', 'w') as file:
                file.writelines(temp_lines)

            # Run galfit
            subprocess.run(['/bin/bash', '-c', str(self.galfit_path+' '+self.ouput_dir+'config_temp.txt'+' -o2')])
            os.remove(self.ouput_dir+'config_temp.txt')
            print('\nFitting finished')
            # Check if galfit was successful
            if os.path.exists(output_fits):
                print("\ngalfit run done, loading into DS9...\n")
                print("produced mutli-frame fits model saved in "+str(self.ouput_dir + self.target_filename + '_model_prod.fits'))
                print()
                # Open output in ds9
                d.set("mecube new " + output_fits)
                d.set("tile no")
                d.set("cmap 1 0.5")
                d.set("scale mode minmax")
                d.set("mode none")
                d.set("zoom to fit")
                d.set("cube play")

                # Save the model and config
                output_fits_final = self.ouput_dir + self.target_filename + '_model_prod.fits'
                os.rename(output_fits, output_fits_final)
            else:
                if os.path.exists(output_fits):
                    print('\nCorrupted output. Check for buffer overflow.\nMay have to do with output directory path or target fits file path being too long\n')
                else:
                    print('\nGalfit crashed. Please edit/remake config file and try again\n')



    def visualize(self, d) -> None:
        '''
        Visualizes sersic model using ds9

        Args: 
            d: pyds9 DS9 instance

        Returns: Nothing
        '''
        if self.config_output_file is None:
            print('\nPlease upload or create sersic model first\n')
        else:
            d.set("mecube new "+ self.config_output_file)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode minmax")
            d.set("mode none")
            d.set("zoom to fit")
            d.set("cube play")

    def visualize_regions(self, d) -> None:
        '''
        Visualizes regions of model using ds9

        Args: 
            d: pyds9 DS9 instance

        Returns: Nothing
        '''
        if self.config_file is None:
            print('\nPlease create or upload config file first\n')
        else:
            # Open target in ds9
            d.set("fits new "+self.target_file)
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("scale mode 99.5")
            d.set("zoom to fit")
            d.set("mode pan")
            box, mags, psf_mags, sky_info, bending = self.config_to_region(d)

    def visualize_rgb(self, rfile: str, gfile: str, bfile: str, single: bool, d) -> None:
        '''
        Prompts user to upload 3 multi-band model files to create DS9 r,g,b comparison

        Args:
            rfile: "red" filter multi-band output file
            gfile: "green" filter multi-band output file
            bfile: "blue" filter multi-band output file

        Returns: Nothing
        '''
        if single:
            d.set("tile no")
            d.set("cmap 1 0.5")
            d.set("rgb")
            d.set("rgb lock scale no")
            d.set("rgb lock colorbar no")
            d.set("rgb lock scalelimits yes")
            d.set("rgb red")
            d.set("scale linear")
            d.set("scale mode 99.5")
            d.set(f"fits {rfile}")
            rscale = d.get("scale limits")
            d.set("rgb green")
            d.set("scale linear")
            d.set("scale mode 99.5")
            d.set(f"fits {gfile}")
            gscale = d.get("scale limits")
            d.set("rgb blue")
            d.set("scale linear")
            d.set("scale mode 99.5")
            d.set(f"fits {bfile}")
            bscale = d.get("scale limits")
            d.set("rgb lock scale yes")
            d.set("rgb lock colorbar yes")
            d.set("zoom to fit")

            if len(open(self.ouput_dir + 'rgb_info.txt', 'r').read().splitlines()) == 3:
                with open(self.ouput_dir + 'rgb_info.txt', 'a') as rgb_info:
                    rgb_info.write(str(rscale)+'\n')
                    rgb_info.write(str(gscale)+'\n')
                    rgb_info.write(str(bscale)+'\n')
        else:
            rscale, gscale, bscale = open(self.ouput_dir + 'rgb_info.txt', 'r').read().splitlines()[3:6]

            hdu_r = fits.open(rfile)
            hdu_g = fits.open(gfile)
            hdu_b = fits.open(bfile)

            if len(hdu_r) == 4 and len(hdu_g) == 4 and len(hdu_b) == 4:
                d.set("frame delete all")
                d.set("tile yes")
                d.set("rgb")
                d.set("rgb lock scale no")
                d.set("rgb lock colorbar no")
                d.set("rgb lock scalelimits yes")
                d.set("rgb red")
                d.set("scale linear")
                d.set("scale mode 99.5")
                d.set(f"mecube {rfile}")
                d.set(f"cube 2")
                d.set("scale limits "+rscale)
                d.set("rgb green")
                d.set("scale linear")
                d.set("scale mode 99.5")
                d.set(f"mecube {gfile}")
                d.set(f"cube 2")
                d.set("scale limits "+gscale)
                d.set("rgb blue")
                d.set("scale linear")
                d.set("scale mode 99.5")
                d.set(f"mecube {bfile}")
                d.set(f"cube 2")
                d.set("scale limits "+bscale)
                d.set("rgb lock scale yes")
                d.set("rgb lock colorbar yes")

                d.set("rgb")
                d.set("rgb lock scale no")
                d.set("rgb lock colorbar no")
                d.set("rgb lock scalelimits yes")
                d.set("rgb red")
                d.set("scale linear")
                d.set("scale mode 99.5")
                d.set(f"mecube {rfile}")
                d.set(f"cube 3")
                d.set("scale limits "+rscale)
                d.set("rgb green")
                d.set("scale linear")
                d.set("scale mode 99.5")
                d.set(f"mecube {gfile}")
                d.set(f"cube 3")
                d.set("scale limits "+gscale)
                d.set("rgb blue")
                d.set("scale linear")
                d.set("scale mode 99.5")
                d.set(f"mecube {bfile}")
                d.set(f"cube 3")
                d.set("scale limits "+bscale)
                d.set("rgb lock scale yes")
                d.set("rgb lock colorbar yes")
                d.set("zoom to fit")
                d.set("frame prev")
                d.set("zoom to fit")
            else:
                with open(self.ouput_dir + 'rgb_info.txt') as info_:
                    lines = info_.readlines()
                with open(self.ouput_dir + 'rgb_info.txt', 'w') as info:
                    info.writelines(lines[:6])
                print("\nUploads must be galfit output multi-band FITS files!\n")



    def upload_config(self, file: str, d) -> None:
        '''
        Prompts user to upload config file and copies it to output dir

        Args:
            file: path to upload file

        Returns: Nothing
        '''
        if self.psf.model_file is None:
            print('\nPlease create or upload psf first\n')
        else:
            # Update config filename
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            if file != self.config_file:
                shutil.copyfile(file, self.config_file)
            # Convert config to regions to get info on box size
            box, mags, psf_mags, sky_info, bending = self.config_to_region(d)

            regions = d.get("region -system image")
            # Establish filenames
            self.config_file = self.ouput_dir + self.target_filename + '_config.txt'
            output_fits = self.ouput_dir + self.target_filename + '_model_temp.fits'
            output_mask = self.ouput_dir + self.target_filename + '_mask.fits'
            # Write new galfit config (to update filenames in the uploaded)
            if self.constraint_file is None:
                constraint = 'none'
            else:
                constraint = self.constraint_file
            input_to_galfit(self.target_file, False, regions, self.zero_point,
                            self.config_file, output_fits, output_mask,
                            self.psf.model_file, box, mags, psf_mags, sky_info,
                            constraint, bending)

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
        d.set("tile no")
        d.set("cmap 1 0.5")
        d.set("scale mode 99.5")
        d.set("zoom to fit")
        # Keep track of magnitudes of all components
        magnitudes = []
        psf_magnitudes = []
        bending = []
        sky_info = [0, 0, 0, 0]
        config = open(self.config_file, 'r')
        lines = config.readlines()

        # create temporary region file to write region files out to
        reg_f = open(self.ouput_dir + "temp_reg.reg", "w")

        for i, line in enumerate(lines):
            # Check for sersic component
            if 'sersic' in line and 'sersic,' not in line:
                if "# Component number:" in lines[i-1]:
                    number = lines[i-1].split()[3]
                else:
                    number = ""
                bend = False
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
                    elif 'B2)' in component_line:
                        bend = component_line
                    if '0)' in component_line or component_line == lines[-1]:
                        # Set ellipse region
                        reg_f.write(f"ellipse {x} {y} {a} {b} {angle} # text={{{number}}} color=#f82")
                        reg_f.write("\n")
                        if bend:
                            bending.append(bend)
                        else:
                            bending.append(None)
                        break
            # Check for psf component
            if '0) psf' in line:
                if "# Component number:" in lines[i-1]:
                    number = lines[i-1].split()[3]
                else:
                    number = ""
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
                        reg_f.write(f"point {x} {y} # text={{{number}}} color=#93f")
                        reg_f.write("\n")
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

        # open regions, then delete temporary region file
        reg_f.close()
        d.set("region "+self.ouput_dir+"temp_reg.reg -system image")
        os.remove(self.ouput_dir+"temp_reg.reg") 

        config.close()
        return [x_min, x_max, y_min, y_max, x_center, y_center],\
                magnitudes, psf_magnitudes, sky_info, bending
    
    def add_constraint(self) -> None:
        '''
        Creates constraint file for galfit config and adds it to config file

        Args: None

        Returns: Nothing
        '''
        if self.config_file is None:
                print('\nPlease create or upload galfit config file first\n')
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
            with open(self.constraint_file, 'w') as h:
                h.write("\n".join(constraint_lines))

    def remove_constraint(self) -> None:
        '''
        Removes constraint file

        Args: None

        Returns: Nothing
        '''
        if self.constraint_file is not None:

            if os.path.exists(self.constraint_file):
                os.remove(self.constraint_file)
            self.constraint_file = None

        if self.config_file is None:
            print('\nPlease create or upload galfit config file first\n')
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
            print("\nPlease upload or create sersic model first\n")
        else:
            hdulist = fits.open(self.config_output_file)
            galfitheader = hdulist[2].header
            galfit_flags = galfitheader["FLAGS"].split()
            print()
            for flag in galfit_flags:
                print("-",flag_dict[flag])
            print()