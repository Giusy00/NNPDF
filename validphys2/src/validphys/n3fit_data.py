"""
n3fit_data.py

Providers which prepare the data ready for
:py:func:`n3fit.performfit.performfit`. Returns python objects but the underlying
functions make calls to libnnpdf C++ library.

"""
from collections import defaultdict
from copy import deepcopy
import hashlib
import logging

import numpy as np
import pandas as pd

from NNPDF import RandomGenerator
from reportengine import collect
from reportengine.table import table

from validphys.n3fit_data_utils import (
    common_data_reader_experiment,
    positivity_reader,
)

log = logging.getLogger(__name__)

def replica_trvlseed(replica, trvlseed):
    """Generates the ``trvlseed`` for a ``replica``."""
    # TODO: move to the new infrastructure
    # https://numpy.org/doc/stable/reference/random/index.html#introduction
    np.random.seed(seed=trvlseed)
    for _ in range(replica):
        res = np.random.randint(0, pow(2, 31))
    return res

def replica_nnseed(replica, nnseed):
    """Generates the ``nnseed`` for a ``replica``."""
    np.random.seed(seed=nnseed)
    for _ in range(replica):
        res = np.random.randint(0, pow(2, 31))
    return res

def replica_mcseed(replica, mcseed, genrep):
    """Generates the ``mcseed`` for a ``replica``."""
    if not genrep:
        return None
    np.random.seed(seed=mcseed)
    for _ in range(replica):
        res = np.random.randint(0, pow(2, 31))
    return res


def tr_masks(data, replica_trvlseed):
    """Generate the boolean masks used to split data into training and
    validation points. Returns a list of 1-D boolean arrays, one for each
    dataset. Each array has length equal to N_data, the datapoints which
    will be included in the training are ``True`` such that

        tr_data = data[tr_mask]

    """
    nameseed = int(hashlib.sha256(str(data).encode()).hexdigest(), 16) % 10 ** 8
    nameseed += replica_trvlseed
    # TODO: update this to new random infrastructure.
    np.random.seed(nameseed)
    trmask_partial = []
    for dataset in data.datasets:
        # TODO: python commondata will not require this rubbish.
        # all data if cuts are None
        cuts = dataset.cuts
        ndata = len(cuts.load()) if cuts else dataset.commondata.ndata
        frac = dataset.frac
        trmax = int(frac * ndata)
        mask = np.concatenate(
            [np.ones(trmax, dtype=np.bool), np.zeros(ndata - trmax, dtype=np.bool)]
        )
        np.random.shuffle(mask)
        trmask_partial.append(mask)
    return trmask_partial

def kfold_masks(kpartitions, data):
    """Collect the masks (if any) due to kfolding for this data.
    These will be applied to the experimental data before starting
    the training of each fold.

    Parameters
    ----------
    kpartitions: list[dict]
        list of partitions, each partition dictionary with key-value pair
        `datasets` and a list containing the names of all datasets in that
        partition. See n3fit/runcards/Basic_hyperopt.yml for an example
        runcard or the hyperopt documentation for an expanded discussion on
        k-fold partitions.
    data: validphys.core.DataGroupSpec
        full list of data which is to be partitioned.

    Returns
    -------
    kfold_masks: list[np.array]
        A list containing a boolean array for each partition. Each array is
        a 1-D boolean array with length equal to the number of cut datapoints
        in ``data``. If a dataset is included in a particular fold then the
        mask will be True for the elements corresponding to those datasets
        such that data.load().get_cv()[kfold_masks[i]] will return the
        datapoints in the ith partition. See example below.

    Examples
    --------
    >>> from validphys.api import API
    >>> partitions=[
    ...     {"datasets": ["HERACOMBCCEM", "HERACOMBNCEP460", "NMC", "NTVNBDMNFe"]},
    ...     {"datasets": ["HERACOMBCCEP", "HERACOMBNCEP575", "NMCPD", "NTVNUDMNFe"]}
    ... ]
    >>> ds_inputs = [{"dataset": ds} for part in partitions for ds in part["datasets"]]
    >>> kfold_masks = API.kfold_masks(dataset_inputs=ds_inputs, kpartitions=partitions, theoryid=53, use_cuts="nocuts")
    >>> len(kfold_masks) # one element for each partition
    2
    >>> kfold_masks[0] # mask which splits data into first partition
    array([False, False, False, ...,  True,  True,  True])
    >>> data = API.data(dataset_inputs=ds_inputs, theoryid=53, use_cuts="nocuts")
    >>> fold_data = data.load().get_cv()[kfold_masks[0]]
    >>> len(fold_data)
    604
    >>> kfold_masks[0].sum()
    604

    """
    list_folds = []
    if kpartitions is not None:
        for partition in kpartitions:
            data_fold = partition.get("datasets", [])
            mask = []
            for dataset in data.datasets:
                # TODO: python commondata will not require this rubbish.
                # all data if cuts are None
                cuts = dataset.cuts
                ndata = len(cuts.load()) if cuts else dataset.commondata.ndata
                # If the dataset is in the fold, its mask is full of 0s
                if str(dataset) in data_fold:
                    mask.append(np.zeros(ndata, dtype=np.bool))
                # otherwise of ones
                else:
                    mask.append(np.ones(ndata, dtype=np.bool))
            list_folds.append(np.concatenate(mask))
    return list_folds


