// $Id
//
// NNPDF++ 2012-2015
//
// Authors: Nathan Hartland,  n.p.hartland@vu.nl
//          Stefano Carrazza, stefano.carrazza@mi.infn.it

#pragma once

#include "common.h"
#include "experiments.h"
#include "dataset.h"

namespace NNPDF{
  matrix<double> ComputeCovMat_basic(int const nDat,
                                     int const nSys,
                                     std::vector<double> const& sqrt_weights,
                                     std::vector<double> const& central_values,
                                     std::vector<double> const& stat_error,
                                     sysError** const systematic_errors,
                                     bool const mult_errors,         // account for multiplicative uncertainties in building the CovMat
                                     bool const use_theory_errors,   // account for MC uncertainties in building the CovMat
                                     bool const th_cov_matrix,       // account for theoretical uncertainties in building the CovMat
                                     std::string filename,
                                     std::vector<int> bmask);

  matrix<double> ComputeCovMat(CommonData const& cd, std::vector<double> const& t0,
                               const bool th_cov_matrix = false, 
                               std::string filename = "",
                               std::vector<int> bmask = {},
                               double weight=1.);
  matrix<double> ComputeSqrtMat(matrix<double> const& inmatrix);
  matrix<double> read_theory_covmat(int ndata, const std::string filename, std::vector<int> bmask);

  void ComputeChi2_basic(int const nDat, int const nMem,
                   const double* data, matrix<double> const& L,
                   real *const& theory, real *chi2);
  template<class T> void ComputeChi2(const T*, int const&, real *const&, real *);
}
