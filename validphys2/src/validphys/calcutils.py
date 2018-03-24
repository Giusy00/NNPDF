"""
calcutils.py

Low level utilities to calculate χ² and such. These are used to implement the
higher level functions in results.py
"""
import numpy as np
import scipy.linalg as la
from typing import Callable

def calc_chi2(sqrtcov, diffs):
    """Elementary function to compute the chi², given a Cholesky decomposed
    lower triangular part and a vector of differences"""
    #Note la.cho_solve doesn't really improve things here
    #NOTE: Do not enable check_finite. The upper triangular part is not
    #guaranteed to make any sense. If this causes a problem, it is a bug in
    #ibnnpdf.
    vec = la.solve_triangular(sqrtcov, diffs, lower=True, check_finite=False)
    #This sums up the result for the chi² for any input shape.
    #Sum the squares over the first dimension and leave the others alone
    return np.einsum('i...,i...->...', vec,vec)

def all_chi2(results):
    """Return the chi² for all elements in the result. Note that the
    interpretation of the result will depend on the PDF error type"""
    data_result, th_result = results
    diffs = th_result._rawdata - data_result.central_value[:,np.newaxis]
    return calc_chi2(sqrtcov=data_result.sqrtcovmat, diffs=diffs)

def central_chi2(results):
    """Calculate the chi² from the central value of the theory prediction to
    the data"""
    data_result, th_result = results
    central_diff = th_result.central_value - data_result.central_value
    return calc_chi2(data_result.sqrtcovmat, central_diff)

def calc_phi(diffs, sqrtcov):
    """Low level function which calculates phi given a vector of differences
    and a Cholesky decomposed lower triangular part. Primarily used when phi
    is to be calculated independently from chi2.
    
    The vector of differences `diffs` should have N_bins on the final axis
    E.g. N_replicas*N_bins
    """
    diffs = np.array(diffs).T
    return np.sqrt((np.mean(calc_chi2(sqrtcov, diffs), axis=0) -
                    calc_chi2(sqrtcov, diffs.mean(axis=1)))/diffs.shape[0])

def bootstrap_values(data, nresamples, 
                    apply_func:Callable=None, *args):
    """General bootstrap sample

    If just `data` and `nresamples` is provided, then `bootstrap_values` 
    creates N resamples of the data, where each resample is a Monte Carlo 
    selection of the data across replicas. The mean of each resample is 
    returned

    Alternatively, the user can specify a function to be sampled `apply_func`
    plus any additional arguments required by that function. 
    `bootstrap_values` then returns `apply_func(bootstrap_data, *args)`
    where `bootstrap_data.shape = (nresamples, data.shape)`. It is 
    critical that `apply_func` can handle data input in this format.
    """
    data = np.atleast_2d(data)
    N_reps = data.shape[0]
    bootstrap_data = data[np.random.randint(N_reps, 
                                            size=(nresamples, N_reps)), ...]
    resample_data = np.empty(nresamples)
    if apply_func is None:
        return np.mean(bootstrap_data, axis=1)
    else:
        return apply_func(bootstrap_data, *args)
