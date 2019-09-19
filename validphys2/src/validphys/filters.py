# -*- coding: utf-8 -*-
"""
Filters for NNPDF fits
"""

import logging
import numbers
import numpy as np

from NNPDF import DataSet, RandomGenerator, CommonData
from reportengine.checks import make_argcheck, check, check_positive, make_check
from reportengine.compat import yaml

log = logging.getLogger(__name__)


@make_argcheck
def check_combocuts(combocuts: str):
    """Check combocuts content"""
    check(combocuts == 'NNPDF31',
          "Invalid combocut. Must be NNPDF31 (or implement it yourself).")


@make_argcheck
def check_rngalgo(rngalgo: int):
    """Check rngalgo content"""
    check(0 <= rngalgo < 17,
          "Invalid rngalgo. Must be int between [0, 16].")


def check_nonnegative(var: str):
    """Ensure that `var` is positive"""
    @make_check
    def run_check(ns, **kwargs):
        val = ns[var]
        check(val >= 0, f"'{var}' must be positive or equal zero, but it is {val!r}.")
    return run_check


def make_dataset_dir(path):
    """Creates directory at path location."""
    if path.exists():
        log.warning(f"Dataset output folder exists: {path} Overwritting contents")
    else:
        path.mkdir(exist_ok=True)


def export_mask(path, mask):
    """Dump mask to file"""
    np.savetxt(path, mask, fmt='%d')


@check_combocuts
@check_rngalgo
@check_positive('errorsize')
@check_nonnegative('filterseed')
@check_nonnegative('seed')
def filter(experiments, theoryid, filter_path,
           fakedata: bool,
           filterseed:int, rngalgo:int, seed:int, fakenoise:bool,
           errorsize:numbers.Real, combocuts, t0pdfset):
    """Apply filters to all datasets"""
    if not fakedata:
        log.info('Filtering real data.')
        total_data, total_cut_data = _filter_real_data(filter_path, experiments)
    else:
        log.info('Filtering closure-test data.')
        RandomGenerator.InitRNG(rngalgo, seed)
        RandomGenerator.GetRNG().SetSeed(filterseed)
        total_data, total_cut_data = _filter_closure_data(filter_path, experiments,
                                                          t0pdfset, fakenoise, errorsize)
    log.info(f'Summary: {total_cut_data}/{total_data} datapoints passed kinematic cuts.')


def _write_ds_cut_data(path, dataset):
    make_dataset_dir(path)
    all_dsndata = dataset.commondata.ndata
    datamask = dataset.cuts.load()
    if datamask is None:
        filtered_dsndata = all_dsndata
        log.info("All {all_ndata} points  in in {dataset.name} passed kinematic cuts.")
    else:
        filtered_dsndata = len(datamask)
        log.info(f"{len(datamask)}/{all_dsndata} datapoints "
                 f"in {dataset.name} passed kinematic cuts.")
    # save to disk
    if datamask is not None:
        export_mask(path / f'FKMASK_{dataset.name}.dat', datamask)
    return all_dsndata, filtered_dsndata


def _filter_real_data(filter_path, experiments):
    """Filter real experimental data."""
    total_data_points = 0
    total_cut_data_points = 0
    for experiment in experiments:
        for dataset in experiment.datasets:
            path = filter_path / dataset.name
            nfull, ncut = _write_ds_cut_data(path, dataset)
            total_data_points += nfull
            total_cut_data_points += ncut
            dataset.load().Export(str(path))
    return total_data_points, total_cut_data_points


def _filter_closure_data(filter_path, experiments, fakepdfset, fakenoise, errorsize):
    """Filter closure test data."""
    total_data_points = 0
    total_cut_data_points = 0
    fakeset = fakepdfset.load()
    # Load experiments
    for experiment in experiments:
        #Don't want to save this in any cache since we are mutating it
        loaded_exp = experiment.load.__wrapped__(experiment)
        loaded_exp.MakeClosure(fakeset, fakenoise)
        for j, dataset in enumerate(experiment.datasets):
            path = filter_path / dataset.name
            nfull, ncut = _write_ds_cut_data(path, dataset)
            total_data_points += nfull
            total_cut_data_points += ncut
            loaded_ds = loaded_exp.GetSet(j)
            if errorsize != 1.0:
                loaded_ds.RescaleErrors(errorsize)
            loaded_ds.Export(str(path))
    return total_data_points, total_cut_data_points


def get_cuts_for_dataset(commondata, theoryid, q2min, w2min):
    """Return cut mask for dataset"""
    ds = commondata.load()
    datamask = [idat for idat in range(ds.GetNData())
                if pass_kincuts(ds, idat, theoryid, q2min, w2min)]
    return datamask


def check_t0pdfset(t0pdfset):
    """T0 pdf check"""
    t0pdfset.load()
    log.info(f'{t0pdfset} T0 checked.')


def check_positivity(posdatasets):
    """Verify positive datasets are ready for the fit."""
    log.info('Verifying positivity tables:')
    for pos in posdatasets:
        pos.load()
        log.info(f'{pos.name} checked.')

class Rule:
    def __init__(self, *, theoryid, initial_data: dict, defaults: dict):
        self.theoryid = theoryid
        self.dataset = None
        self.process_type = None
        for key in initial_data:
            setattr(self, key, initial_data[key])

        if not hasattr(self, "rule"):
            raise AttributeError("No rule defined.")

        if self.dataset is None and self.process_type is None:
            raise AttributeError("Please define either a process type or dataset.")

        # BUG: check this
        if self.process_type is None:
            from validphys.loader import Loader

            l = Loader()
            cd = l.check_commondata(self.dataset)
            self.process_type = cd.process_type

        self.defaults = defaults
        if self.process_type[:3] == "DIS":
            self.variables = CommonData.kinLabel["DIS"]
        else:
            self.variables = CommonData.kinLabel[self.process_type]

    def __call__(self, dataset, idat):
        """If this rule applies, we return True"""
        pto = self.theoryid.get_description().get('PTO')
        vfns = self.theoryid.get_description().get('FNS')
        ic = self.theoryid.get_description().get('IC')

        self.kinematics = [dataset.GetKinematics(idat, j) for j in range(3)]
        self.kinematics_dict = dict(zip(self.variables, self.kinematics))

        # Handle the generalised DIS cut
        if (self.process_type == "DIS_ALL" and dataset.GetProc(idat)[:3] == "DIS"):
            return eval(self.rule, {**self.defaults, **self.kinematics_dict})

        # potential BUG: check this
        if (dataset.GetSetName() != self.dataset and
            dataset.GetProc(idat) != self.process_type):
            return

        if hasattr(self, "VFNS") and self.VFNS != vfns:
            return

        # Will return True if inequality is satisfied
        return eval(self.rule, {**self.defaults, **self.kinematics_dict})


path = "/home/shayan/nnpdfgit/nnpdf/validphys2/src/validphys/"
with open(path+"cuts/filters.yaml", "r") as rules_stream,\
     open(path+"cuts/defaults.yaml", "r") as defaults_stream:
    try:
        rules = yaml.safe_load(rules_stream)
        defaults = yaml.safe_load(defaults_stream)
    except yaml.YAMLError as exception:
        print(exception)
def pass_kincuts(
    dataset,
    idat: int,
    theoryid,
    # TODO: check how to handle these arguments. Not needed currently
    q2min: float,
    w2min: float,
):
    # TODO: Add docstring
        
    for rule in (Rule(initial_data=i, theoryid=theoryid, defaults=defaults) for i in rules):
        rule_result = rule(dataset, idat)
        if rule_result is not None and rule_result == False:
            return False

    return True
