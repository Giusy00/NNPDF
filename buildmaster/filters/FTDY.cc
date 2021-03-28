/*
WARNING: File modified by ERN Nov 2020.
Additional data sets, with suffix _dw and _sh have been added with extra 
systematic ucnertainties. These systematic ucnertainties account for nuclear 
uncertainties (estimated according to 1812.09074).
The two strategies (dw=deweighted and sh=shifted) are implemented.
The necessary shifts can be printed on screen and should be pasted into the
appropriate cfactor file.
*/

/**
 *
 *     Drell-Yan experiment E605
 *
 *     Data from
 *     "Dimuon production in proton-copper collisions at
 *     sqrt(s)=38.8 GeV"
 *
 *     EXPeriment = FNAL-605
 *     REaction = p Nucleus --> mu+ mu- X
 *     Plab = 800 GeV
 *
 *     G. Moreno et al., PRD 43 (1991) 9
 *
 *     The format of data is for the paper:
 *
 *     y   sqrt(tau)  s*d^2sigma/dsqt(tau)/dy [pb GeV2 / nucleon]  stat(abs.)
 *
 *     but for the tables from HEPDATA, in the file data/dy-E605/dy-e605.data
 *     one has instead
 *
 *     y   sqrt(tau)  s*d^2sigma/dsqt(tau)/dy [cm2 GeV2 / nucleon]  stat(abs.)
 *
 *     So there is a conversion factor 10E33 between them
 *
 *     s: Center of mass energy of the collision squared
 *     sqrt(tau): M/sqrt(s), with M the invariant mass of the muon pair
 *     y: lepton rapidity: log( ( q0 + qz ) / ( q0 - qz ) ) / 2
 *
 *     The statistical error is given in its absolute value
 *     On top of this, there is a 10% systematic uncertainty and
 *     and a 15% overall normalization uncertainty
 *     Overall `K-factor' from NLO QCD prediction 1.071 +- 0.010.
 *     The 10% systematic uncertainty is taken to be uncorrelated
 *     and added in quadrature to the statistical uncertainty
 *
 *     Data in file:
 *     data/dy-E605/dy-e605.data
 *
 *     At some point it will be necessary to check the effects
 *     in this dataset of various models of nuclear corrections,
 *     since E-605 uses a nuclear Copper target. However statistical
 *     errors are much larger than typical nuclear PDF corrections
 *
 *
 */

#include "FTDY.h"

void DYE605Filter::ReadData()
{
  // Opening files
  fstream f1;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/dy-e605.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }
  
  // Starting filter
  double convfact = 1e33;
  double SCM = 38.8*38.8;  
  
  string line;
  double sqrttau;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    
    lstream >> sqrttau;
    // Instead of sqrttau, save M2 as second kinematical variable using
    // M2 = taus * S
    fKin2[i] = sqrttau*sqrttau*SCM;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    fData[i]*= convfact;     // Convert from cm2 to pb
    
    lstream >> fStat[i];     // stat
    fStat[i]*= convfact;     // Convert from cm2 to pb
    
    fSys[i][0].mult = 10.0;   // 10% uncorrelated systematic
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "UNCORR";
    
    fSys[i][1].mult = 15.0;         // 15% normalisation uncertainty
    fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
    fSys[i][1].type = MULT;
    fSys[i][1].name = "CORR";
  }
  
  f1.close();  
}

