%module(package="NNPDF") experiments
 %{
#include "../../src/NNPDF/experiments.h"
 %}

%include "std_string.i" 
%include "std_vector.i" 
%import "dataset.i"
%import "pdfset.i"

/* Parse the header file to generate wrappers */
%include "../../src/NNPDF/experiments.h"
