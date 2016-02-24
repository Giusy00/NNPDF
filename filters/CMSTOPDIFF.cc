/*
Experiment: CERN-LHC-CMS (CMS)
Preprinted as CERN-PH-EP-2015-117
Preprinted as CMS-TOP-12-028
Archived as: ARXIV:1505.04480
Published in Eur.Phys.J. C75 (2015) 11, 542

Record in: INSPIRE
Record in: CERN Document Server
Record in: HEPData 

Description of the measurement 
The normalized differential cross section for top quark pair (ttbar) 
production is measured in pp collisions at a centre-of-mass energy 
of 8 TeV at the CERN LHC using the CMS detector in data corresponding 
to an integrated luminosity of 19.7 inverse femtobarns. 
The measurements are performed in the lepton+jets (e/mu+jets) and in the 
dilepton (e e, mu mu, and e mu) decay channels. 
The ttbar cross section is measured as a function of the kinematic 
properties of the charged leptons, the jets associated to b quarks, 
the top quarks, and the ttbar system. 

Description of the buildmaster implementation
Normalized cross sections for the distributions (lepton+jets channel)
differential in the following variables are implemented:
1) top quark transverse momentum;       
2) top quark pair transverse momentum;  
3) top quark rapidity;                  
4) top quark pair rapidity;             
5) top quark pair invariant mass.       

Raw data and full breakdown of systematic uncertainties are from HepData:
http://hepdata.cedar.ac.uk/view/ins1370682
1) TABS 15-16-17 HepData; TAB A.6 in the preprint
2) TABS 33-34-35 HepData; TAB A.9 in the preprint
3) TABS 21-22-23 HepData; TAB A.7 in the preprint
4) TABS 36-37-38 Hepdata; TAB A.9 in the preprint
5) TABS 39-40-41 HepData; TAB A.9 in the preprint

Notes:
1) The data is available separately for the lepton+jets and for the 
   dilepton channel.
2) The statistical covariance matrix is also available, so far we take 
   into account only the principal diagonal values.
3) All systematic uncertainties are assumed to be multiplicative.
4) Custom uncertainty descriptions are assumed to allow for cross-correlations
   among the five differential distributions. 
5) Unnormalized differential distributions are obtained by multiplying the
   normalized distributions by the total inclusive ttbar cross section   
   available in CMS PAS TOP-13-004. 
   Statistical uncertainties (on the total cross section and on the 
   normalised distributions) are added in quadrature.
   Systematic uncertainties (of the normalised distributions) factorise.
   Two addidional sources of systematics coming from the total cross 
   section (total sys and lumi) are considered on top of the full 
   breakdown of the systematics on normalised distributions.
*/
 
#include "CMSTOPDIFF.h"

//A - NORMALISED distributions

//1) Distribution differential in top quark transverse momentum
void  CMSTOPDIFF8TEVTPTFilter::ReadData()
{
  // Opening files
  fstream f1, f2;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
	   << fSetName << "/" << fSetName <<".data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() << "rawdata/"
	    << fSetName << "/" << fSetName << ".sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";

  //Starting filter
  string line;
  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;
  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  lstream >> fSys[i][j].mult;
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
  
  f1.close();
  f2.close();

}

//==================================================================

//2) Distribution differential in top quark pair transverse momentum
void  CMSTOPDIFF8TEVTTPTFilter::ReadData()
{
  // Opening files
  fstream f1, f2;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
	   << fSetName << "/" << fSetName <<".data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() << "rawdata/"
	    << fSetName << "/" << fSetName << ".sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";

  //Starting filter
  string line;
  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;
  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  lstream >> fSys[i][j].mult;
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
  
  f1.close();
  f2.close();

}

//==============================================================