void DYE605_dwFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE605/dy-e605.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE605/nuclear/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE605/proton/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }

  // Starting filter
  double convfact = 1e33;
  double SCM = 38.8*38.8;
  int nrep=1000;
  int nrealsys=2;
  
  string line;
  double sqrttau;

  getline(f2,line);
  getline(f3,line);
  
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    
    lstream >> sqrttau;
    // Instead of sqrttau, save M2 as second kinematical variable using
    // M2 = taus * S
    fKin2[i] = sqrttau*sqrttau*SCM;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    fData[i]*= convfact;     // Convert from cm2 to pb
    
    lstream >> fStat[i];     // stat
    fStat[i]*= convfact;     // Convert from cm2 to pb
    
    fSys[i][0].mult = 10.0;   // 10% uncorrelated systematic
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "UNCORR";
    
    fSys[i][1].mult = 15.0;         // 15% normalisation uncertainty
    fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
    fSys[i][1].type = MULT;
    fSys[i][1].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    nstream >> sdum >> sdum >> idum >> ddum >> ddum;
    
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - proton_cv)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "NUCLEAR" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }
  }
  
  f1.close();
  f2.close();
  f3.close();
  
}

void DYE605_shFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE605/dy-e605.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE605/nuclear/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE605/proton/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }

  // Starting filter
  double convfact = 1e33;
  double SCM = 38.8*38.8;
  int nrep=1000;
  int nrealsys=2;
  
  string line;
  double sqrttau;

  getline(f2,line);
  getline(f3,line);
  
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    
    lstream >> sqrttau;
    // Instead of sqrttau, save M2 as second kinematical variable using
    // M2 = taus * S
    fKin2[i] = sqrttau*sqrttau*SCM;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    fData[i]*= convfact;     // Convert from cm2 to pb
    
    lstream >> fStat[i];     // stat
    fStat[i]*= convfact;     // Convert from cm2 to pb
    
    fSys[i][0].mult = 10.0;   // 10% uncorrelated systematic
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "UNCORR";
    
    fSys[i][1].mult = 15.0;         // 15% normalisation uncertainty
    fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
    fSys[i][1].type = MULT;
    fSys[i][1].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    double nuclear;
    nstream >> sdum >> sdum >> idum >> ddum >> nuclear;
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - nuclear)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "NUCLEAR" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }

    //Compute shifts
    //cout << nuclear/proton_cv << "   " << 0.0 << endl;   

  }
  
  f1.close();
  f2.close();
  f3.close();
  
}

void DYE605_dw_iteFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE605/dy-e605.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE605/nuclear/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE605/proton_ite/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }

  // Starting filter
  double convfact = 1e33;
  double SCM = 38.8*38.8;
  int nrep=1000;
  int nrealsys=2;
  
  string line;
  double sqrttau;

  getline(f2,line);
  getline(f3,line);
  
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    
    lstream >> sqrttau;
    // Instead of sqrttau, save M2 as second kinematical variable using
    // M2 = taus * S
    fKin2[i] = sqrttau*sqrttau*SCM;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    fData[i]*= convfact;     // Convert from cm2 to pb
    
    lstream >> fStat[i];     // stat
    fStat[i]*= convfact;     // Convert from cm2 to pb
    
    fSys[i][0].mult = 10.0;   // 10% uncorrelated systematic
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "UNCORR";
    
    fSys[i][1].mult = 15.0;         // 15% normalisation uncertainty
    fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
    fSys[i][1].type = MULT;
    fSys[i][1].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    nstream >> sdum >> sdum >> idum >> ddum >> ddum;
    
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - proton_cv)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "NUCLEAR" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }
  }
  
  f1.close();
  f2.close();
  f3.close();
  
}

void DYE605_sh_iteFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE605/dy-e605.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE605/nuclear/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE605/proton_ite/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }

  // Starting filter
  double convfact = 1e33;
  double SCM = 38.8*38.8;
  int nrep=1000;
  int nrealsys=2;
  
  string line;
  double sqrttau;

  getline(f2,line);
  getline(f3,line);
  
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    
    lstream >> sqrttau;
    // Instead of sqrttau, save M2 as second kinematical variable using
    // M2 = taus * S
    fKin2[i] = sqrttau*sqrttau*SCM;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    fData[i]*= convfact;     // Convert from cm2 to pb
    
    lstream >> fStat[i];     // stat
    fStat[i]*= convfact;     // Convert from cm2 to pb
    
    fSys[i][0].mult = 10.0;   // 10% uncorrelated systematic
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "UNCORR";
    
    fSys[i][1].mult = 15.0;         // 15% normalisation uncertainty
    fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
    fSys[i][1].type = MULT;
    fSys[i][1].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    double nuclear;
    nstream >> sdum >> sdum >> idum >> ddum >> nuclear;
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - nuclear)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "NUCLEAR" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }

    //Compute shifts
    //cout << nuclear/proton_cv << "   " << 0.0 << endl;   

  }
  
  f1.close();
  f2.close();
  f3.close();
  
}

