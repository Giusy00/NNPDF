// $Id$
//
// NNPDF++ 2012-2015
//
// Authors: Nathan Hartland,  n.p.hartland@ed.ac.uk
//          Stefano Carrazza, stefano.carrazza@mi.infn.it
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <sys/stat.h>
#include "evolgrid.h"
#include "exportgrid.h"
#include <NNPDF/pdfset.h>
#include <NNPDF/utils.h>
#include <NNPDF/exceptions.h>
#include <APFEL/APFEL.h>
#include <APFEL/APFELdev.h>

using namespace NNPDF;
using namespace std;

//______________________________________________________
vector<double> generate_q2grid(const int nq2,
                               const double q2min,
                               const double q2max,
                               const double lambda2)
{
    vector<double> q2grid;
    const double tau_min   = log( log( q2min / lambda2 ));
    const double tau_max   = log( log( q2max / lambda2 ));
    const double delta_tau = (tau_max - tau_min) /( (double) nq2 - 1);

    for (int iq2 = 0; iq2 < nq2; iq2++)
        q2grid.push_back(lambda2 * exp(exp( tau_min + iq2*delta_tau)));
    return q2grid;
}

//______________________________________________________
vector< vector<double> > generate_q2subgrids( const int nq2,
        const double q2min, const double q2max)
{
    const double eps     = 1E-4;
    const double lambda2 = 0.0625e0;
    const int nfpdf = APFEL::GetMaxFlavourPDFs();

    const std::array<double, 3> hqth = {{
        pow(APFEL::GetThreshold(4),2),
        pow(APFEL::GetThreshold(5),2),
        pow(APFEL::GetThreshold(6),2),
    }};

    // Determine subgrid edges
    vector<double> subgrid_edges={q2min};
    for (int i=0; i<(nfpdf-3); i++)
        if (hqth[i] > q2min) subgrid_edges.push_back(hqth[i]);
    subgrid_edges.push_back(q2max);

    // Determine point distribution across subgrids and generate subgrids
    const std::vector<double> point_dist = generate_q2grid(nq2, q2min, q2max, lambda2);
    std::vector<vector<double>> q2grid_subgrids;
    for (size_t i=0; i<subgrid_edges.size()-1; i++)
    {
        const double min_edge = subgrid_edges[i];
        const double max_edge = subgrid_edges[i+1];
        auto in_sub = [=](double q2pt){return (q2pt - min_edge) > -eps && (q2pt - max_edge) < eps;};
        const int npoints_sub = std::count_if(point_dist.begin(), point_dist.end(), in_sub);

        if (npoints_sub < 2)
            throw std::runtime_error("Too few points to sufficiently populate subgrids. More Q points required");

        const vector< double > subgrid = generate_q2grid(npoints_sub, min_edge, max_edge, lambda2);
        q2grid_subgrids.push_back(subgrid);
    }

    return q2grid_subgrids;
}

//______________________________________________________
EvolveGrid::EvolveGrid(ExportGrid const& initialscale_grid,
                       map<string, string> const& theory):
  fnq2(50),
  fq2min(pow(atof(theory.at("Q0").c_str()),2)),
  fq2max(1E5*1E5),
  finitialscale_grid(initialscale_grid)
{
  const auto xg = initialscale_grid.GetXGrid();
  cout << "- Initialising evolution with " + std::to_string(xg.size()) + " x-points" << endl;

  // Initialize APFEL
  APFEL::SetParam(theory);

  // Fetch initial-scale x-grid
  APFEL::SetNumberOfGrids(1);
  APFEL::SetExternalGrid(1, xg.size()-1, 3, (double*) xg.data());

  // General settings
  APFEL::SetQLimits(sqrt(fq2min), sqrt(fq2max));
  APFEL::SetFastEvolution(false);
  APFEL::EnableEvolutionOperator(true);

  APFEL::InitializeAPFEL();
}

