<h1>USE DEMONSTRATION</h1>

This example will use object **CJ0408** and its [g](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/CJ0408_g.fits), [r](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/CJ0408_r.fits), and [z](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/CJ0408_z.fits) bands from DECaLS. The images below are from using WSL on MobaXterm on a Windows OS, but majority of steps are identical to other operating systems and terminals.

<h3>PREPARING WRAPPER AND FILES</h3>

![clone repository](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/1clone_repo.png)

The first step is to clone the repository. Use `cd` to navigate to a directory that makes sense to you to store the code. Once in the directory, run `https://github.com/paxsonswierc/galfit_wrapper.git` then `cd` into the created directory. There will be a lot of files, but the relevant one is *galfit_wrapper.py* which contains the source code and is what you will run.

At this point, it would make sense to download required libraries/programs. Downloading everything is required for a successful run with the galfit wrapper.

![first run](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/2first_run.png)

The very first time you run the wrapper, it will require you to input a path to the *galfit* binary file. Have the full directory noted before running the wrapper for the first time.

The wrapper requires to have a prepared one-band .fits image prepared. There are multiple data cleaning methods and steps depending on the file you have. This can include, but is not limited to: converting counts/sec to counts for pixel values, adding *EXPTIME*, *GAIN*, and other FITS header numbers to default values, matching image and physical coordinates, matching pixels with WCS between different bands, etc. The example files at the top are pre-processed with these data cleaning steps already implemented.

Once you have downloaded required libraries/programs and cloned the code directory, you can run the code. `cd` to the directory containing *galfit_wrapper.py*, and use `conda activate <name>` if you created a conda enviornment. To run the wrapper code, simply type `python3 galfit_wrapper.py` which will then prompt a full path to the *galfit* executable binary file (be sure to input full directory, without shortcuts like \~) Next, you will need to pick the target file - simply navigate to the file you processed in the opened file navigator, then hit Open. Once you upload the file, it will immediately create a new directory with the same name as the input .fits file in the created *\~/gf_out* directory, and it will copy the target .fits file in this named directory. Note that any changes to the target file should be made in this new directory. It will also ask for a zeropoint, which may have been calculated in the data processing step; however, it can be changed at any time if a better value is calculated.

![init wrapper](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/3initiating_wrapper.png)