/**
 *     Drell-Yan experiment E886 ---- Also known as NuSea
 *
 *     Here we read the data converted from d\sigma/dx_F/dM to d\sigma/dYdM
 * ----------------------------------------------
 *
 *     2001 data
 *
 *     Data on the ratio of pd DY cross sections over pp cross sections
 *     "Improved measurement of the anti-d / anti-u asymmetry
 *     in the nucleon sea"
 *     Published in Phys.Rev.D64:052002,2001.
 *     e-Print: hep-ex/0103030
 *
 *     The dimesionless ratio ( sigma^pd / 2*sigma^pp ) is given
 *     as 15 points in different bins with average <xF> and <M>
 *     In this case the number of kinematical variables is three,
 *     <xF>, <M>, <x2>
 *     Although in principle one could related x2 to xF and M by leading
 *     order kinematics, it is safer to use the same values as those
 *     of kinematical data
 *
 *     The converted experimental data can be found in
 *
 *     data/dy-E886/dy-e886-rat-2001-y.data
 *
 *     with format
 *
 *     <Y>  <x2>  <M> [GeV]  sigma^pd/(2*sigma^pp) stat (abs) sys (abs)
 *
 * ----------------------------------------------
 *
 *     2003 data
 *
 *     These data sets consists on measurements of the double differential cross section
 *     (M**3)*D2(SIG)/DM/DxF as a function of the invariant mass
 *     of the DY pair M and the XF kinematical variable
 *
 *     The units are in  NB*GEV**2/NUCLEON
 *
 *     "Absolute Drell-Yan dimuon cross-sections in 800 GeV / c pp and pd collisions"
 *     By NuSea Collaboration (J.C. Webb et al.).
 *     FERMILAB-PUB-03-302-E, Feb 2003. 5pp.
 *     e-Print: hep-ex/0302019
 *
 *     The 2003 publication consists of two sets of measurements,
 *     one on an hidrogen target and the other in a deuterium target
 *
 *     Data in file:
 *     data/dy-E886/dy-e886-2003-y.data
 *
 *     The point-to-point systematic uncertainties are correlated
 *     between the pp and the pd samples
 *
 *     The is an additional 6.5% normalization uncertainty, associated
 *     to the calibration of the beam intensity
 *
 *     The format of the data is
 *     --> proton and deuteron
 *     do I=1,fNData
 *        Y  M d2sigma/dM/dY  stat (abs)  sys (abs)
 *     enddo
 *     --> ratio
 *     do I=1,fNData
 *        Y  x2  M d2sigma/dM/dY  stat (abs)  sys (abs)
 *     enddo
 */
void DYE866PFilter::ReadData()
{
  // Opening files
  fstream f1;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/dy-e886-2003-y.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }
   
  // Starting filter
  string line;
  double m;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    
    lstream >> m;
    // Instead of M, save M2 as second kinematical variable using
    fKin2[i] = m*m;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    
    lstream >> fStat[i];     // stat
    fStat[i]*= fData[i]*1e-2;
    
    lstream >> fSys[i][0].mult;    // Uncorrelated sys
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "UNCORR";
    
    fSys[i][1].mult = 6.5;         // 6.5% normalisation uncertainty
    fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
    fSys[i][1].type = MULT;
    fSys[i][1].name = "CORR";
  }
  
  f1.close();  
}


