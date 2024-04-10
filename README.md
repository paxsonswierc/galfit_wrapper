# Welcome to galfit_wrapper!

## Current dependencies:

### System/Executables:

bash, ds9 able to run through terminal, galfit

### Python libraries:

numpy, astropy, pyds9, pyregion

## Running galfit wrapper

To run download repository and run 
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
Alternatively, you can just delete all text from path_config.txt and galfit wrapper will as your input
again next time you run it.