//3) Distribution differential in top quark rapidity
void  CMSTOPDIFF8TEVTRAPFilter::ReadData()
{
  // Opening files
  fstream f1, f2;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
	   << fSetName << "/" << fSetName <<".data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() << "rawdata/"
	    << fSetName << "/" << fSetName << ".sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";

  //Starting filter
  string line;
  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;
  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  lstream >> fSys[i][j].mult;
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
  
  f1.close();
  f2.close();

}

//=================================================================

//4) Distribution differential in top quark pair rapidity
void  CMSTOPDIFF8TEVTTRAPFilter::ReadData()
{
  // Opening files
  fstream f1, f2;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
	   << fSetName << "/" << fSetName <<".data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() << "rawdata/"
	    << fSetName << "/" << fSetName << ".sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";

  //Starting filter
  string line;
  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;
  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  lstream >> fSys[i][j].mult;
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
  
  f1.close();
  f2.close();

}

//=================================================================

//5) Distribution differential in top quark pair invariant mass
void  CMSTOPDIFF8TEVTTMFilter::ReadData()
{
  // Opening files
  fstream f1, f2;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
	   << fSetName << "/" << fSetName <<".data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() << "rawdata/"
	    << fSetName << "/" << fSetName << ".sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";

  //Starting filter
  string line;
  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;
  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  lstream >> fSys[i][j].mult;
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
  
  f1.close();
  f2.close();

}

/*
========================================================================
*/

//B - UNNORMALISED distributions

//1) Distribution differential in top quark transverse momentum
void  CMSTOPDIFF8TEVTPTUNNORMFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() 
	   << "rawdata/CMSTOPDIFF8TEVTPT/CMSTOPDIFF8TEVTPT.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() 
	  << "rawdata/CMSTOPDIFF8TEVTPT/CMSTOPDIFF8TEVTPT.sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Inclusive total cross section
  stringstream sigmatotfile("");
  sigmatotfile << dataPath() 
	       << "rawdata/CMSTOPDIFF8TEVTOT/CMSTOPDIFF8TEVTOT.data";
  f3.open(sigmatotfile.str().c_str(), ios::in);

  if (f3.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";
  sysdescr[11]="CMSTOPDIFFTotXSec";
  sysdescr[12]="CMSTOPDIFFLumi";

  //Starting filter
  string line;

  for(int i=0; i<3; i++)
    {
      getline(f3,line);
    }

  double xscv, xsstat, xssystpl, xssystmi, xslumi;
  double dtmp, stmp;

  f3 >> xscv >> xsstat >> xssystpl >> xssystmi >> xslumi;

  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;

  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      //differential distributions are unnormalized
      fData[i] = fData[i]*xscv;
      //statistical uncertainties are added in quadrature
      fStat[i] = fData[i]*pow(pow(fStat[i]/(fData[i]/xscv),2)+pow(xsstat/xscv,2),0.5); 

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys-2; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  //Relative systematic uncertainties are the same for both normalised and unnormalised distributions
	  lstream >> fSys[i][j].mult; 
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
 
  //Two additional sources of systematic uncertainties affect the unnormalised distributions
  for(int i=0; i<fNData; i++)
    {
      symmetriseErrors(xssystpl, xssystmi, &stmp, &dtmp); //symmetrise systematics
      fSys[i][11].add  = fData[i]/xscv*stmp;
      fSys[i][11].mult = fSys[i][11].add/fData[i]*100; 
      fSys[i][11].type = MULT;
      fSys[i][11].name = sysdescr[11];

      fSys[i][12].add  = fData[i]/xscv*xslumi;
      fSys[i][12].mult = fSys[i][12].add/fData[i]*100;
      fSys[i][12].type = MULT;
      fSys[i][12].name = sysdescr[12];
    }
  
  f1.close();
  f2.close();
  f3.close();

}

//========================================================================