def _mask_fk_tables(dataset_dicts, tr_masks):
    """
    Internal function which masks the fktables for a group of datasets.

    Parameters
    ----------
        dataset_dicts: list[dict]
            list of datasets dictionaries returned by
            :py:func:`validphys.n3fit_data_utils.common_data_reader_experiment`.
        tr_masks: list[np.array]
            a tuple containing the lists of training masks for each dataset.

    Return
    ------
        data_trmask: np.array
            boolean array resulting from concatenating the training masks of
            each dataset.

    Note: the returned masks are only used in order to mask the covmat
    """
    trmask_partial = tr_masks
    for dataset_dict, tr_mask in zip(dataset_dicts, trmask_partial):
        # Generate the training and validation fktables
        tr_fks = []
        vl_fks = []
        ex_fks = []
        vl_mask = ~tr_mask
        for fktable_dict in dataset_dict["fktables"]:
            tr_fks.append(fktable_dict["fktable"][tr_mask])
            vl_fks.append(fktable_dict["fktable"][vl_mask])
            ex_fks.append(fktable_dict.get("fktable"))
        dataset_dict["tr_fktables"] = tr_fks
        dataset_dict["vl_fktables"] = vl_fks
        dataset_dict["ex_fktables"] = ex_fks

    return np.concatenate(trmask_partial)


def generate_data_replica(data, replica_mcseed, setupfit_check=False,):
    """Generate a pseudodata replica for ``data`` given the ``replica_seed``"""
    if setupfit_check:
        replica_mcseed = None
    spec_c = data.load()
    base_mcseed = int(hashlib.sha256(str(data).encode()).hexdigest(), 16) % 10 ** 8
    # copy C++ object to avoid mutation
    # t0 not required for replica generation, since libnnpdf uses experimental
    # covmat to generate replicas.
    spec_replica_c = type(spec_c)(spec_c)
    # Replica generation
    if replica_mcseed is not None:
        mcseed = base_mcseed + replica_mcseed
        RandomGenerator.InitRNG(0, mcseed)
        spec_replica_c.MakeReplica()
    return spec_replica_c.get_cv()