//______________________________________________________
void EvolveGrid::WriteInfoFile(const string infofile) const
{
  // skip if file exists
  struct stat s;
  stringstream infodata;
  if(stat(infofile.c_str(), &s) == 0 && S_ISREG(s.st_mode))
    {
      cout << "- LHAPDF info already exported: " << infofile << endl;
      return;
    }
  else
    cout << "- Exporting LHAPDF info file: " << infofile << endl;

  // LHAPDF6 HEADER
  const auto xg = finitialscale_grid.GetXGrid();
  const auto q2subgrids = generate_q2subgrids(fnq2, fq2min, fq2max);

  infodata << "SetDesc: \"NNPDF x.x\"" << endl;
  infodata << "SetIndex: " << endl;
  infodata << "Authors: NNPDF Collaboration." << endl;
  infodata << "Reference: arXiv:xxxx.xxxxxx" << endl;
  infodata << "Format: lhagrid1" << endl;
  infodata << "DataVersion: 1" << endl;
  infodata << "NumMembers: REPLACE_NREP" << endl;
  infodata << "Particle: 2212" << endl;
  infodata << "Flavors: [-6, -5, -4, -3, -2, -1, 21, 1, 2, 3, 4, 5, 6, 22]" << endl;
  infodata << "OrderQCD: " << APFEL::GetPerturbativeOrder() << endl;
  infodata << "FlavorScheme: variable" << endl;
  infodata << "NumFlavors: " << std::max(APFEL::GetMaxFlavourPDFs(), APFEL::GetMaxFlavourAlpha()) << endl;
  infodata << "ErrorType: replicas" << endl;

  infodata.precision(7);
  infodata << scientific;
  infodata << "XMin: "<< xg[0] << endl;
  infodata << "XMax: "<< xg.back() << endl;
  infodata << "QMin: "<< sqrt(fq2min) << endl;
  infodata << "QMax: "<< sqrt(fq2max) << endl;
  infodata << "MZ: "  << APFEL::GetZMass() << endl;
  infodata << "MUp: 0\nMDown: 0\nMStrange: 0" << std::endl;
  infodata << "MCharm: "  << APFEL::GetThreshold(4) << endl;
  infodata << "MBottom: " << APFEL::GetThreshold(5) << endl;
  infodata << "MTop: "    << APFEL::GetThreshold(6) << endl;
  infodata << fixed << "AlphaS_MZ: " << APFEL::AlphaQCD(APFEL::GetZMass()) << endl;
  infodata << scientific;
  infodata << "AlphaS_OrderQCD: " << APFEL::GetPerturbativeOrder() << endl;
  infodata << "AlphaS_Type: ipol" << endl;
  infodata << "AlphaS_Qs: [";

  for (int s = 0; s < (int) q2subgrids.size(); s++)
    for (int iq = 0; iq < (int) q2subgrids[s].size(); iq++)
      infodata << sqrt(q2subgrids[s][iq]) << ((s == (int) q2subgrids.size()-1 && iq == (int) q2subgrids[s].size()-1) ? "]\n" : ", ");

  infodata << "AlphaS_Vals: [";
  for (int s = 0; s < (int) q2subgrids.size(); s++)
    for (int iq = 0; iq < (int) q2subgrids[s].size(); iq++)
      infodata << APFEL::AlphaQCD(sqrt(q2subgrids[s][iq])) << ((s == (int) q2subgrids.size()-1 && iq == (int) q2subgrids[s].size()-1) ? "]\n" : ", ");

  infodata << "AlphaS_Lambda4: 0.342207" << endl;
  infodata << "AlphaS_Lambda5: 0.239" << endl;
  write_to_file(infofile, infodata.str());
}