//2) Distribution differential in top quark pair transverse momentum
void  CMSTOPDIFF8TEVTTPTUNNORMFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() 
	   << "rawdata/CMSTOPDIFF8TEVTTPT/CMSTOPDIFF8TEVTTPT.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() 
	  << "rawdata/CMSTOPDIFF8TEVTTPT/CMSTOPDIFF8TEVTTPT.sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Inclusive total cross section
  stringstream sigmatotfile("");
  sigmatotfile << dataPath() 
	       << "rawdata/CMSTOPDIFF8TEVTOT/CMSTOPDIFF8TEVTOT.data";
  f3.open(sigmatotfile.str().c_str(), ios::in);

  if (f3.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";
  sysdescr[11]="CMSTOPDIFFTotXSec";
  sysdescr[12]="CMSTOPDIFFLumi";

  //Starting filter
  string line;

  for(int i=0; i<3; i++)
    {
      getline(f3,line);
    }

  double xscv, xsstat, xssystpl, xssystmi, xslumi;
  double dtmp, stmp;

  f3 >> xscv >> xsstat >> xssystpl >> xssystmi >> xslumi;

  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;

  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      //differential distributions are unnormalized
      fData[i] = fData[i]*xscv;
      //statistical uncertainties are added in quadrature
      fStat[i] = fData[i]*pow(pow(fStat[i]/(fData[i]/xscv),2)+pow(xsstat/xscv,2),0.5); 

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys-2; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  //Relative systematic uncertainties are the same for both normalised and unnormalised distributions
	  lstream >> fSys[i][j].mult; 
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
 
  //Two additional sources of systematic uncertainties affect the unnormalised distributions
  for(int i=0; i<fNData; i++)
    {
      symmetriseErrors(xssystpl, xssystmi, &stmp, &dtmp); //symmetrise systematics
      fSys[i][11].add  = fData[i]/xscv*stmp;
      fSys[i][11].mult = fSys[i][11].add/fData[i]*100; 
      fSys[i][11].type = MULT;
      fSys[i][11].name = sysdescr[11];

      fSys[i][12].add  = fData[i]/xscv*xslumi;
      fSys[i][12].mult = fSys[i][12].add/fData[i]*100;
      fSys[i][12].type = MULT;
      fSys[i][12].name = sysdescr[12];
    }
  
  f1.close();
  f2.close();
  f3.close();

}

//===================================================================

//3) Distribution differential in top quark rapidity
void  CMSTOPDIFF8TEVTRAPUNNORMFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() 
	   << "rawdata/CMSTOPDIFF8TEVTRAP/CMSTOPDIFF8TEVTRAP.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() 
	  << "rawdata/CMSTOPDIFF8TEVTRAP/CMSTOPDIFF8TEVTRAP.sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Inclusive total cross section
  stringstream sigmatotfile("");
  sigmatotfile << dataPath() 
	       << "rawdata/CMSTOPDIFF8TEVTOT/CMSTOPDIFF8TEVTOT.data";
  f3.open(sigmatotfile.str().c_str(), ios::in);

  if (f3.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";
  sysdescr[11]="CMSTOPDIFFTotXSec";
  sysdescr[12]="CMSTOPDIFFLumi";

  //Starting filter
  string line;

  for(int i=0; i<3; i++)
    {
      getline(f3,line);
    }

  double xscv, xsstat, xssystpl, xssystmi, xslumi;
  double dtmp, stmp;

  f3 >> xscv >> xsstat >> xssystpl >> xssystmi >> xslumi;

  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;

  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      //differential distributions are unnormalized
      fData[i] = fData[i]*xscv;
      //statistical uncertainties are added in quadrature
      fStat[i] = fData[i]*pow(pow(fStat[i]/(fData[i]/xscv),2)+pow(xsstat/xscv,2),0.5); 

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys-2; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  //Relative systematic uncertainties are the same for both normalised and unnormalised distributions
	  lstream >> fSys[i][j].mult; 
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
 
  //Two additional sources of systematic uncertainties affect the unnormalised distributions
  for(int i=0; i<fNData; i++)
    {
      symmetriseErrors(xssystpl, xssystmi, &stmp, &dtmp); //symmetrise systematics
      fSys[i][11].add  = fData[i]/xscv*stmp;
      fSys[i][11].mult = fSys[i][11].add/fData[i]*100; 
      fSys[i][11].type = MULT;
      fSys[i][11].name = sysdescr[11];

      fSys[i][12].add  = fData[i]/xscv*xslumi;
      fSys[i][12].mult = fSys[i][12].add/fData[i]*100;
      fSys[i][12].type = MULT;
      fSys[i][12].name = sysdescr[12];
    }
  
  f1.close();
  f2.close();
  f3.close();

}