To speed things up, you can input the file directory directly while running the wrapper: `python3 galfit_wrapper.py <dir/to/target.fits>` It makes sense to use the *\~/gf_out/...* directory after successive runs, but FITS files with the same name will cause the wrapper to run in the same *\~/gf_out/* location.

![upload other bands](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/4upload_others.png)

If you are working with a multiple bands, it can be convenient to set up the other directories by uploading the pre-processed images of the other bands, along with their zeropoints. If using multiple bands, you should start with the file with the best signal to noise and detection of what you're looking for - this is the r-band for lensed objects in DECaLS.

![target visualize](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/5target_visualize.png)

Run the galfit wrapper with a chosen file, and run `target visualize` to view the uploaded target .fits file. This will open an instance of DS9, and it can be convenient to organize your screen to split-screen to see the DS9 image along with the wrapper.

![start tv rgb](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/6tvrgb_input.png)

With multiple bands, it can be convenient to view the image in RGB. To do this, run `target visualize rgb` and upload the target .fits files in red, green, blue order. It would make sense to upload files from the *\~/gf_out/* directory, so changes to original files are propagated when visualizing.

![tv rgb](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/7tv_rgb.png)

After the three red, green, blue files are uploaded, it will open the files into an RGB frame in DS9.

<h3>PSF CREATION</h3>

![psf create](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/8psf_create.png)

When done visualizing the target, you can create a psf (point spread function) that will be eventually used in the galfit run. To do this, run `psf create` which will open the target in DS9, and ask for both a circle for a star and a box for a frame. If using multiple bands, you should use the same source, which means finding a bright, isolated, circular star that is bright in all filters. The circle will create a moffat profile in galfit, and the box will be the region where the optimization is performed.

![psf output](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/9psf_final.png)

After the circle and box are created, galfit will run and optimize with these parameters. If the optimization does not crash, it will open and blink between the 4-band output file in DS9. The bands are as follows: blank, target, model, residual. In this case, I am happy the the residual as the PSF was subtracted nicely from the center, but am worried about the source in the bottom left messing with the fit. I will type `no` to redo the PSF creation.

![exclude region](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/10psf_exclude.png)

Using the same steps as above, I place a circle for a moffat profile on a bright star, and a large bounding box. I chose to mask out the aforementioned nearby source, which can be done by creating any shaped region with an *exclude* property, which can be placed at any time while placing other regions. This will create a *psf_mask.fits* file which will be updated with different runs - note if no exclude regions are created, then the mask file is empty. I run this model in the same way as previously, and this time hit `enter` to indicate I am happy with the produced residual.

![psf outputs](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/11psf_outputs.png)

To see what has been done, you can run `target list` which lists some of the files in the directory. Here, we have an original target file, a psf galfit config file, and a psf galfit 4-band model file. Additionally, galfit prints out some flags while running - if you would like to retrieve these flags at any point of the most recent psf model file, use `psf flags` which will print everything out. Finally, if you wish to see the 4-band model file in DS9, you can use `psf visualize` - note these commands can be run at any time, after a PSF model is created.

<h3>MODEL CREATION</h3>

![scc](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/12create_config.png)

To create the actual model of the target, you follow steps very similar to the PSF creation. Run `sersic create config` to start creation of a model. Place ellipses for galaxies, which are inputted as sersic components in galfit, points for point sources, and a box for the bounding area on where to optimize. Once this is done, you can hit `enter` to run galfit - at this step, you can also make manual edits or additions to the created galfit file.

![out to 3](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/13config_3.png)

Once galfit runs, similar to PSF creation, it will display the 4-band model file in DS9. It allows you to do 3 things - either save the model and config if you're happy with the model, edit the config starting at the output of this model, or start from the regions you placed before running the galfit optimization. With this specific model, I see some patterns in residuals, and do not trust the optimization that took place - for this reason, I will enter `3` to start at the regions I created at the beginning of the config creation.

![3 edit](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/14config_3_edit.png)

Edit config steps

![out to 2](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/15config_2.png)

Happy with optimization, but want to add something, do 2

![2 edit](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/16config_2_edit.png)

Edit config steps

![out to 1](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/17config_1.png)

Happy with final model, save 1

![config outputs](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/18after_config.png)

Visualize model, view flags

![one band done](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/19oneband_done.png)

Finished with one band - add constraint to be used for other bands, list all files created, use quit

<h3>MULTI-BAND PROPAGATION</h3>

![psf 2 with background](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/20newband_psf.png)

introudce background source = do not include in model (note psf has to be created manually, and aliases!)

![psf ran, upload config](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/21upload_config.png)

upload config after psf run

![upload constraint](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/22upload_constraint.png)

regions are visualized, upload constraint

![new after opt](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/23newband_afteroptimization.png)

can simply run optimize to not edit regions, but just use constraint and config to otpimize; target list, and view flags

![other band after opt](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/24otherband_afteroptimization_2.png)

for the other band, it didn't work as well - so i chose to edit the output

![editing with constraint](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/25edit_with_cst.png)

i add psf component, and i want to use a constraint, but not overwrite the existing on i uploaded

![other band after edit](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/26otherband_better.png)

this one isn't perfect still, but much better- saved for visualization sake

![sv rgb](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/27sersic_visualize_rgb.png)

after red,green,blue bands' models are created, can use `sersic visualize rgb` to view the rgb target and model side by side, and the rgb_info file can be copied and pasted

![sersic produce](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/28sersic_prod.png)

if want to not optimize, but just run a given galfit file - has option to background sources

![sersic produce output](https://github.com/paxsonswierc/galfit_wrapper/blob/fbe8c042a48e782fa515815ec184c7e5e2f58468/example/pictures/29sersic_prod_output.png)

after output is produced

