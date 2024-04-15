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

After running galfit_wrapper, all output files will be saved to a directory called `gf_out`, located
in your user home directory. For example, on mac this will be `\Users\username\gf_out\`

Note, the first time you run the program it will ask you to input a path to your galfit executable.
If you ever want to change this or you input it wrong, you can edit the path in `path_config.txt`
Alternatively, you can just delete `path_config.txt` and galfit wrapper will ask your input
again next time you run it.

For a list of commands, type help into tui

## Missing features in developement

* Automatic pixel constraint file generation for all models
* In terminal text editing option for config files
* Better multi band support (rgb images, automatic propogation between bands, etc.)

### Feel free to log any crashes or bugs in issues! Reach out to authors for help at emails pswierc@uchicago.edu or babnigg@uchicago.edu, or on slack as Paxson or Daniel B