def fitting_data_dict(
    data,
    generate_data_replica,
    tr_masks,
    kfold_masks,
    t0set=None,
    diagonal_basis=None,
):
    """
    Provider which takes  the information from validphys ``data``.

    Returns
    -------
    all_dict_out: dict
        Containing all the information of the experiment/dataset
        for training, validation and experimental With the following keys:

        'datasets'
            list of dictionaries for each of the datasets contained in ``data``
        'name'
            name of the ``data`` - typically experiment/group name
        'expdata_true'
            non-replica data
        'invcovmat_true'
            inverse of the covmat (non-replica)
        'trmask'
            mask for the training data
        'invcovmat'
            inverse of the covmat for the training data
        'ndata'
            number of datapoints for the training data
        'expdata'
            experimental data (replica'd) for training
        'vlmask'
            (same as above for validation)
        'invcovmat_vl'
            (same as above for validation)
        'ndata_vl'
            (same as above for validation)
        'expdata_vl'
            (same as above for validation)
        'positivity'
            bool - is this a positivity set?
        'count_chi2'
            should this be counted towards the chi2
    """
    # TODO: Plug in the python data loading when available. Including but not
    # limited to: central values, ndata, replica generation, covmat construction
    spec_c = data.load()
    ndata = spec_c.GetNData()
    expdata_true = spec_c.get_cv().reshape(1, ndata)
    if t0set:
        t0pdfset = t0set.load_t0()
        spec_c.SetT0(t0pdfset)

    expdata = generate_data_replica

    datasets = common_data_reader_experiment(spec_c, data)

    # t0 covmat
    covmat = spec_c.get_covmat()
    inv_true = np.linalg.inv(covmat)

    if diagonal_basis:
        log.info("working in diagonal basis.")
        eig, v = np.linalg.eigh(covmat)
        dt_trans = v.T
    else:
        dt_trans = None
        dt_trans_tr = None
        dt_trans_vl = None


    # Copy dataset dict because we mutate it.
    datasets_copy = deepcopy(datasets)

    tr_mask = _mask_fk_tables(datasets_copy, tr_masks)
    vl_mask = ~tr_mask

    if diagonal_basis:
        expdata = np.matmul(dt_trans, expdata)
        # make a 1d array of the diagonal
        covmat_tr = eig[tr_mask]
        invcovmat_tr = 1./covmat_tr

        covmat_vl = eig[vl_mask]
        invcovmat_vl = 1./covmat_vl

        # prepare a masking rotation
        dt_trans_tr = dt_trans[tr_mask]
        dt_trans_vl = dt_trans[vl_mask]
    else:
        covmat_tr = covmat[tr_mask].T[tr_mask]
        invcovmat_tr = np.linalg.inv(covmat_tr)

        covmat_vl = covmat[vl_mask].T[vl_mask]
        invcovmat_vl = np.linalg.inv(covmat_vl)

    ndata_tr = np.count_nonzero(tr_mask)
    expdata_tr = expdata[tr_mask].reshape(1, ndata_tr)

    ndata_vl = np.count_nonzero(vl_mask)
    expdata_vl = expdata[vl_mask].reshape(1, ndata_vl)

    # Now save a dictionary of training/validation/experimental folds
    # for training and validation we need to apply the tr/vl masks
    # for experimental we need to negate the mask
    folds = defaultdict(list)
    for fold in kfold_masks:
        folds["training"].append(fold[tr_mask])
        folds["validation"].append(fold[vl_mask])
        folds["experimental"].append(~fold)

    dict_out = {
        "datasets": datasets_copy,
        "name": str(data),
        "expdata_true": expdata_true,
        "invcovmat_true": inv_true,
        "trmask": tr_mask,
        "invcovmat": invcovmat_tr,
        "ndata": ndata_tr,
        "expdata": expdata_tr,
        "vlmask": vl_mask,
        "invcovmat_vl": invcovmat_vl,
        "ndata_vl": ndata_vl,
        "expdata_vl": expdata_vl,
        "positivity": False,
        "count_chi2": True,
        "folds" : folds,
        "data_transformation_tr": dt_trans_tr,
        "data_transformation_vl": dt_trans_vl,
    }
    return dict_out

exps_fitting_data_dict = collect("fitting_data_dict", ("group_dataset_inputs_by_experiment",))

def replica_nnseed_fitting_data_dict(replica, exps_fitting_data_dict, replica_nnseed):
    """For a single replica return a tuple of the inputs to this function.
    Used with `collect` over replicas to avoid having to perform multiple
    collects.

    See Also
    --------
    replicas_nnseed_fitting_data_dict - the result of collecting this function
    over replicas.

    """
    return (replica, exps_fitting_data_dict, replica_nnseed)

replicas_nnseed_fitting_data_dict = collect("replica_nnseed_fitting_data_dict", ("replicas",))

exps_pseudodata = collect("generate_data_replica", ("group_dataset_inputs_by_experiment",))
replicas_exps_pseudodata = collect("exps_pseudodata", ("replicas",))

@table
def pseudodata_table(replicas_exps_pseudodata, replicas, experiments_index):
    """Creates a pandas DataFrame containing the generated pseudodata. The
    index is :py:func:`validphys.results.experiments_index` and the columns
    are the replica numbers.

    Notes
    -----
    Whilst running ``n3fit``, this action will only be called if
    `fitting::savepseudodata` is `true` and replicas are fitted one at a time.
    The table can be found in the replica folder i.e. <fit dir>/nnfit/replica_*/

    """
    rep_dfs = []
    for rep_exps_pseudodata, rep in zip(replicas_exps_pseudodata, replicas):
        all_pseudodata = np.concatenate(rep_exps_pseudodata)
        rep_dfs.append(pd.DataFrame(
            all_pseudodata,
            columns=[f"replica {rep}"],
            index=experiments_index
        ))
    return pd.concat(rep_dfs, axis=1)


exps_tr_masks = collect("tr_masks", ("group_dataset_inputs_by_experiment",))
replicas_exps_tr_masks = collect("exps_tr_masks", ("replicas",))


