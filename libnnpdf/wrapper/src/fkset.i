%module(package="NNPDF") fkset
 %{
#include <iostream>
#include <fstream>
#include <iomanip>
#include <vector>
#include <string>
#include <cstdlib>
#include <sstream>
#include <cmath>
#include <sys/stat.h>
#include <stdio.h>
#include <gsl/gsl_math.h>
#include <gsl/gsl_eigen.h>

#include "../../src/NNPDF/fkset.h"
 %}

%include "std_string.i" 
%include "std_vector.i" 

/* Parse the header file to generate wrappers */

%import "fastkernel.i"
%include "fkgenerator.i"
%include "../../src/NNPDF/fkset.h"
