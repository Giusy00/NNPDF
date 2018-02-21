# buildmaster

The `buildmaster` project provides a systematic mechanism to convert
experimental data provided in various formats into a standard (or *master*)
version in the NNPDF CommonData format.

## Dependencies and compilation

`buildmaster` depends on:

- NNPDF/nnpdf
- yaml-cpp
- gsl

(Note that both yaml-cpp and gsl are also dependencies of NNPDF/nnpdf).

In order to compile just type `make`.

## Running the code

In order to generate a master copy of all experimental data run the
`buildmaster` program. This program will create for each dataset:
- DATA_[setname].dat are generated and placed in the results folder
- SYSTYPE_[setname]_DEFAULT.dat are generated and placed in results/systypes
After generating these files the user can copy them to the `nnpdfcpp/data/commondata` folder.


## Implementing new datasets

In order to implement a new dataset the developer has to:

1. Create input files in `rawdata/<exp>`, where `<exp>` is the name of
the new dataset and must coincide with the `apfelcomb` and `applgrid`
definitions. The input files are raw data files obtained from papers
(copy/paste) or from the HEPDATA website. The user has the freedom to
select his preferred format, but csv or plain text are the recommended
formats.

2. Create a metadata file in `meta` in yaml with the format
```yaml
# DATASET.yaml
ndata:    <number of datapoints>
nsys:     <number of systematic errors>
setname:  <setname in double quotes, i.e "ATLAS1JET11">
proctype: <process type (see nnpdfcpp/doc) in double quotes i.e "JET")
```

3. Create a new class with the dataset name in `inc` (*.h) and
`filters` (*.cc) following the patter of other datasets, i.e. in the
header create a new class which inherits from `CommonData`:
```c++
class MY_NEW_DATASET_CLASSFilter: public CommonData {
public: MY_NEW_DATASET_CLASSFilter("MY_NEW_DATASET_NAME") { ReadData(); }
private:
	void ReadData();
}
```
in the C++ file you implement the `void ReadData()` method.

4. The previous class must read from rawdata all the required
information about the data, and fill the attributes of the CommonData
class in `libnnpdf`. The required entries are:
- the kinematic information: fKin1, fKin2, fKin3
- the data: fData
- the statistical uncer.: fStat
- the systematic uncer.: fSys

5. Edit `src/buildmaster.cc` by including the header file of the new
dataset and by pushing back to the `target` object a new instance of
the class created in step 2. Namely:
```c++
target.push_back(new MY_NEW_DATASET_CLASSFilter());
```

## Code development policy/rules

Developers must never commit code structure modifications to master. The development pattern should follow these rules:
- Open an issue explaining your bug or feature request. If you report a bug, post information to reproduce it.
- The resolution of issues must be performed in a new branch through a pull request.
- If you have a local version of the code that you would like to merge in the master, open a pull request.
- The pull request must be reviewed by at least 2 core developers.

## File format documentation

For specifications about data file formats please check the `nnpdf` repository in `nnpdfcpp/data/doc`.

