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

class H1_HQ_ptji_1JETFilter: public CommonData
{
public: H1_HQ_ptji_1JETFilter():
  CommonData("H1_HQ_ptji_1JET") { ReadData(); }

private:
  void ReadData();
};

class H1_HQ_ptji_2JETFilter: public CommonData
{
public: H1_HQ_ptji_2JETFilter():
  CommonData("H1_HQ_ptji_2JET") { ReadData(); }

private:
  void ReadData();
};
