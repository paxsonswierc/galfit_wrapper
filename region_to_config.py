# Function to convert a ds9 region to a config file
# Author: Daniel Babnigg

import pyregion
from astropy.io import fits
import numpy as np
import math

# function for fits file and regions -> galfit file, for both psf and normal galfit
def input_to_galfit(fits_file, psf, regions, zpt, output_file, output_fits,
                    mask_file, psf_file, pre_box, pre_mags, pre_psf_mags,
                    sky_info, constraint_file):
    # creates lines for sky component
    def create_sky_component(component_number, fits_data, sky_info):
        if sky_info[3] == 0:
            sky_level = np.median(fits_data)
        else:
            sky_level = sky_info[3]

        component_lines = [
            f"# Component number: {component_number}",
            "0) sky",
            f"1) {sky_level} 1",
            f"2) {sky_info[0]} {sky_info[2]}",
            f"3) {sky_info[1]} {sky_info[2]}",
            "Z) 0",
            "\n"
        ]
        return '\n'.join(component_lines)

    # creates lines for psf component
    def create_psf_component(component_number, x, y, magnitude, skip):
        component_lines = [
            f"# Component number: {component_number}", 
            "0) psf", 
            f"1) {x} {y} 1 1", 
            f"3) {magnitude} 1",
            f"Z) {skip}",
            "\n"
        ]
        return '\n'.join(component_lines)
    
    # creates lines for moffat component
    def create_moffat_component(compenent_number, x, y, a, b, angle, magnitude, skip):
        component_lines = [
            f"# Component number: {component_number}",
            "0) moffat",
            f"1) {x} {y} 1 1",
            f"3) {magnitude} 1",
            f"4) {max(a, b)} 1",
            "5) 3 1",
            f"9) {b/a} 1",
            f"10) {(angle + 90) % 360} 1",
            f"Z) {skip}",
            "\n"
        ]
        return "\n".join(component_lines)
    
    # creates lines for sersic component
    def create_sersic_component(component_number, x, y, a, b, angle, magnitude, skip):
        component_lines = [ 
            f"# Component number: {component_number}",
            "0) sersic",
            f"1) {x} {y} 1 1",
            f"3) {magnitude} 1",
            f"4) {a} 1",
            "5) 2 1",
            f"9) {b/a} 1",
            f"10) {(angle + 90) % 360} 1",
            f"Z) {skip}",
            "\n"
        ]
        return "\n".join(component_lines)
    


    # define names of files, then create lines
    sigma_file = 'none'
    psfSampling = 1

    file_lines = [
        f"A) {fits_file}",
        f"B) {output_fits}",
        f"C) {sigma_file}",
        f"D) {psf_file}",
        f"E) {psfSampling}",
        f"F) {mask_file}",
        f"G) {constraint_file}",
        ""
    ]



    # gets data and header from input FITS file
    hdulist_fits = fits.open(fits_file)
    fits_data = hdulist_fits[0].data
    header = hdulist_fits[0].header
    hdulist_fits.close()

    ps_x,ps_y = 3600*abs(header["CD1_1"]*header["CD2_2"]-header["CD1_2"]*header["CD2_1"])**0.5,3600*abs(header["CD1_1"]*header["CD2_2"]-header["CD1_2"]*header["CD2_1"])**0.5
    if pre_box:
        info_lines = [
            f"H) {pre_box[0]} {pre_box[1]} {pre_box[2]} {pre_box[3]}",
            f"I) {pre_box[4]} {pre_box[5]}",
            f"J) {zpt}",
            f"K) {ps_x} {ps_y}",
            "O) regular",
            "P) 0",
            "\n"
        ]

    # initializes the components and masks
    component_regions = []
    excluded_regions_mask = np.zeros(fits_data.shape)
    small_regions_mask_mag = np.zeros(fits_data.shape)
    component_number = 1

    # parses regions from above
    regions = pyregion.parse(regions)



    # creates sky component
    component_regions.append(create_sky_component(component_number, fits_data, sky_info))
    component_number += 1

    sersic_count = 0
    psf_count = 0
    for region in regions:
        if region.__dict__['exclude']:
            region.__dict__['exclude'] = False
            excluded_regions_mask += pyregion.get_mask([region], fits_data).astype(int)
        elif region.name == 'box':
            cx, cy, x, y, _ = region.coord_list
            xmin,xmax,ymin,ymax = int(np.round(cx-x/2)),int(np.round(cx+x/2)),int(np.round(cy-y/2)),int(np.round(cy+y/2))
            ps_x,ps_y = 3600*abs(header["CD1_1"]*header["CD2_2"]-header["CD1_2"]*header["CD2_1"])**0.5,3600*abs(header["CD1_1"]*header["CD2_2"]-header["CD1_2"]*header["CD2_1"])**0.5
            info_lines = [
                f"H) {xmin} {xmax} {ymin} {ymax}",
                f"I) {xmax-xmin+1} {ymax-ymin+1}",
                f"J) {zpt}",
                f"K) {ps_x} {ps_y}",
                "O) regular",
                "P) 0",
                "\n"
            ]
        elif region.name == 'point':
            x, y = region.coord_list
            if "background" in region.__dict__["attr"][0]:
                skip = 1
            else:
                skip = 0
            if pre_psf_mags and (psf_count+1) <= len(pre_psf_mags):
                magnitude = pre_psf_mags[psf_count]
                psf_count += 1
            else:
                magnitude = zpt - 10
            component_regions.append(create_psf_component(component_number, x, y, magnitude, skip))
            component_number += 1
        elif region.name == 'ellipse':
            x, y, a, b, angle = region.coord_list
            if "background" in region.__dict__["attr"][0]:
                skip = 1
            else:
                skip = 0
            if b > a:
                if angle >= 270:
                    angle -= 90
                else:
                    angle += 90
                a,b = b,a
            if b == 0:
                b = 1
            if a == 0:
                a = 1
            small_regions_mask_mag = pyregion.get_mask([region], fits_data).astype(int)
            sum_pixels = (np.sum(fits_data * small_regions_mask_mag)) * 2
            zeropoint = zpt
            if pre_mags and (sersic_count+1) <= len(pre_mags):
                magnitude = pre_mags[sersic_count]
                sersic_count += 1
            else:
                magnitude = (-2.5 * math.log10(sum_pixels)) + zeropoint
            component_regions.append(create_sersic_component(component_number, x, y, a, b, angle, magnitude, skip))
            component_number += 1 
        elif region.name == 'circle':
            x, y, r = region.coord_list
            if "background" in region.__dict__["attr"][0]:
                skip = 1
            else:
                skip = 0
            small_regions_mask_mag = pyregion.get_mask([region], fits_data).astype(int)
            sum_pixels = (np.sum(fits_data * small_regions_mask_mag)) * 2
            zeropoint = zpt
            magnitude = (-2.5 * math.log10(sum_pixels)) + zeropoint
            component_regions.append(create_moffat_component(component_number, x, y, r, r, 0, magnitude, skip))
            component_number += 1
        else:
            print(region,"will be ignored")

    # create mask and mask file
    excluded_regions_mask = np.ma.masked_greater(excluded_regions_mask,0).filled(1)
    fits.PrimaryHDU(excluded_regions_mask).writeto(mask_file, overwrite=True)

    # writes galfit output file
    with open(output_file, 'w') as h:
        h.write("\n".join(file_lines)) 
        h.write("\n".join(info_lines))
        h.write('\n'.join(component_regions))