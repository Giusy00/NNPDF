%module(package="NNPDF") parametrisation
 %{
#include "../../src/NNPDF/exceptions.h"
#include "../../src/NNPDF/parametrisation.h"
 %}

%include "std_string.i" 
%include "std_vector.i" 
%include "common.i"

/* Parse the header file to generate wrappers */

%feature("autodoc", "3");

%include "include/excepthandler.i"

%include "../../src/NNPDF/parametrisation.h"
