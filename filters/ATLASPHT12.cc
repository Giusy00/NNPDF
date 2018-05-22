/*
 * ATLASPHT12 - ATLAS inclusive photons 2012
 *
 * ATLAS isolated photon production, LHC 8 TeV, 20.2 fb^-1
 * Reference:  [arXiv:1605.03495] 
 * 
 */

#include "ATLASPHT12.h"

/*
 * d sigma/dE_{T}^{gamma} [pb / GeV], 
 * Bin 1: |eta| < 0.6
 * Bin 2: 0.6 < |eta| < 1.37
 * Bin 3: 1.56 < |eta| < 1.81
 * 4th bin excluded 
 *
 */

void ATLASPHT12Filter::FilterData(fstream & file, int nDataMin, int nDataMax, double rap)
{

 for (int idat = nDataMin; idat < nDataMax; idat++) {
      double shift = 0.;

      double central, upper, lower, dummy;
      string line; 
      getline(file,line);
      istringstream lstream(line);

      lstream >> central >> lower >> upper >> fData[idat] >> fStat[idat] >> dummy;

      for(int j=0; j<2; ++j) {

        double sys1, sys2, plus, minus;
        double stmp, dtmp;

        lstream >> sys1 >> sys2;
        minus=sys2; 
        plus=sys1;

        //convert to relative percentage values
        plus = plus/fData[idat]*100;  
        minus = minus/fData[idat]*100;
        symmetriseErrors(plus,minus,&stmp,&dtmp);

        fSys[idat][j].type = MULT;
        fSys[idat][j].name = "CORR";
        fSys[idat][j].mult = stmp;
        fSys[idat][j].add  = fSys[idat][j].mult*fData[idat]/100;

        shift += dtmp;
      }

      for(int j=2; j<7; ++j) {

        double sys1, sys2, plus, minus;
        double stmp, dtmp;

        lstream >> sys1 >> sys2;
        minus=sys2; 
        plus=sys1;

        //convert to relative percentage values
        plus = plus/fData[idat]*100;  
        minus = minus/fData[idat]*100;
        symmetriseErrors(plus,minus,&stmp,&dtmp);

        fSys[idat][j].type = MULT;
        fSys[idat][j].name = "UNCORR";
        fSys[idat][j].mult = stmp;
        fSys[idat][j].add  = fSys[idat][j].mult*fData[idat]/100;

        shift += dtmp;
      }

      for(int j=7; j<fNSys-1; ++j) {

        double sys1, sys2, plus, minus;
        double stmp, dtmp;

        lstream >> sys1 >> sys2;
        minus=sys2; 
        plus=sys1;

        //convert to relative percentage values
        plus = plus/fData[idat]*100;  
        minus = minus/fData[idat]*100;
        symmetriseErrors(plus,minus,&stmp,&dtmp);

        fSys[idat][j].type = MULT;
        fSys[idat][j].name = "CORR";
        fSys[idat][j].mult = stmp;
        fSys[idat][j].add  = fSys[idat][j].mult*fData[idat]/100;

        shift += dtmp;
      }

    for(int j=fNSys-1; j<fNSys; ++j) {

        double sys1, sys2, plus, minus;
        double stmp, dtmp;

        lstream >> sys1 >> sys2;
        minus=sys2; 
        plus=sys1;

        //convert to relative percentage values
        plus = plus/fData[idat]*100;  
        minus = minus/fData[idat]*100;
        symmetriseErrors(plus,minus,&stmp,&dtmp);

        // some of the uncertainties are uncorrelated
        fSys[idat][j].type = MULT;
        fSys[idat][j].name = "ATLASLUMI12";
        fSys[idat][j].mult = stmp;
        fSys[idat][j].add  = fSys[idat][j].mult*fData[idat]/100;

        shift += dtmp;
    }

  fData[idat]*=(1.0 + shift*0.01); //Shift from asymmetric errors

    // Kinematic variables
    
    fKin1[idat] = rap;                     // Avg. eta_gamma 
    fKin2[idat] = pow((upper + lower) * 0.5,2);   // Avg. Et of each bin
    fKin3[idat] = 8000.;                              // LHC 8 TeV
    
  }
}

void ATLASPHT12Filter::ReadData()
{
  // Opening files
  fstream cent, fwd1, fwd2;

  stringstream datafileCNTR("");
  datafileCNTR << dataPath() << "rawdata/ATLASPHT12/eta_bin1.dat";
  cent.open(datafileCNTR.str().c_str(), ios::in);

  if (cent.fail()) {
    cerr << "Error opening data file " << datafileCNTR.str() << endl;
    exit(-1);
  }

  stringstream datafileFWD1("");
  datafileFWD1 << dataPath() << "rawdata/ATLASPHT12/eta_bin2.dat";
  fwd1.open(datafileFWD1.str().c_str(), ios::in);

  if (fwd1.fail()) {
    cerr << "Error opening data file " << datafileFWD1.str() << endl;
    exit(-1);
  }

  stringstream datafileFWD2("");
  datafileFWD2 << dataPath() << "rawdata/ATLASPHT12/eta_bin3.dat";
  fwd2.open(datafileFWD2.str().c_str(), ios::in);

  if (fwd2.fail()) {
    cerr << "Error opening data file " << datafileFWD2.str() << endl;
    exit(-1);
  }

FilterData(cent,  0,  18,  0.3);
FilterData(fwd1,  18,  35,  0.385);
FilterData(fwd2,  35,  49,  0.125);

  cent.close();
  fwd1.close();
  fwd2.close();
}

