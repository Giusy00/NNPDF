# nnpdfcpp
The main repository with the programs used in the NNPDF fitting framework. 
 
## Project summary and aim

The aim of `nnpdfcpp` is to provide a set of programs used in the NNPDF fitting framework. These programs are linked to the `libnnpdf` library. Each fit is defined by a runcard stored in `config/`. This runcard is shared among programs in order to obtain a fit and much more. Input data is stored in the `data` folder, where users can download theories and check the data layout documentation. The output of all programs is stored in `results/<runcard_filename>/<program_name>`.

This repository provides the following core components:
- filter: reads runcards, apply kinematical cuts and store masks in `results`
- nnfit: perform a single replica fit
- validphys: creates a complete PDF report comparing 2 runcards, showing the fit estimators and plots.

and the extra optional programs:
- chi2check: compute chi2 for each dataset and experiment in the runcards
- fkcheck: prints the FK-PDF convolution output
- gencovmat: prints the covariance matrix and inverse covariance matrix of all datasets and experiments
- kinplot: generate kinematics plots, obsolete user vp2
- mkthpredictions: print theoretical predictions and data
- revolve: evolve PDF set using APFEL setup
- revolvenet: evolve PDF neural network using APFEL setup
- tconvcheck: convolution timing
- fiatlux: generate a T0 set with the photon PDF via `libfiatlux`

and the following scripts:
- postfit.py: completes the fit applying post-selection of replicas and building the LHAPDF grid
- fitmanager.py: uploads and downloads the PDF fits to/from the NNPDF server
- disp_theory.py: display and downloads apfelcomb theories from the server
- fiatlux.py: same as postfit but for the fiatlux output
- `nnfit.*`: several template scripts for the cluster submissions
- postrevolvenet: same as postfit for the output of revolvenet

The repository also includes some tools, based on `libnnpdf` used at some stage sinse 2012 for specific applications, many of then however are obsolete.

### Release and Tag policy

The library is tagged and released when a major and stable status is achieved. 
Tags and releases follows the NNPDF releases. This project requires compatible versions of `libnnpdf` see binary installation for details.

### Code development policy/rules

Developers must never commit code structure modifications to master. The development pattern should follow these rules:
- Open an issue explaining your bug or feature request. If you report a bug, post information to reproduce it.
- The resolution of issues must be performed in a new branch through a pull request.
- If you have already a local version of the code that you would like to merge in the master, open a pull request.
- The pull request must be reviewed by at least 2 core developers.

### Code style

Originally the code of this library was written at the beginning of 2012 so at that time C++11 was not used as default. 
During the last months the library is receiving constant feedback and requests to improve the data types, so a code modernization is in place.

### Continuous integration (CI)

Zahari has a private TravisCI instance used to build binary packages (conda packages) for this project.

### Testing

Testing is actually not implemented in the current repository, however we have an issue for that, see https://github.com/NNPDF/libnnpdf/issues/10 .

## Installation

We provide two installation methods: binary packages and from source.
If do not plan to apport modifications to the library the recommended installation system is through binary packages.

### Binary packages

The master version of `libnnpdf` and its dependencies can be obtained in binary format, as a conda package. A bootstrap script exist to aid the configuration. Simply clone its repository and execute it:
```Shell
git clone git@github.com:NNPDF/binary-bootstrap.git
./binary-botstrap/bootstrap.sh
```
The script will ask for the password of the private NNPDF repositories. It is:
```
BifaSali9
```
Once configured, it is possible to install libnnpdf or apfel by simply:
```Shell
conda install nnpdf validphys2
```

Which will pull also LHAPDF, libnnpdf, apfel and all the other dependencies.

A detailed validphys2 guide including conda installation instructions can be found here:

http://pcteserver.mi.infn.it/~nnpdf/validphys-docs/guide.html

### From source

`nnpdfcpp` depends on the following libraries in order to compile all programs:

- pkg-config
- lhapdf
- gsl
- libarchive
- sqlite
- yaml-cpp
- libnnpdf
- CERN-ROOT (for validphys)
- APFEL
- fiatlux

please ensure to have the dependencies correctly installed and in your PATH before compiling nnpdfcpp.
The exact or minimal version requirements for each package is summarized in https://github.com/NNPDF/nnpdfcpp/blob/master/conda-recipe/meta.yaml.

#### Configurations

Possible configurations:

```Shell
cmake .
make
```

More options are available when running:
```Shell
ccmake .
```
or 
```Shell
cmake-gui .
```

## Documentation

### Runcard

The runcard is written in YAML. The interpretation of the entries should be self-explanatory. The runcard is the unique identifier of a fit, it is also the only required configuration input required for many programs of this repository.

### Performing a fit (simple example)

0. compile the code

1. Create a runcard by taking as template one of the files in `config`.

2. Go to `data` and download the specific theory folder using `disp_theory.py` and passing the `theoryid` of your runcard as theory number.

3. Go to `bin` and
```Shell
./filter <runcard>.yml
```

4. Decide how many NN replicas you wish and then launch in your cluster:
```Shell
./nnfit <replica_number> <runcard>.yml
```
where replica_number goes from 1-n.

5. Wait for the termination of all replicas and then run `postfit.py n <runcard>.yml` if many requires are discarded reduce `n`.

6. At this stage you have your LHAPDF set, you can upload to the server with `fitmanager.py` (so you can download and use it in vp2) or just run `validphys` to see results in a PDF report, the syntax is:
```Shell
./validphys <runcard>.yml <other_fit>.yml
```

### Code documentation

THe code is documented with Doxygen, if you find methods or classes not fully documented open a issue request.

### Layout documentation

For specifications about data please check `data/doc`.
For specifications about the code design see Chapter 3 of http://arxiv.org/pdf/1509.00209.pdf
