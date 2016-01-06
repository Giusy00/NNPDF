%module(package="NNPDF") nnpdfdb
 %{
#include "../../src/NNPDF/exceptions.h"
#include "../../src/NNPDF/nnpdfdb.h"
 %}

%include "std_string.i" 
%include "std_vector.i" 
%include "common.i"

/* Parse the header file to generate wrappers */

%include "include/excepthandler.i"

%include "../../src/NNPDF/nnpdfdb.h"
