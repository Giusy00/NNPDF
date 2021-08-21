/*
Reference: hep-ex/0608048
Hepdata: https://www.hepdata.net/record/ins724050
Published in Nucl.Phys.B 765 (2007) 1-30
DESY-HERA. Measurement of the inclusive-jet differential cross sections in 
neutral current deep inelastic scattering of 27.5 GeV positrons and electrons 
on 920 GeV protons at a centre of mass energy 319 GeV. The data, which cover 
photon virtualities (Q**2) > 125 GeV**2 were collected during the 1998-2000 
running period and have an integrated luminosity of 81.7 +- 1.8 pb-1. Jets were 
selected in the Breit frame with a longitudinally invariant KT cluster 
algorithm.

The data is taken from Hepdata, specifically from Tabs. 12-17. The cross
section is differential in pT in bins of ET and Q2.
*/

#include "ZEUS_HeraI_HQ_ptji.h"

void ZEUS_HeraI_HQ_ptjiFilter::ReadData()
{
  const int ntab=6;

  const double Q2[6]={187.5, 375.0, 750.0, 1500.0, 3500.0, 7500.0};
  
  for(int i=0; i<ntab; i++)
    {
      int index = 12+i;
      fstream f1;
      stringstream datafile("");
      datafile << dataPath() << "rawdata/" << fSetName
	       << "/HEPData-ins724050-v1-Table_" << index << ".csv";
      f1.open(datafile.str().c_str(), ios::in);

      if (f1.fail())
	{
	  cerr << "Error opening data file " << datafile.str() << endl;
	  exit(-1);
	}
      
      string line;

      for(int j=0; j<17; j++)
	{
	  getline(f1,line);
	}

      for(int j=0; j<5; j++)
	{
	  int k = 5*i+j;
	  getline(f1,line);
	  istringstream lstream(line);
	  char comma;
	  double Et, Etmin, Etmax, ddum;
	  double sys1p, sys1m, sys2p, sys2m;
	  double shift, delta;
	  lstream >> Et >> comma
		  >> Etmin >> comma
		  >> Etmax >> comma
		  >> fData[k] >> comma
		  >> fStat[k] >> comma
		  >> ddum  >> comma
		  >> sys1p >> comma
		  >> sys1m >> comma
		  >> sys2p >> comma
		  >> sys2m;

	  fKin1[k] = Et;
	  fKin2[k] = Q2[i]; //Q2
	  fKin3[k] = 318.;  //GeV

	  symmetriseErrors(sys1p, sys1m, &delta, &shift);
	  fSys[k][0].add = delta;
	  fData[k] += shift;
	  fSys[k][0].type = ADD;
	  fSys[k][0].name = "UNCORR";

	  symmetriseErrors(sys2p, sys2m, &delta, &shift);
	  fSys[k][1].add = delta;
	  fData[k] += shift;
	  fSys[k][1].type = MULT;
	  fSys[k][1].name = "CORR";

	  fSys[k][0].mult = fSys[k][0].add/fData[k] * 100;
	  fSys[k][1].mult = fSys[k][1].add/fData[k] * 100;
	  
	}
      
      f1.close();

    }

}
