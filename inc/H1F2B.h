// $Id
//
// NNPDF++ 2013
//
// Authors: Nathan Hartland,  n.p.hartland@ed.ac.uk
//          Stefano Carrazza, stefano.carrazza@mi.infn.it
//          Luigi Del Debbio, luigi.del.debbio@ed.ac.uk
//          Luca Rottoli,     luca.rottoli@physics.oc.ac.uk

#pragma once

#include "buildmaster_utils.h"

// ********** H1 reduced bb xsec ***************

static const dataInfoRaw H1F2Binfo = {
  12,                //nData
  25,                 //nSys
  "H1HERAF2B",          //SetName
  "DIS_NCE_BT"          //ProcType
};

// ********* Filters **************

class H1F2BFilter: public CommonData
{
public: H1F2BFilter():
  CommonData(H1F2Binfo) { ReadData(); }

private:
  void ReadData();
};