//==================================================================

//4) Distribution differential in top quark pairrapidity
void  CMSTOPDIFF8TEVTTRAPUNNORMFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() 
	   << "rawdata/CMSTOPDIFF8TEVTTRAP/CMSTOPDIFF8TEVTTRAP.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() 
	  << "rawdata/CMSTOPDIFF8TEVTTRAP/CMSTOPDIFF8TEVTTRAP.sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Inclusive total cross section
  stringstream sigmatotfile("");
  sigmatotfile << dataPath() 
	       << "rawdata/CMSTOPDIFF8TEVTOT/CMSTOPDIFF8TEVTOT.data";
  f3.open(sigmatotfile.str().c_str(), ios::in);

  if (f3.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";
  sysdescr[11]="CMSTOPDIFFTotXSec";
  sysdescr[12]="CMSTOPDIFFLumi";

  //Starting filter
  string line;

  for(int i=0; i<3; i++)
    {
      getline(f3,line);
    }

  double xscv, xsstat, xssystpl, xssystmi, xslumi;
  double dtmp, stmp;

  f3 >> xscv >> xsstat >> xssystpl >> xssystmi >> xslumi;

  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;

  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      //differential distributions are unnormalized
      fData[i] = fData[i]*xscv;
      //statistical uncertainties are added in quadrature
      fStat[i] = fData[i]*pow(pow(fStat[i]/(fData[i]/xscv),2)+pow(xsstat/xscv,2),0.5); 

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys-2; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  //Relative systematic uncertainties are the same for both normalised and unnormalised distributions
	  lstream >> fSys[i][j].mult; 
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
 
  //Two additional sources of systematic uncertainties affect the unnormalised distributions
  for(int i=0; i<fNData; i++)
    {
      symmetriseErrors(xssystpl, xssystmi, &stmp, &dtmp); //symmetrise systematics
      fSys[i][11].add  = fData[i]/xscv*stmp;
      fSys[i][11].mult = fSys[i][11].add/fData[i]*100; 
      fSys[i][11].type = MULT;
      fSys[i][11].name = sysdescr[11];

      fSys[i][12].add  = fData[i]/xscv*xslumi;
      fSys[i][12].mult = fSys[i][12].add/fData[i]*100;
      fSys[i][12].type = MULT;
      fSys[i][12].name = sysdescr[12];
    }
  
  f1.close();
  f2.close();
  f3.close();

}

//====================================================================

