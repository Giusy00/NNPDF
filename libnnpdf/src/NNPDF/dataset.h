// $Id: dataset.h 2990 2015-06-08 19:06:21Z s1044006 $
//
// NNPDF++ 2012
//
// Authors: Nathan Hartland,  n.p.hartland@ed.ac.uk
//          Stefano Carrazza, stefano.carrazza@mi.infn.it
//          Luigi Del Debbio, luigi.del.debbio@ed.ac.uk

#pragma once

#include "common.h"
#include <string>
#include <fstream>
#include <algorithm>

#include "fkset.h"
#include "pdfset.h"
#include "commondata.h"

namespace NNPDF
{

  class ThPredictions;


  /**
   *  \class DataSet
   *  \brief Class for datasets loading and computing of observables
   */
  class DataSet : public CommonData, public FKSet
  {
   private:    
    bool fIsArtificial; //!< Flag to determine if data is artifical
    bool fIsT0;         //!< Flag to determine if covmat is T0
    bool fHasCovMat;    //!< Flag to determine if covmat has been computed

    // Data information
    double *fT0Pred;      //!< The t0 predictions - defaults to data in case of no t0-std::vector
    double **fCovMat;     //!< The covariance matrix
    double **fSqrtCov;    //!< The Cholesky decomposition of the covariance matrix
    
    // private methods for constructor
    void GenCovMat();     //!< Generate covariance matrix

    DataSet();                          //!< Disable default constructor

   public:
    DataSet(CommonData const&, FKSet const&, bool computecovmat = false); //!< Constructor
    virtual ~DataSet();                       //!< The destructor.    

    DataSet(const DataSet&);            //!< Copy constructor
    friend void swap(DataSet&, DataSet&);
    DataSet& operator=(DataSet);        //!< Copy-assignment
    DataSet(DataSet&&);                 //!< Move constructor
    DataSet(const DataSet&, std::vector<int> const&, bool computecovmat = false);     //!< Masked Copy constructor

    // ****************   DataSet T0 Methods  **********************

    void   SetT0( ThPredictions  const&);               //!< Set T0 predictions
    void   SetT0(PDFSet const&);                        //!< Set T0 predictions
    bool   const& IsT0 ()  const { return fIsT0; }      //!< Return t0 covmat flag
    
    // ************************ Data Get Methods ******************************
    
    double const&  GetT0Pred(int i)    const { return fT0Pred[i];}  //!< Return t0 prediction
    
    double** GetCovMat()  const; //!< Return fCovMat
    double** GetSqrtCov() const; //!< Return the Cholesky decomposition of the covariance matrix
    double const& GetSqrtCov(int const& i, int const& j) const; //!< Returns an element of the Cholesky decomposition

    bool const& IsArtificial()         const { return fIsArtificial;} //!< Returns the artificial flag
    
    // ****************   Update data values  ********************************

    void   MakeArtificial(); //!< Make an artificial data replica
    
    void   UpdateData(double* newdat);                //!< Update data
    void   UpdateData(double* newdat, double* norm);  //!< Update with a rescaling - also rescales additive uncertainties
    void   UpdateData(double* newdat, sysType* type); //!< Update data and systypes

    void SetArtificial( bool const& artificial) {fIsArtificial = artificial;};
    
    // ****************   Rescale Uncertainties   ****************************
    
    void RescaleErrors(const double mult); //!< Rescale uncertainties by a multiplicative factor
    
    // **************************************************************************
  
  };
  
};
