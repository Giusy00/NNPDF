%module(package="NNPDF") dataset
 %{
#define SWIG_FILE_WITH_INIT
#include "NNPDF/exceptions.h"
#include "NNPDF/dataset.h"
 %}

%include "std_string.i" 
%include "std_vector.i" 

%include "include/numpy.i"

%init %{
    import_array();
%}

%import "commondata.i"
%import "fkset.i"
%import "pdfset.i"
%import "utils.i"
/* Parse the header file to generate wrappers */

%feature("autodoc", "3");

%include "include/excepthandler.i"

%template(vector_int) std::vector<int>;

/* We copy the arrays for every reason. It's too dangerous to pass by
 * reference with too little benefict. */
%apply (double** ARGOUTVIEWM_ARRAY2, int* DIM1, int* DIM2) {(double** datamat, int* n, int* m)}

%ignore NNPDF::swap;
%ignore NNPDF::DataSet::operator=;
%ignore NNPDF::DataSet::DataSet(DataSet &&);
%include "NNPDF/dataset.h"

%feature("docstring") NNPDF::DataSet::get_covmat
"Return a copy of the experiment covariance matrix."
%feature("docstring") NNPDF::DataSet::get_cv
"Return a copy of the central values for the experiment."

%extend NNPDF::DataSet{

void get_covmat(double ** datamat, int* n, int* m){
    int len = $self->GetNData();
    auto data = $self->GetCovMat().data();
    auto size = len*len;
    auto result = (double*) malloc(sizeof(double)*size);
    std::copy(data, data + size, result);
    *datamat = result;
    *m = *n = len;
}


void get_sqrtcovmat(double ** datamat, int* n, int* m){
    int len = $self->GetNData();
    auto data = $self->GetSqrtCov().data();
    auto size = len*len;
    auto result = (double*) malloc(sizeof(double)*size);
    std::copy(data, data + size, result);
    *datamat = result;
    *m = *n = len;
}



%pythoncode{

def __len__(self):
    return self.GetNData();

}

}
