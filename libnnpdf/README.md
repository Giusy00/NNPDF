libnnpdf 1.1.1
----------------------------

Libary for core NNPDF utilities.

Possible configurations:
```Shell
cmake .
```
or (recommended):
```Shell
mkdir build
cd build
cmake ..
```
You can control the optional flags with ccmake or from cmd line, the most relevant flags are:
```Shell
CMAKE_INSTALL_PREFIX
ENABLE_OPENMP
ENABLE_OPENMPI
ENABLE_PYWRAP
```

On the command line, options are controlled appending a `-D` flag. For
example:

```
cmake .. -DENABLE_PYWRAP=on
```

To compile the Python wrappers, set ENABLE_PYWRAP=ON as above, and
after libnnpdf is installed, then compile with:
```Shell
make wrapper
make wrapper-clean
```
This will also install the wrapper in the current Python environment.
