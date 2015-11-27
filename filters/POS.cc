/**
 * POS.cc
 * Positivity observables
 */

#include "POS.h"

static const int nDYsets = 20;
static const std::string DYSets[nDYsets] = 
{
  "POSDYC",
  "POSDYCBD",
  "POSDYCBDB",
  "POSDYCBS",
  "POSDYCBSB",
  "POSDYCD",
  "POSDYCDB",
  "POSDYCS",
  "POSDYCSB",
  "POSDYD",
  "POSDYS",
  "POSDYU",
  "POSDYUBD",
  "POSDYUBDB",
  "POSDYUBS",
  "POSDYUBSB",
  "POSDYUD",
  "POSDYUDB",
  "POSDYUS",
  "POSDYUSB"
};

static const std::string DYProc[nDYsets] = {
  "DYP_PPY_CON_CH",
  "DYP_CNS_CON_CBD",
  "DYP_CNO_CON_CBD",
  "DYP_CNS_CON_CBS",
  "DYP_CNO_CON_CBS",
  "DYP_CPO_CON_CDB",
  "DYP_CPS_CON_CDB",
  "DYP_CPO_CON_CSB",
  "DYP_CPS_CON_CSB",
  "DYP_PPY_CON_DW",
  "DYP_PPY_CON_ST",
  "DYP_PPY_CON_UP",
  "DYP_CNS_CON_UBD",
  "DYP_CNO_CON_UBD",
  "DYP_CNS_CON_UBS",
  "DYP_CNO_CON_UBS",
  "DYP_CPO_CON_UDB",
  "DYP_CPS_CON_UDB",
  "DYP_CPO_CON_USB",
  "DYP_CPS_CON_USB"
};

const int nDISsets = 4;
static const std::string DISSets[nDISsets] = {
  "POSF2DW",
  "POSF2S",
  "POSF2U",
  "POSFLL"
};

static const std::string DISProc[nDISsets] = {
  "DIS_F2d",
  "DIS_F2S",
  "DIS_F2U",
  "DIS_FLL"
};

void registerDYPos(vector<CommonData*>& list)
{
  const int nDYpoints = 20; // Number of points in a dataset

  for (int i=0; i<nDYsets; i++)
  {
    const dataInfoRaw posInfo = {
      nDYpoints,  
      0,       
      DYSets[i],   
      DYProc[i] 
    };

    list.push_back(new DYPosFilter(posInfo));
  }
}

void registerDISPos(vector<CommonData*>& list)
{
  const int nDISpoints = 20; // Number of points in a dataset

  for (int i=0; i<nDISsets; i++)
  {
    const dataInfoRaw posInfo = {
      nDISpoints,  
      0,       
      DISSets[i],   
      DISProc[i] 
    };

    list.push_back(new DISPosFilter(posInfo));
  }
}


void DYPosFilter::ReadData()
{
  const double xmin = 1E-2;
  const double xmax = 0.9;
  const double xch = 0.1;
  
  const int nxposlog = fNData/2.0;
  const double step   = ( xmax - xch ) / ( fNData - nxposlog );

  const double q2pos = 100;  // DY positivity imposed at 100GeV 
  const double tau = xmin * xmax;
  const double sqrts = sqrt(q2pos/tau);


  for (int i=0; i< fNData; i++)
  {
    if (i < nxposlog)
    {
      const double x1 =  xmin*pow( xch / xmin ,(double)i/(double)(nxposlog-1));
      fKin1[i] = log( x1 / sqrt(tau) );
    }
    else 
    {
      const double x1 = xch + step * ( 1 + i - nxposlog);
      fKin1[i] = log( x1 / sqrt(tau) );
    }

    fData[i] = 0;
    fKin2[i] = q2pos;
    fKin3[i] = sqrts;
  }

}

void DISPosFilter::ReadData()
{
  const double q2pos = 5;

  const double xmin = 5E-7;
  const double xmax = 0.9;
  const double xch = 0.1;
  
  const int nxposlog = fNData/2.0;
  const double step  = ( xmax - xch ) / ( fNData - nxposlog );

  for (int i=0; i< fNData; i++)
  {
    if (i < nxposlog)
      fKin1[i] = xmin*pow( xch / xmin ,(double)i/(double)(nxposlog-1));
    else 
      fKin1[i] = xch + step * ( 1 + i - nxposlog);

    fData[i] = 0;
    fKin2[i] = q2pos;
    fKin3[i] = 0;
  }

}