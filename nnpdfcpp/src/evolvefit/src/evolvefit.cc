// $Id$
//
// NNPDF++ 2016
//
// Authors: Nathan Hartland,  n.p.hartland@ed.ac.uk
//          Stefano Carrazza, stefano.carrazza@mi.infn.it

#include <string>
#include <iomanip>
#include "common.h"
#include "nnpdfsettings.h"
#include "exportgrid.h"
#include "evolgrid.h"
#include <sys/stat.h>
using namespace NNPDF;
using std::cout;
using std::endl;
using std::cerr;
using std::string;
using std::stoi;

// Create cascade of folders for output
void CreateResultsFolder(const NNPDFSettings &settings, const int theory_id)
{
  stringstream folder("");
  folder << settings.GetResultsDirectory() << "/evolvefit";
  int status = mkdir(folder.str().c_str(), 0777);
  if (status == -1 && errno != EEXIST)
    throw FileError("CreateResultsFolder", "Cannot create folder " + folder.str());
  folder << "/theory_" << theory_id << "-" << settings.GetPDFName();
  status = mkdir(folder.str().c_str(), 0777);
  if (status == -1 && errno != EEXIST)
    throw FileError("CreateResultsFolder", "Cannot create folder " + folder.str());
}

// Check if folder exists
bool CheckFolderExists(string const& folder)
{
  bool status = false;
  struct stat s;
  if (stat(folder.c_str(), &s) == 0)
    if (s.st_mode & S_IFDIR)
        status = true;
  return status;
}

// Compute average array
vector<array<double,14>> ComputeAVGPDFgrid(vector<vector<array<double,14>>> eg)
{
  vector<array<double,14>> result(eg[0].size(), array<double,14>{});
  for (size_t row = 0; row < eg[0].size(); row++)
    for (size_t rep = 0; rep < eg.size(); rep++)
      for (size_t fl = 0; fl < 14; fl++)
        result[row][fl] += eg[rep][row][fl]/eg.size();
  return result;
}

int main(int argc, char **argv)
{
  // Read configuration filename from arguments
  if (argc != 3)
    {
      cerr << Colour::FG_RED << "\nusage: evolvefit [configuration folder] [theoryid]\n" << Colour::FG_DEFAULT << endl;
      exit(EXIT_FAILURE);
    }

  const string fit_path = argv[1];
  const int theory_id = stoi(argv[2]);

  // load settings from config folder
  NNPDFSettings settings(fit_path);

  // check if user is not doing something stupid...
  if (theory_id == stoi(settings.GetTheory("ID")))
    throw NNPDF::RuntimeException("main", "Same theory ID for the original fit and this evolvefit run.");

  // load theory from db
  std::map<string,string> theory_map;
  NNPDF::IndexDB db(get_data_path() + "/theory.db", "theoryIndex");
  db.ExtractMap(theory_id, APFEL::kValues, theory_map);

  // create output folder
  CreateResultsFolder(settings, theory_id);

  // load grids
  vector<ExportGrid> initialscale_grids;
  int nrep;
  for (nrep = 0;; nrep++)
    {
      const string folder = fit_path + "/postfit/replica_" + std::to_string(nrep+1);
      bool status = CheckFolderExists(folder);
      if (status)
        {
          const string path = folder + "/" + settings.GetPDFName() + ".exportgrid";
          cout << "- Reading exportgrid: " << path << endl;
          initialscale_grids.emplace_back(path);

          // take first replica and duplicate entry, we will use it as baseline for replica 0
          if (nrep == 0)
            initialscale_grids.emplace_back(path);
        }
      else
        break;
    }
  cout << "- Detected " << nrep << " replicas (contiguous)." << endl;
  
  if (nrep == 0)
      throw NNPDF::RuntimeException("main", "nrep = 0, check replica folder/files.");

  // compute avg over pdfgrid and set to replica 0 - if someone has a better idea let me know
  vector<vector<array<double,14>>> pdfgridvectors(initialscale_grids.size()-1);
  for (size_t i = 0; i < pdfgridvectors.size(); i++)
    pdfgridvectors[i] = initialscale_grids[i+1].GetPDFgrid();
  const auto rep0pgrid = ComputeAVGPDFgrid(pdfgridvectors);

  // replace content of replica 0
  initialscale_grids[0].SetPDFgrid(rep0pgrid);

  string infofile = fit_path + "/evolvefit/theory_" + std::to_string(theory_id)
                  + "-" + settings.GetPDFName() + "/" + settings.GetPDFName() + ".info";
  auto dglapg = EvolveGrid(initialscale_grids, theory_map);
  dglapg.WriteInfoFile(infofile, initialscale_grids.size());

  const auto outstream = dglapg.WriteLHAFile();
  for (size_t i = 0; i < outstream.size(); i++)
    {
      stringstream replica_file;
      replica_file << fit_path
                   << "/evolvefit/theory_" << theory_id
                   << "-" << settings.GetPDFName()
                   << "/" << settings.GetPDFName() << "_"
                   << std::setfill('0') << std::setw(4) << i << ".dat";
      write_to_file(replica_file.str(), outstream[i].str());
    }

  return 0;
}
