"""
test_regression.py

Write files with data to disk and assert they are the same upon
updates.
"""
import pathlib
import logging
import functools

import numpy as np
import scipy.linalg as la
import pandas as pd
from pandas.testing import assert_frame_equal

from reportengine.table import savetable, str_columns

import NNPDF
from validphys import results
from validphys.api import API
from validphys.tests.test_covmats import CORR_DATA


log = logging.getLogger(__name__)

REGRESSION_FOLDER = pathlib.Path(__file__).with_name('regressions')

#TODO: Move these to a library
def compare_tables(produced_table, storage_path):
    """Test that the ``produced_table`` is equal (as in allclose) to
    the one loaded from the `storage_path` using the `loader_func`"""
    if not storage_path.exists():
        savetable(produced_table, storage_path)
        #Fail test
        assert False, "Storage path does not exist"
    stored_table = pd.read_parquet(storage_path)
    assert_frame_equal(produced_table, stored_table, check_dtype=False)

def make_table_comp(f):
    """Compare the dataframe that the decorated function outputs with
    a file with the same name as the function and extension csv, loaded
    using the provided `loader_func`"""
    @functools.wraps(f)
    def f_(*args, **kwargs):
        filename = f'{f.__name__}.parquet'
        produced_table = str_columns(f(*args, **kwargs))
        compare_tables(produced_table, REGRESSION_FOLDER/filename)
    return f_

@make_table_comp
def test_mcreplica(data_config):
    config = dict(data_config)
    config["dataset_inputs"] = CORR_DATA
    seed = 123456
    # Use no cuts because if filter rules change in the
    # future then this test will end up failing
    rep = API.indexed_make_replica(**config, seed=seed)
    return rep

@make_table_comp
def test_expcovmat(data_config):
    mat = API.groups_covmat_no_table(**data_config)
    covmats = []
    for exp in API.experiments_data(**data_config):
        cd = exp.datasets[0].commondata.load()
        covmats.append(NNPDF.ComputeCovMat(cd, cd.get_cv()))
    othermat = la.block_diag(*covmats)
    assert np.allclose(mat.values, othermat)
    return mat

@make_table_comp
def test_t0covmat(data_witht0_config):
    return API.groups_covmat_no_table(**data_witht0_config)

@make_table_comp
def test_expsqrtcovmat(data_config):
    return API.groups_sqrtcovmat(**data_config)

@make_table_comp
def test_t0sqrtcovmat(data_witht0_config):
    return API.groups_sqrtcovmat(**data_witht0_config)

@make_table_comp
def test_pdf_plus_exp_covmat(data_config):
    return API.groups_covmat_no_table(use_pdferr=True, **data_config)

@make_table_comp
def test_predictions(data_config):
    # TODO: ideally we would change the baseline to just be corresponding columns
    # of `experiment_result_table`, however sane_load expects just a single level
    # of column and index - if we use a different format like parquet this could
    # be changed.
    res_tab = API.group_result_table_no_table(**data_config)
    th = res_tab.iloc[:, 2:].values
    return pd.DataFrame(th, columns=map(str, range(th.shape[1])))

@make_table_comp
def test_dataset_t0_predictions(data_witht0_config):
    # TODO: As in `test_predictions`
    res_tab = API.group_result_table_no_table(**data_witht0_config)
    th = res_tab.iloc[:, 2:].values
    return pd.DataFrame(th, columns=map(str, range(th.shape[1])))

@make_table_comp
def test_cv(data_config):
    # TODO: As in `test_predictions`
    res_tab = API.group_result_table_no_table(**data_config)
    data_values = res_tab.iloc[:, 0].values[:, np.newaxis]
    return pd.DataFrame(data_values, columns=['CV'])

@make_table_comp
def test_replicachi2data(data_witht0_config):
    return API.perreplica_chi2_table(**data_witht0_config)

@make_table_comp
def test_datasetchi2(data_singleexp_witht0_config):
    # This is a bit hacky but avoids requiring a fit
    exps = API.groups_data(**data_singleexp_witht0_config)
    chi2s = API.groups_datasets_chi2_data(**data_singleexp_witht0_config)
    return results.fits_datasets_chi2_table(['test'], [exps], [chi2s])

@make_table_comp(sane_load)
def test_art_rep_generation(data_config):
    config = dict(data_config)
    config["dataset_inputs"] = CORR_DATA
    config["fitting"] = {"seed": 123456}
    config["nreplica"] = 1
    _, art_replicas, _,_ = API.art_rep_generation(**config)
    return pd.DataFrame(art_replicas.T, columns=['rep0'])
