// $Id$
//
// NNPDF++ 2012
//
// Authors: Nathan Hartland,  n.p.hartland@ed.ac.uk
//          Stefano Carrazza, stefano.carrazza@mi.infn.it
//          Luigi Del Debbio, luigi.del.debbio@ed.ac.uk

#include <stdio.h>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <sstream>

#include "NNPDF/fkset.h"
#include "NNPDF/fastkernel.h"
#include "NNPDF/utils.h"

namespace NNPDF
{

  /**
    * DataSet Operators
    * Ratio -> for W asymmetries etc
    */
  static void OpNull(int const& Nvals, std::vector<real*> const& obs, real*out)
  {
    for (int i=0; i<Nvals; i++)
      out[i] = obs[0][i];
    
    return;
  }

  static void OpAdd(int const& Nvals, std::vector<real*> const& obs, real*out)
  {
    for (int i=0; i<Nvals; i++)
      out[i] = obs[0][i] + obs[1][i];
    
    return;
  }

  static void OpRatio(int const& Nvals, std::vector<real*> const& obs, real*out)
  {
    if (obs.size()!=2)
    {
      std::cerr << "OpRatio Error: number of FK grids is incorrect"<<std::endl;
      exit(-1);
    }
    
    for (int i=0; i<Nvals; i++)
      out[i] = obs[0][i]/obs[1][i];
    
    return;
  }

  static void OpAsy(int const& Nvals, std::vector<real*> const& obs, real*out)
  {
    if (obs.size()!=2)
    {
      std::cerr << "OpAsy Error: number of FK grids is incorrect"<<std::endl;
      exit(-1);
    }
    
    for (int i=0; i<Nvals; i++)
      out[i] = (obs[0][i]-obs[1][i])/(obs[0][i]+obs[1][i]);
    
    return;
  }


  // Normalised sum operation
  static void OpSmn(int const& Nvals, std::vector<real*> const& obs, real*out)
  {
    if (obs.size()!=4)
    {
      std::cerr << "OpSmn Error: number of FK grids is incorrect"<<std::endl;
      exit(-1);
    }
    
    for (int i=0; i<Nvals; i++)
      out[i] = (obs[0][i]+obs[1][i])/(obs[2][i]+obs[3][i]);
    
    return;
  }


  // FKSet
  FKSet::FKSet(SigmaOp op, std::vector<FKTable*> const& fktabs):
  fOperator(op),
  fNSigma(fktabs.size()),
  fNDataFK(fktabs[0]->GetNData()),
  fHadronic(fktabs[0]->IsHadronic()),
  fDataName(fktabs[0]->GetDataName()),
  fFK(new FKTable*[fNSigma])
  {
    // Copy FKTables
    for (size_t i=0; i<fktabs.size(); i++)
      fFK[i] = fktabs[i];

    if (fNSigma == 0)
    {
      std::cerr << "FKSet::FKSet Error: No FK tables added to set"<<std::endl;
      exit(-1);
    }

    for (size_t i=0; i<fNSigma; i++)
    {
      if (fFK[i]->IsHadronic() != fHadronic)
      {
        std::cerr << "FKSet::FKSet Error: Hadronic status mismatch!"<<std::endl;
        exit(-1);
      }

      if (fFK[i]->GetNData() != fNDataFK)
      {
        std::cerr << "FKSet::FKSet Error: NData mismatch!"<<std::endl;
        exit(-1);
      }

      if (fFK[i]->GetDataName().compare(fDataName) != 0)
      {
        std::cerr << "FKSet::FKSet Error: Setname mismatch: "<<fFK[i]->GetDataName()<<"  "<<fDataName<<std::endl;
        exit(-1);
      }

    }
  };


  // FKSet copy-constructor
  FKSet::FKSet(FKSet const& set):
  fOperator(set.fOperator),
  fNSigma(set.fNSigma),
  fNDataFK(set.fNDataFK),
  fHadronic(set.fHadronic),
  fDataName(set.fDataName),
  fFK(new FKTable*[fNSigma])
  {
    // Copy FKTables
    for (size_t i=0; i<set.fNSigma; i++)
      fFK[i] = new FKTable(*set.fFK[i]);

    // Verify masking (uneccesary after one go)
    for (size_t i=0; i<fNSigma; i++)
      if (fFK[i]->GetNData() != fNDataFK)
      {
        std::cerr << "FKSet::FKSet Error: NData mismatch!"<<std::endl;
        exit(-1);
      }
  };


  // FKSet masked copy-constructor
  FKSet::FKSet(FKSet const& set, std::vector<int> const& mask):
  fOperator(set.fOperator),
  fNSigma(set.fNSigma),
  fNDataFK( mask.size() ),
  fHadronic(set.fHadronic),
  fDataName(set.fDataName),
  fFK(new FKTable*[fNSigma])
  {
    // Copy FKTables
    for (size_t i=0; i<set.fNSigma; i++)
      fFK[i] = new FKTable(*set.fFK[i], mask);

    // Verify masking (uneccesary after one go)
    for (size_t i=0; i<fNSigma; i++)
      if (fFK[i]->GetNData() != fNDataFK)
      {
        std::cerr << "FKSet::FKSet Error: NData mismatch!"<<std::endl;
        exit(-1);
      }
  };

  FKSet::~FKSet()
  {
    for (int i=0; i<fNSigma; i++)
      delete fFK[i];
    delete[] fFK;
  }

    // Parse dataset operators
  SigmaOp FKSet::parseOperator(std::string const& op)
  {

    if (op.compare("RATIO") == 0)
      return OpRatio;

    if (op.compare("ASY") == 0)
      return OpAsy;

    if (op.compare("ADD") == 0)
      return OpAdd;

    if (op.compare("SMN") == 0)
      return OpSmn;

    if (op.compare("NULL") == 0)
      return OpNull;

      // Add other operations here if required

    std::cerr << "parseOperator Error: Operator "<<op<<" unknown!"<<std::endl;
    exit(-1);

    return OpNull;
  }

}