//______________________________________________________
void EvolveGrid::WriteLHAFile(const string replica_file) const
{
  cout << "- Writing out LHAPDF file: " << replica_file << endl;
  // Setup stringstreams for LHgrid writing

  stringstream outstream;
  outstream << scientific << setprecision(7);
  outstream << "PdfType: replica\nFormat: lhagrid1\nFromMCReplica: " << finitialscale_grid.GetReplica() << "\n---" << std::endl;

  // compute q2 subgrids
  const auto xg = finitialscale_grid.GetXGrid();
  const auto q2subgrids = generate_q2subgrids(fnq2, fq2min, fq2max);
  for (auto subgrid: q2subgrids)
    {
      // Print out x-grid
      for ( auto x : xg )
        outstream << x << " ";
      outstream << std::endl;

      // Print out q2-grid
      for ( auto q2val : subgrid )
        outstream << sqrt(q2val) << " ";
      outstream << std::endl;

      // Print out final-state PIDs
      // Currently prints out all flavours
      const array<int, 14> pids = {-6, -5, -4, -3, -2, -1, 21, 1, 2, 3, 4, 5, 6, 22};
      for ( auto fl : pids )
        outstream << fl << " ";
      outstream << std::endl;

      // Compute Evolution Operators
      // Ordered evol_op[q][ox][ofl][ix][ifl]
      // This is a big array
      const int evol_op_size = subgrid.size()*xg.size()*xg.size()*14*14;
      vector<double> evol_op(evol_op_size, std::numeric_limits<double>::signaling_NaN());

      for ( size_t iq = 0; iq < subgrid.size(); iq++ )
        {
          const double qi = sqrt(fq2min);
          const double qt = sqrt(subgrid[iq]);

          std::cout << " Qi = " << qi << " -> Qt = " << qt << " GeV" << std::endl;
          std::cout << "-------------------------"<<std::endl;

          if ( fabs(qi - qt ) < 1E-5 )
            APFEL::EvolveAPFEL(qi,qi);
          else
            APFEL::EvolveAPFEL(qi,qt);

          for(int ix_out = 0; ix_out < (int) xg.size(); ix_out++)
            for(int if_out = 0; if_out < 14;        if_out++) // These can be optimised, don't always need 14 flavours
              for( int if_in = 0; if_in  < 14;        if_in++ )
                for( int ix_in = 0; ix_in  < (int) xg.size(); ix_in++ ) // This can be optimised, should start from ix_in = ix_out and above
                  {
                     const int index = ix_in + if_in*xg.size() + if_out*xg.size()*14 + ix_out*xg.size()*14*14 + iq*xg.size()*xg.size()*14*14;
                     evol_op[index] = APFEL::ExternalEvolutionMatrixPh2Ph(if_out-6, if_in-6, ix_out, ix_in);
                  }
        }

      for (int i=0; i<evol_op_size; i++)
        if (isnan(evol_op[i]))
          throw NNPDF::RuntimeException("EvolveGrid::WriteLHAFile", "Evolution operator is NAN.");

      // Evolve and write to file
      for(int ix_out = 0; ix_out < (int) xg.size(); ix_out++)
        for(size_t iq = 0; iq < subgrid.size(); iq++ )
        {
            // New line in LHAgrid
            outstream << " ";
            for(int if_out=0; if_out<14; if_out++)
            {
                double evolved_pdf = 0;
                for(int if_in = 0; if_in < 14; if_in++)
                  for(int ix_in = 0; ix_in < (int) xg.size(); ix_in++) // ix_in = ix_out
                  {
                      const int index = ix_in + if_in*xg.size() + if_out*xg.size()*14 + ix_out*xg.size()*14*14 + iq*xg.size()*xg.size()*14*14;
                      evolved_pdf += evol_op[index] * finitialscale_grid.GetPDF(ix_in, if_in);
                  }
                outstream << std::setw(14) << evolved_pdf;
            }
            // End of LHAgrid line
            outstream <<std::endl;
        }

      // Terminate each subgrid
      outstream << "---" << std::endl;
    }
  // Terminate each subgrid
  write_to_file(replica_file, outstream.str());
}
