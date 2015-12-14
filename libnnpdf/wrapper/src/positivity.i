%module(package="NNPDF") positivity
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

#include "../../src/NNPDF/positivity.h"
 %}

%include "std_string.i" 
%include "std_vector.i" 

%include "commondata.i"
%include "fastkernel.i"
%include "common.i"

/* Parse the header file to generate wrappers */
%include "../../src/NNPDF/positivity.h"