/**
 * See doc filterDYE866P()
 */
void DYE866RFilter::ReadData()
{
  // Opening files
  fstream f1;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/dy-e886-rat-2001-y.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }
  
  // Starting filter
  string line;
  double m, tmp;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    lstream >> tmp;        // x2
    lstream >> m;
    // Instead of M, save M2 as second kinematical variable using
    fKin2[i] = m*m;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    
    lstream >> fStat[i];     // stat
    fStat[i]*= fData[i]*1e-2;

    lstream >> fSys[i][0].mult;  //sys
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "CORR";
  }
  
  f1.close();
}

void DYE866R_dwFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE886R/dy-e886-rat-2001-y.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE886R/nuclear/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE886R/proton/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }
  
  // Starting filter
  int nrep=100;
  int nrealsys=1;
  
  string line;
  getline(f2,line);
  getline(f3,line);
  double m, tmp;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    lstream >> tmp;        // x2
    lstream >> m;
    // Instead of M, save M2 as second kinematical variable using
    fKin2[i] = m*m;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    
    lstream >> fStat[i];     // stat
    fStat[i]*= fData[i]*1e-2;

    lstream >> fSys[i][0].mult;  //sys
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    nstream >> sdum >> sdum >> idum >> ddum >> ddum;
    
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - proton_cv)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "DEUTERON" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }
    
  }
  
  f1.close();
  f2.close();
  f3.close();
}

void DYE866R_shFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE886R/dy-e886-rat-2001-y.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE886R/nuclear/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE886R/proton/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }
  
  // Starting filter
  int nrep=100;
  int nrealsys=1;
  
  string line;
  getline(f2,line);
  getline(f3,line);
  double m, tmp;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    lstream >> tmp;        // x2
    lstream >> m;
    // Instead of M, save M2 as second kinematical variable using
    fKin2[i] = m*m;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    
    lstream >> fStat[i];     // stat
    fStat[i]*= fData[i]*1e-2;

    lstream >> fSys[i][0].mult;  //sys
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    double nuclear;
    nstream >> sdum >> sdum >> idum >> ddum >> nuclear;
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - nuclear)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "DEUTERON" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }
    
    //Compute shifts
    //cout << nuclear/proton_cv << "   " << 0.0 << endl;
    
  }
  
  f1.close();
  f2.close();
  f3.close();
}

void DYE866R_dw_iteFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE886R/dy-e886-rat-2001-y.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE886R/nuclear_ite/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE886R/proton_ite/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }
  
  // Starting filter
  int nrep=100;
  int nrealsys=1;
  
  string line;
  getline(f2,line);
  getline(f3,line);
  double m, tmp;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    lstream >> tmp;        // x2
    lstream >> m;
    // Instead of M, save M2 as second kinematical variable using
    fKin2[i] = m*m;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    
    lstream >> fStat[i];     // stat
    fStat[i]*= fData[i]*1e-2;

    lstream >> fSys[i][0].mult;  //sys
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    nstream >> sdum >> sdum >> idum >> ddum >> ddum;
    
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - proton_cv)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "DEUTERON" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }
    
  }
  
  f1.close();
  f2.close();
  f3.close();
}