@table
def training_mask_table(replicas_exps_tr_masks, replicas, experiments_index):
    """Save the boolean mask used to split data into training and validation
    for each replica as a pandas DataFrame, indexed by
    :py:func:`validphys.results.experiments_index`. Can be used to reconstruct
    the training and validation data used in a fit.

    Parameters
    ----------
    replicas_exps_tr_masks: list[list[list[np.array]]]
        Result of :py:func:`tr_masks` collected over experiments then replicas,
        which creates the nested structure. The outer list is len(replicas),
        the next list is len(group_dataset_inputs_by_experiment) and the
        inner-most list has an array for each dataset in that particular
        experiment - as defined by the metadata. The arrays should be 1-D
        boolean arrays which can be used as masks.
    replicas: NSlist
        Namespace list of replica numbers to tabulate masks for, each element
        of the list should be a `replica`. See example below for more
        information.
    experiments_index: pd.MultiIndex
        Index returned by :py:func:`validphys.results.experiments_index`.


    Example
    -------
    >>> from validphys.api import API
    >>> from reportengine.namespaces import NSList
    >>> # create namespace list for collects over replicas.
    >>> reps = NSList(list(range(1, 4)), nskey="replica")
    >>> ds_inp = [
    ...     {'dataset': 'NMC', 'frac': 0.75},
    ...     {'dataset': 'ATLASTTBARTOT', 'cfac':['QCD'], 'frac': 0.75},
    ...     {'dataset': 'CMSZDIFF12', 'cfac':('QCD', 'NRM'), 'sys':10, 'frac': 0.75}
    ... ]
    >>> API.training_mask_table(dataset_inputs=ds_inp, replicas=reps, trvlseed=123, theoryid=162, use_cuts="nocuts", mcseed=None, genrep=False)
                        replica 1  replica 2  replica 3
    group dataset    id                                 
    NMC   NMC        0        True      False      False
                    1        True       True       True
                    2       False       True       True
                    3        True       True      False
                    4        True       True       True
    ...                        ...        ...        ...
    CMS   CMSZDIFF12 45       True       True       True
                    46       True      False       True
                    47       True       True       True
                    48      False       True       True
                    49       True       True       True

    [345 rows x 3 columns]

    """
    rep_dfs = []
    for rep_exps_masks, rep in zip(replicas_exps_tr_masks, replicas):
        # create flat list with all dataset masks in, then concatenate to single
        # array.
        all_masks = np.concatenate([
            ds_mask
            for exp_masks in rep_exps_masks
            for ds_mask in exp_masks
        ])
        rep_dfs.append(pd.DataFrame(
            all_masks,
            columns=[f"replica {rep}"],
            index=experiments_index
        ))
    return pd.concat(rep_dfs, axis=1)

def fitting_pos_dict(posdataset):
    """Loads a positivity dataset. For more information see
    :py:func:`validphys.n3fit_data_utils.positivity_reader`.

    Parameters
    ----------
    posdataset: validphys.core.PositivitySetSpec
        Positivity set which is to be loaded.

    Examples
    --------
    >>> from validphys.api import API
    >>> posdataset = {"dataset": "POSF2U", "maxlambda": 1e6}
    >>> pos = API.fitting_pos_dict(posdataset=posdataset, theoryid=162)
    >>> len(pos)
    9

    """
    log.info("Loading positivity dataset %s", posdataset)
    return positivity_reader(posdataset)

posdatasets_fitting_pos_dict = collect("fitting_pos_dict", ("posdatasets",))


#can't use collect here because integdatasets might not exist.
def integdatasets_fitting_integ_dict(integdatasets=None):
    """Loads a integrability dataset. Calls same function as
    :py:func:`fitting_pos_dict`, except on each element of
    ``integdatasets`` if ``integdatasets`` is not None.

    Parameters
    ----------
    integdatasets: list[validphys.core.PositivitySetSpec]
        list containing the settings for the integrability sets. Examples of
        these can be found in the runcards located in n3fit/runcards. They have
        a format similar to ``dataset_input``.

    Examples
    --------
    >>> from validphys.api import API
    >>> integdatasets = [{"dataset": "INTEGXT3", "maxlambda": 1e2}]
    >>> res = API.integdatasets_fitting_integ_dict(integdatasets=integdatasets, theoryid=53)
    >>> len(res), len(res[0])
    (1, 9)
    >>> res = API.integdatasets_fitting_integ_dict(integdatasets=None)
    >>> print(res)
    None

    """
    if integdatasets is not None:
        integ_info = []
        for integ_set in integdatasets:
            log.info("Loading integrability dataset %s", integ_set)
            # Use the same reader as positivity observables
            integ_dict = positivity_reader(integ_set)
            integ_info.append(integ_dict)
        return integ_info
    log.warning("Not using any integrability datasets.")
    return None