//5) Distribution differential in top quark pair invariant mass
void  CMSTOPDIFF8TEVTTMUNNORMFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;

  //Central values and statistical uncertainties
  stringstream datafile("");
  datafile << dataPath() 
	   << "rawdata/CMSTOPDIFF8TEVTTM/CMSTOPDIFF8TEVTTM.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) 
    {
      cerr << "Error opening data file " << datafile.str() << endl;
      exit(-1);
    }
  
  //Full breakdown of systematic uncertainties
  stringstream sysfile("");
  sysfile << dataPath() 
	  << "rawdata/CMSTOPDIFF8TEVTTM/CMSTOPDIFF8TEVTTM.sys";
  f2.open(sysfile.str().c_str(), ios::in);

  if (f2.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Inclusive total cross section
  stringstream sigmatotfile("");
  sigmatotfile << dataPath() 
	       << "rawdata/CMSTOPDIFF8TEVTOT/CMSTOPDIFF8TEVTOT.data";
  f3.open(sigmatotfile.str().c_str(), ios::in);

  if (f3.fail()) 
    {
      cerr << "Error opening data file " << sysfile.str() << endl;
      exit(-1);
    }

  //Define custom uncertainty descriptions to allow for cross-correlated 
  string sysdescr[fNSys];
  sysdescr[0]="CMSTOPDIFFLEP";
  sysdescr[1]="CMSTOPDIFFJES";
  sysdescr[2]="CMSTOPDIFFJER";
  sysdescr[3]="CMSTOPDIFFBG";
  sysdescr[4]="CMSTOPDIFFBtag";
  sysdescr[5]="CMSTOPDIFFPU";
  sysdescr[6]="CMSTOPDIFFTopScale";
  sysdescr[7]="CMSTOPDIFFTopMatch";
  sysdescr[8]="CMSTOPDIFFHadronization";
  sysdescr[9]="CMSTOPDIFFTopMass";
  sysdescr[10]="CMSTOPDIFFPDF";
  sysdescr[11]="CMSTOPDIFFTotXSec";
  sysdescr[12]="CMSTOPDIFFLumi";

  //Starting filter
  string line;

  for(int i=0; i<3; i++)
    {
      getline(f3,line);
    }

  double xscv, xsstat, xssystpl, xssystmi, xslumi;
  double dtmp, stmp;

  f3 >> xscv >> xsstat >> xssystpl >> xssystmi >> xslumi;

  for(int i=0; i<10; i++)
    {
      getline(f1,line);
    }

  int idum;

  for(int i=0; i<fNData; i++)
    {
      getline(f1,line);
      istringstream lstream(line);
      lstream >> idum;
      double adum;
      for(int j=0; j<5; j++)
	{
	  lstream >> adum;
	}
      double pt_top;
      lstream >> pt_top;
      
      fKin1[i] = pt_top;   //P_T^(top)
      fKin2[i] = Mt*Mt;    //mu^2
      fKin3[i] = 8000;     //sqrt(s)

      lstream >> fData[i]; //normalized differential distribution
      lstream >> fStat[i]; //assume stat errors uncorrelated so far

      //differential distributions are unnormalized
      fData[i] = fData[i]*xscv;
      //statistical uncertainties are added in quadrature
      fStat[i] = fData[i]*pow(pow(fStat[i]/(fData[i]/xscv),2)+pow(xsstat/xscv,2),0.5); 

      for(int j=0; j<3; j++)
	{
	  lstream >> adum;
	}
    }

  for(int i=0; i<8; i++)
    {
      getline(f2,line);
    }

  for(int j=0; j<fNSys-2; j++)
    {
      string sdum;
      getline(f2,line);
      istringstream lstream(line);
      lstream >> sdum;
      for(int i=0; i<fNData; i++)
	{
	  //Relative systematic uncertainties are the same for both normalised and unnormalised distributions
	  lstream >> fSys[i][j].mult; 
	  fSys[i][j].add = fSys[i][j].mult*fData[i]/100;
	  fSys[i][j].type = MULT;
	  fSys[i][j].name = sysdescr[j];
	}
    }
 
  //Two additional sources of systematic uncertainties affect the unnormalised distributions
  for(int i=0; i<fNData; i++)
    {
      symmetriseErrors(xssystpl, xssystmi, &stmp, &dtmp); //symmetrise systematics
      fSys[i][11].add  = fData[i]/xscv*stmp;
      fSys[i][11].mult = fSys[i][11].add/fData[i]*100; 
      fSys[i][11].type = MULT;
      fSys[i][11].name = sysdescr[11];

      fSys[i][12].add  = fData[i]/xscv*xslumi;
      fSys[i][12].mult = fSys[i][12].add/fData[i]*100;
      fSys[i][12].type = MULT;
      fSys[i][12].name = sysdescr[12];
    }
  
  f1.close();
  f2.close();
  f3.close();

}