void DYE866R_sh_iteFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/DYE886R/dy-e886-rat-2001-y.data";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream nuclearfile("");
  nuclearfile << dataPath() << "rawdata/DYE886R/nuclear_ite/output/tables/group_result_table.csv";
  f2.open(nuclearfile.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << nuclearfile.str() << endl;
    exit(-1);
  }
  
  stringstream protonfile("");
  protonfile << dataPath() << "rawdata/DYE886R/proton_ite/output/tables/group_result_table.csv";
  f3.open(protonfile.str().c_str(), ios::in);
  
  if (f3.fail()) {
    cerr << "Error opening data file " << protonfile.str() << endl;
    exit(-1);
  }
  
  // Starting filter
  int nrep=100;
  int nrealsys=1;
  
  string line;
  getline(f2,line);
  getline(f3,line);
  double m, tmp;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin1[i];   // y
    lstream >> tmp;        // x2
    lstream >> m;
    // Instead of M, save M2 as second kinematical variable using
    fKin2[i] = m*m;
    
    fKin3[i] = 38.8;   //s
    
    lstream >> fData[i];
    
    lstream >> fStat[i];     // stat
    fStat[i]*= fData[i]*1e-2;

    lstream >> fSys[i][0].mult;  //sys
    fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "CORR";

    //Get proton central value
    getline(f3,line);
    istringstream pstream(line);
    string sdum;
    int idum;
    double ddum;
    double proton_cv;
    pstream >> sdum >> sdum >> idum >> ddum >> proton_cv;
    
    //Get nuclear replicas
    getline(f2,line);
    istringstream nstream(line);
    double nuclear;
    nstream >> sdum >> sdum >> idum >> ddum >> nuclear;
    vector<double> nuclear_cv (nrep);
      
    for(int irep=0; irep<nrep; irep++)
      {
	nstream >> nuclear_cv[irep];
      }

    //Compute additional uncertainties
    for(int l=nrealsys; l<fNSys; l++)
      {
	fSys[i][l].add = (nuclear_cv[l-nrealsys] - nuclear)/sqrt(nrep);
	fSys[i][l].mult = fSys[i][l].add*100/fData[i];
	fSys[i][l].type = ADD;
	ostringstream sysname;
	sysname << "DEUTERON" << l-nrealsys;
	fSys[i][l].name = sysname.str();
      }
    
    //Compute shifts
    //cout << nuclear/proton_cv << "   " << 0.0 << endl;
    
  }
  
  f1.close();
  f2.close();
  f3.close();
}

/**
 * Drell Yan experiment E906/SeaQuest
 * 
 * Name_exp  : E906
 * Reference : The Asymmetry of Antimatter in the Proton
 * ArXiv     : 2103.04024
 * Published : Nature volume 590, pages 561–565(2021)
 * Hepdata   : n/a 
 * Dimesionless ratio between DY cross sections with hydrogen and deuterium targets ( sigma^pd / 2*sigma^pp ) is given
 * as 6 points in different bins with average <xt>, <xb>, <M> and <PT> (Bjorken-x of the target/beam, invarinat mass and 
 * transverse momentum of the DY pair). The data have been collected with a proton beam at an energy of 120 GeV.
 * The data are stored in rawdata/DTE906/data_paper.dat, according to the original format as in the paper.
 * In rawdata/DTE906/prefilter.py they are converted in data for the distribution
 * differential in hadronic rapidity and invariant mass, using Eqs. (4.6),(4.7) of https://arxiv.org/pdf/1009.5691.pdf.
 * The converted data are saved in the file rawdata/DTE906/data_E906.dat, which is read in the c++ filter.  
 * 
 * Implemented by TG March 2021
 **/

void DYE906RFilter::ReadData()
{
  //Opening files
  fstream f1;
  
  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/data_E906.dat";
  f1.open(datafile.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }
  
  //Starting filter
  string line;
  double M, dum;
  for (int i = 0; i < fNData; i++)
  {
    getline(f1,line);
    istringstream lstream(line);
    
    lstream >> fKin3[i]; //sqrt(s), 17.37 GeV 
    lstream >> fKin1[i]; //Y
    lstream >> dum; //xt
    lstream >> M;
    fKin2[i] = M*M; //Invariant mass square
        
    lstream >> fData[i];  
    lstream >> fStat[i]; //stat
    
    lstream >> fSys[i][0].add;  //sys
    fSys[i][0].mult = fSys[i][0].add/fData[i]*1e2;
    fSys[i][0].type = ADD;
    fSys[i][0].name = "CORR";
  }
  
  f1.close();
}
