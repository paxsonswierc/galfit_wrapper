<h1>GETTING STARTED</h1>

how to clone, install, and run galfit_wrapper



<h3>REQUIRED PACKAGES</h3>

[![Python version](https://img.shields.io/badge/Python-3.10-green.svg?style=flat)](https://www.python.org/downloads/release/python-3100/)

**System/Executables:**
 * [ds9](https://sites.google.com/cfa.harvard.edu/saoimageds9/download)
 * [galfit](https://users.obs.carnegiescience.edu/peng/work/galfit/galfit.html)
 * bash (for Unix)
 * [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
 * [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) (for Windows)
 * [MobaXterm](https://mobaxterm.mobatek.net/) (optional; for Windows)
 * [anaconda](https://docs.anaconda.com/free/anaconda/install/) (optional)

**Python libraries:** 
 * [numpy](https://numpy.org/install/)
 * [astropy](https://www.astropy.org/)
 * [pyds9](https://github.com/ericmandel/pyds9)
 * [pyregion](https://github.com/astropy/pyregion)

<h3>INSTALLATION</h3>

in terminal (in MobaXterm for Windows), navigate using `cd` to convenient directory

clone repository: `git clone https://github.com/paxsonswierc/galfit_wrapper.git`  
to update repository: `git pull` in code directory

if using Anaconda, first do `conda create -n "<name>" python=3.10.0` then `conda activate <name>`  
download all required python libraries while in the conda enviornment

<h3>FIRST RUN</h3>

to run, always `cd` to directory containing code, and `conda activate <name>` if using Anaconda

to start wrapper, run  
`python3 galfit_wrapper.py`  
which will prompt an input for the target .fits file

alternatively, run  
`python3 galfit_wrapper.py path/to/file.fits`  
with the target .fits file to save time

the first time running will prompt for a galfit execuatble path. this should be a `\path\to\galfit` that will run the galfit executable. if you wish to change the path, you can delete `path_config.txt` in the code directory which will allow you to re-enter the galfit executable path in the next run.

all output files will be saved to a directory called `gf_out`, located in your user home (`~`) directory.  
for example, on mac this will be `\Users\<username>\gf_out\`  
on Windows with WSL, this will be `\home\<username>\gf_out\`
