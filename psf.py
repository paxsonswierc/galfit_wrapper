# Base class for PSF
from astropy.io import fits
import pyds9
import pyregion
import numpy as np
import math

class PSF():

    def __init__(self, filter, target_file, ouput_dir,
                 target_filename, config_file=None,
                 config_output_file=None, model_file=None):
        self.filter = filter
        self.target_file = target_file
        self.ouput_dir = ouput_dir
        self.target_filename = target_filename
        self.config_file = config_file
        self.config_output_file = config_output_file
        self.model_file = model_file


    def region_to_psf_config(self, regions):
        zpt = 32.5
        hdulist_fits = fits.open(self.target_file)
        header = hdulist_fits[0].header
        ps_x,ps_y = 3600*abs(header["CD1_1"]*header["CD2_2"]-header["CD1_2"]\
                             *header["CD2_1"])**0.5,3600*abs(header["CD1_1"]\
                             *header["CD2_2"]-header["CD1_2"]*header["CD2_1"])\
                                **0.5
        hdulist_fits.close()

        output_fits = self.ouput_dir + self.target_filename + '_psf.fits'
        output_config = self.ouput_dir + self.target_filename + 'psf_config.txt'


        sigma_file = 'none'
        psf_file = 'none'
        psfSampling = 1
        mask_file = 'none'
        constraint_file = 'none'

        # creates top of the galfit file
        fits_line = f"A) {self.target_file[self.target_file.rfind('/')+1:]}\n"
        outputfits_line = f"B) {output_fits}\n"
        sigma_line = f"C) {sigma_file}\n"
        psf_line = f"D) {psf_file}\n"
        psfsample_line = f"E) {psfSampling}\n"
        mask_line = f"F) {mask_file}\n"
        constraints_line = f"G) {constraint_file}\n"
        zpt_line = f"J) {zpt}\n"
        ps_line = f"K) {ps_x} {ps_y}\n"
        otherLines = "O) regular\nP) 0\n\n"

        # parses regions from above
        regions = pyregion.parse(regions)
        imIn = fits.getdata(self.target_file)

        # initializes the components and masks
        component_regions = []
        excluded_regions_mask = np.zeros(imIn.shape)
        small_regions_mask_mag = np.zeros(imIn.shape)
        component_number = 1

        # creates a sky component
        def create_sky_component(component_number, fits_file):
            hdulist = fits.open(fits_file)
            image_data = hdulist[0].data
            sky_level = np.median(image_data)
            hdulist.close()

            component_lines = [
                f"#Component number: {component_number}",
                "0) sky",
                f"1) {sky_level} 1"
            ]
            return '\n'.join(component_lines)
        
        component_regions.append(create_sky_component(component_number,
                                                      self.target_file))
        component_number += 1

         # creates a moffot component
        def create_moffat_component(compenent_number, x, y, a, b, angle,
                                    magnitude):
            component_lines = [
                f"#Component number: {component_number}",
                "0) moffat",
                f"1) {x} {y} 1 1",
                f"3) {magnitude} 1",
                f"4) {max(a, b)} 1",
                "5) 2 1",
                f"9) {b/a} 1",
                f"10) {(angle + 90) % 360} 1"
            ]
            return "\n".join(component_lines)
        
        # if box region is given, then use that to create image region
        #default_box = True
        for region in regions:
            if region.name == 'box':
                #default_box = False
                cx, cy, x, y, _ = region.coord_list
                xmin,xmax,ymin,ymax = int(cx-x/2),int(cx+x/2),int(cy-y/2),\
                                        int(cy+y/2)
                image_reg_line = f"H) {xmin} {xmax} {ymin} {ymax}\n"
                convo_box_line = f"I) {xmax-xmin+1}    {ymax-ymin+1}\n"

         # iterate through other regions (exclude regions to add to mask, circle region to make PSF)
        for region in regions:
            if region.__dict__['exclude']:
                region.__dict__['exclude'] = False
                excluded_regions_mask += pyregion.get_mask([region], imIn)\
                                            .astype(int)
            elif region.name == 'point':
                x, y = region.coord_list
                small_regions_mask_mag = pyregion.get_mask([region], imIn)\
                                            .astype(int)
                sum_pixels = (np.sum(imIn * small_regions_mask_mag)) * 2
                zeropoint = zpt
                magnitude = (-2.5 * math.log10(sum_pixels)) + zeropoint
                component_regions.append(create_moffat_component(\
                    component_number, x, y, 0, magnitude))
                component_number += 1

                # if default_box:
                #     xmin,xmax,ymin,ymax = int(x-r*2),int(x+r*2),int(y-r*2),\
                #         int(y+r*2)
                #     image_reg_line = f"H) {xmin} {xmax} {ymin} {ymax}\n"
                #     convo_box_line = f"I) {xmax-xmin+1}    {ymax-ymin+1}\n" 

        # create mask
        excluded_regions_mask = np.ma.masked_greater(excluded_regions_mask, 0)\
                            .filled(1) 
        
        # writes galfit output file
        with open(output_config, 'w') as h:
            h.write(fits_line) 
            h.write(outputfits_line)
            h.write(sigma_line)
            h.write(psf_line)
            h.write(psfsample_line)
            h.write(mask_line)
            h.write(constraints_line)
            h.write(image_reg_line)
            h.write(convo_box_line)
            h.write(zpt_line)
            h.write(ps_line)
            h.write(otherLines)
            h.write('\n'.join(component_regions))

        return output_config, output_fits


    def write_config(self, d):
        d.set("fits new "+self.target_file)
        d.set("scale mode 99.5")
        d.set("mode region")
        d.set("region shape point")
        input('Place point for star. Hit enter when region is placed\n')
        d.set("region shape box")
        input('Place box for frame. Hit enter when region is placed\n')
        psf_regions = d.get("region")
        output_config, output_fits = self.region_to_psf_config(psf_regions)

    def edit_confit(self, d):
        assert self.config_file is not None

    def alter_config(self, d):
        assert self.config_file is not None

    def optimize_config(self):
        pass

    def visualize(self, d):
        assert self.config_output_file is not None
        d.set("mecube new " + self.config_output_file)

    def set_model(self):
        pass