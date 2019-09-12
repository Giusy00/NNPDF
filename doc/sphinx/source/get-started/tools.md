# Tools, or  "What does any of this have to do with apples?"

*Author: Cameron Voisey, 12/10/2019*

There are many ingredients that go into a PDF fit. For example, one must generate the partonic cross sections for use in the fit, convert these predictions into a format that is suitable for PDF fits, i.e. the format must be suitable for on-the-fly convolutions, and evolve the PDFs according to the DGLAP equations. To perform each of these steps, different codes are used. In this subsection various codes that you will frequently encounter are described.  

## NNPDF specific codes

validphys and reportengine are two internal NNPDF codes that form the basis of much of the work that NNPDF does. To read about what validphys and reportengine are and what they do, please refer to the introductory section of the [vp-guide](./../vp/introduction.md).

## PDF set storage and interpolation

[LHAPDF](https://lhapdf.hepforge.org/) is a C++ library that evaluates PDFs by intepolating the discretised PDF 'grids' that PDF collaborations produce. It also gives its users access to proton and nuclear PDF sets from a variety of PDF collaborations, including NNPDF, MMHT and CTEQ. A list of all currently available PDF sets can be found on their [website](https://lhapdf.hepforge.org/pdfsets.html). Particle physics programmes that typically make use of PDFs, such as Monte Carlo event generators, will usually be interfaced with LHAPDF, to allow a user to easily specify the PDF set that they wish to use in their calculations. You can read more about LHAPDF by reading the [paper](https://arxiv.org/abs/1412.7420) that marked their latest release.

## Partonic cross section generation

Many programmes exist to evaluate partonic cross sections (otherwise known as hard cross sections or matrix elements). Some are general purpose, such as MadGraph5\_aMC@NLO and MCFM, in that they compute predictions for a variety of physical processes (e.g. drell-yan and single top production) up to a given order. Others are more specific, such as top++, which makes predictions for a single process. In the case of top++, this is top quark pair production. Some of these programmes will be briefly outlined here. Note that to produce predictions at NNLO in QCD, which is the highest order used in NNPDF fits, one usually produces APPLgrids at NLO in QCD (and potentially NLO in EW), and then supplements these with NNLO QCD corrections which are computed with a code with NNLO capabilities. These C-factors are often provided to the collaboration by external parties, rather than the code being run in-house.

Many programmes exist to evaluate partonic cross sections (otherwise known as hard cross sections or matrix elements). Some are general purpose, such as MadGraph5\_aMC@NLO and MCFM, in that they compute predictions for a variety of physical processes (e.g. drell-yan and single top production) up to a given order (typically next-to-leading order (NLO) in QCD, with some also computing NLO electroweak (EW) corrections). Others are more specific, such as top++, which makes predictions for top quark pair production up to next-to-next-to-leading order (NNLO). Some of these programmes will be briefly outlined here. Note that to produce predictions at NNLO in QCD, which is the highest order used in NNPDF fits, one usually produces APPLgrids at NLO in QCD (and potentially NLO in EW), and then supplements these with NNLO QCD corrections which are computed with a code with NNLO capabilities. These C-factors are often provided to the collaboration by external parties, rather than the code being run in-house.

[MadGraph5\_aMC@NLO](https://launchpad.net/mg5amcnlo) is the programme that will be used for most of the future NNPDF calculations of matrix elements. This is in large part due to its ability to compute predictions at NLO in QCD with NLO EW corrections. To generate APPLgrids from MadGraph5\_aMC@NLO, one can use [aMCfast](https://amcfast.hepforge.org/), which interfaces between the two formats.

### Other codes

[MCFM](https://mcfm.fnal.gov/) ('Monte Carlo for FeMtobarn processes') is an alternative programme to MadGraph5\_aMC@NLO, which instead uses mcfm-bridge as an interface to generate APPLgrids.

[FEWZ](https://arxiv.org/abs/1011.3540) ('Fully Exclusive W and Z Production') is a programme for calculating (differential) cross sections for the Drell-Yan production of lepton pairs up to NNLO in QCD.

[NLOjet++](http://www.desy.de/~znagy/Site/NLOJet++.html) is a programme that can compute cross sections for a variety of processes up to NLO. The processes include electon-positron annihilation, deep-inelastic scattering (DIS), photoproduction in electron-proton collisions, and a variety of processes in hadron-hadron collisions.

[Top++](http://www.precision.hep.phy.cam.ac.uk/top-plus-plus/) is a programme for computing top quark pair production inclusive cross sections at NNLO in QCD with soft gluon resummation inluded up to next-to-next-to-leading log (NNLL).

## PDF evolution

[APFEL](https://apfel.hepforge.org/) ('A PDF Evolution Library') is the PDF evolution code currently used by the NNPDF Collaboration. In addition to its PDF evolution capabilities, it also produces predictions of deep-inelastic scattering structure functions. In recent years it has been developed along with NNPDF, and so it therefore contains the features and settings required in an NNPDF fit. That is, it includes quark masses in the MSbar scheme, the various FONLL heavy quark schemes, scale variations up to NLO, etc. Note that at the time of writing, a more streamlined code is being written to replace APFEL, which is currently dubbed EKO ('Evolution Kernel Operator').

### Other codes

[Hoppet](https://hoppet.hepforge.org/) ('Higher Order Perturbative Parton Evolution Toolkit') is an alternative PDF evolution code which is capable of evolving unpolarised PDFs to NNLO and linearly polarised PDFs to NLO. The unpolarised evolution includes heavy-quark thresholds in the MSbar scheme.

## Grid generation

Grids play a crucial role in NNPDF fits. This is because they enable otherwise very time consuming computations to be computed on the fly during an NNPDF fit. The guiding principle behind producing grids is that the maximum possible amount of information should be computed before a PDF fit, so that the smallest possible number of operations has to be carried out during a fit. There are two particularly important types of grid: APPLgrids and FK tables.

[APPLgrid](https://applgrid.hepforge.org/) is a C++ programme that allows the user to change certain settings within observable calculations a posteriori. Most importantly, the user can change the PDF set used, but they can also alter the renormalisation scale, factorisation scale and the strong coupling constant. Without APPLgrids, such changes would usually require a full rerun of the code, which is very costly in terms of time. Moreover, these features are crucial for PDF fits, where hard cross sections must be convoluted with different PDFs many times on the fly. APPLgrid works for hadron collider processes up to NLO in QCD, although work is ongoing to also include NLO EW corrections in the APPLgrid format. In addition the standard version of APPLgrid, a modified version of APPLgrid exists which includes photon channels. This is known as APPLgridphoton. To learn how to generate APPLgrids, please see the tutorial [here](../tutorials/APPLgrids.md).

APFELcomb generates FK (or 'Fast Kernel') tables for NNPDF fits. FK tables are APPLgrids combined with DGLAP evolution kernels. This therefore means that FK tables can be multiplied with PDFs at the fitting scale to produce predictions for observables.

#### Other codes

[fastNLO](https://fastnlo.hepforge.org/) is an alternative code to APPLgrid, which is currently not used by NNPDF, since the grids produced by fastNLO are not interfaced with the NNPDF code.

Discuss interface codes?
