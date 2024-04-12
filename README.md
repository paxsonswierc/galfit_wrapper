# Welcome to galfit_wrapper!

![Python version](https://img.shields.io/badge/Python-3.10-green.svg?style=flat)

## Current dependencies:

System/Executables: 
 * bash
 * [ds9](https://sites.google.com/cfa.harvard.edu/saoimageds9/download) (able to run through terminal)
 * [galfit](https://users.obs.carnegiescience.edu/peng/work/galfit/galfit.html)

Python libraries: 
 * [numpy](https://numpy.org/install/)
 * [astropy](https://www.astropy.org/)
 * [pyds9](https://github.com/ericmandel/pyds9)
 * [pyregion](https://github.com/astropy/pyregion)
 * [sep](https://github.com/kbarbary/sep)

## Running galfit wrapper

Download code into directory of your choice. cd into the directory and run the following. Note that currently,
you must run `galfit_wrapper.py` from inside the directory containing the code or it may break.
```
$ python3 galfit_wrapper.py
```
This will open up prompt to input a target fits file to start working on

Alternatively, you can give the target fits file path as a command line argument
```
$ python3 galfit_wrapper.py path/to/file.fits
```
Note, the first time you run the program it will ask you to input a path to your galfit executable
and to an output directory. The output directory is where all output models/config files will be saved.
If you ever want to change these or you input them wrong, you can edit the two paths in path_config.txt
Alternatively, you can just delete all text from `path_config.txt` and galfit wrapper will as your input
again next time you run it.

For a list of commands, type help into tui

## NOTE ON OUTPUT DIRECTORY AND TARGET FILE LOCATION

Galfit has a bug where input filenames that are too long will stop it from running correctly. To avoid this,
please place your output directory and the target fits files you will be working with as close to your home directory
as possible. We are working on a fix for this, but please use the previous temporary solution for now.

## Missing features in developement

* Automatic constraint file generation
* In terminal text editing option for config files
* Better multi band support (rgb images, automatic propogation between bands, etc.)

### Feel free to log any crashes or bugs in issues! Reach out to authors for help at emails pswierc@uchicago.edu or babnigg@uchicago.edu, or on slack as Paxson or Daniel B
