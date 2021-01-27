# -*- coding: utf-8 -*-
"""
Tools to obtain and analyse the pseudodata that was seen by the neural
networks during the fitting.
"""
import logging
import multiprocessing as mp
import os
import pathlib
import random

import numpy as np
import pandas as pd

from validphys.checks import check_cuts_fromfit, check_darwin_single_process
from validphys.commondataparser import load_commondata
from validphys.coredata import CommonData
from validphys.covmats import INTRA_DATASET_SYS_NAME

from reportengine import collect

import n3fit.io.reader as reader
from n3fit.performfit import initialize_seeds

import NNPDF

log = logging.getLogger(__name__)


fitted_pseudodata = collect('fitted_pseudodata_internal', ('fitcontext',))

context_index = collect("groups_index", ("fitcontext",))

@check_cuts_fromfit
def read_fit_pseudodata(fitcontext, context_index):
    """Generator to handle the reading of training and validation splits for a fit that has been
    produced with the ``savepseudodata`` flag set to ``True``.

    The data is read from the PDF to handle the mixing introduced by ``postfit``.

    The data files are concatenated to yield all the data that went into a fit. The training and validation
    indices are also returned so one can access the splits using pandas indexing.

    Raises
    ------
    FileNotFoundError
        If the training or validation files for the PDF set cannot be found.
    CheckError
        If the ``use_cuts`` flag is not set to ``fromfit``

    Example
    -------
    >>> from validphys.api import API
    >>> data_generator = API.read_fit_pseudodata(fit="NNPDF31_nnlo_as_0118_DISonly_pseudodata", use_cuts="fromfit")
    >>> data, tr_idx, val_idx = next(data_generator)
    >>> data.loc[tr_idx]
                        data
    group dataset id
    BCDMS BCDMSD  0    0.371510
                1    0.365659
                2    0.350234
                4    0.355560
                6    0.346234
    ...                     ...
    SLAC  SLACP   122  0.245322
                123  0.256854
                142  0.165455
                165  0.089741
                166  0.090437
    [1556 rows x 1 columns]
    """
    # List of length 1 due to the collect
    context_index = context_index[0]
    # The [0] is because of how pandas handles sorting a MultiIndex
    sorted_index = context_index.sortlevel(level=range(3))[0]

    pdf = fitcontext["pdf"]
    log.info(f"Using same pseudodata & training/validation splits as {pdf.name}.")
    nrep = len(pdf)
    path = pathlib.Path(pdf.infopath)

    for rep_number in range(1, nrep):
        # This is a symlink (usually).
        replica = path.with_name(pdf.name + "_" + str(rep_number).zfill(4) + ".dat")
        # we resolve the symlink
        if replica.parent.is_symlink():
            replica = pathlib.Path(os.path.realpath(replica))

        training_path = replica.with_name("training.dat")
        validation_path = replica.with_name("validation.dat")

        try:
            tr = pd.read_csv(training_path, index_col=[0, 1, 2], sep="\t", names=["data"])
            val = pd.read_csv(validation_path, index_col=[0, 1, 2], sep="\t", names=["data"])
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Could not find saved training and validation data files. "
                f"Please ensure {pdf} was generated with the savepseudodata flag set to true"
            ) from e
        tr["type"], val["type"] = "training", "validation"

        pseudodata = pd.concat((tr, val))
        pseudodata.sort_index(level=range(3), inplace=True)

        pseudodata.index = sorted_index

        tr = pseudodata[pseudodata["type"]=="training"]
        val = pseudodata[pseudodata["type"]=="validation"]

        yield pseudodata.drop("type", axis=1), tr.index, val.index


def make_replica(list_of_commondata, seed=None):
    # TODO: this is the old docstring: update it
    """Generator that takes in a :py:class:`validphys.coredata.CommonData` or
    :py:class:`validphys.core.CommonDataSpec` object and yields pseudodata replicas
    of the data central value. This generator is infinite in the sense that it will
    never raise a StopIteration exception

    The square root (obtained by the Cholesky decomposition) of the covariance
    matrix is used as the sampling matrix with the covariance matrix being obtained using
    :py:func:`validphys.covmats.covmat_from_systematics`. In the internal code, the call
    to this function has the boolean parameter ``use_mult_errors`` set to ``False`` to
    ignore multiplicative uncertainties. Gaussian sampling is performed using the
    additive part of the covariance matrix. An additional gaussian sampling for the
    renormalization of the data having multiplicative uncertainties happens later.
    All the contributions to the covariance matrix coming from theory errors should be
    accounted for in the additive part.

    Parameters
    ---------
    commondata: :py:class:`validphys.coredata.CommonData`, :py:class:`validphys.core.CommonDataSpec`
        CommonData which stores information about systematic errors,
        their treatment and description.

    seed: int, None
        Seed used to initialise the random number generator. If ``None`` then a random seed is allocated
        using ``random.randint(1, 1000)``. This default behaviour is selected to avoid introducing
        inadvertent correlations.

    Returns
    -------
    pseudodata: np.array
        Numpy array which is N_dat (where N_dat is the number of data points after cuts)
        containing monte carlo samples of data centered around the data central value.


    Example
    -------
    >>> from validphys.loader import Loader
    >>> l = Loader()
    >>> from validphys.pseudodata import make_replica
    >>> cd = l.check_commondata("NMC")
    >>> data_generator = make_replica(cd)
    >>> next(data_generator)
    - Random Generator allocated: ranlux
    array([0.24013561, 0.24060029, 0.26382826, 0.27698772, 0.28603631,
           0.28491346, 0.30983694, 0.31394779, 0.2987047 , 0.31680287,
           0.33169788, 0.29497604, 0.30490075, 0.32969979, 0.34781687,
           0.34964414, 0.30162117, 0.32235222, 0.32743923, 0.33293424,


    .. todo:: Replace the inhouse random number generation with a numpy equivalent.
    .. todo:: Allow for correlations between datasets within an experiment.
    """
    # Seed the numpy RNG with the seed.
    np.random.seed(seed=seed)

    # The inner while True loop is for ensuring a positive definite
    # pseudodata replica
    while True:
        pseudodatas = []
        special_add = []
        special_mult = []
        mult_shifts = []
        check_positive_masks = []
        for cd in list_of_commondata:
            pseudodata = cd.central_values.to_numpy()

            # add contribution from statistical uncertainty
            pseudodata += (cd.stat_errors.to_numpy() * np.random.randn(cd.ndata))

            # ~~~ ADDITIVE ERRORS  ~~~
            add_errors = cd.additive_errors
            add_uncorr_errors = add_errors.loc[:, add_errors.columns=="UNCORR"].to_numpy()

            pseudodata += (add_uncorr_errors * np.random.randn(*add_uncorr_errors.shape)).sum(axis=1)

            # correlated within dataset
            add_corr_errors = add_errors.loc[:, add_errors.columns == "CORR"].to_numpy()
            pseudodata += add_corr_errors @ np.random.randn(add_corr_errors.shape[1])

            # append the partially shifted pseudodata
            pseudodatas.append(pseudodata)
            # store the additive errors with correlations between datasets for later use
            special_add.append(
                add_errors.loc[:, ~add_errors.columns.isin(INTRA_DATASET_SYS_NAME)]
            )
            # ~~~ MULTIPLICATIVE ERRORS ~~~
            mult_errors = cd.multiplicative_errors
            mult_uncorr_errors = mult_errors.loc[:, mult_errors.columns == "UNCORR"].to_numpy()
            # convert to from percent to fraction
            mult_shift = (
                1 + mult_uncorr_errors * np.random.randn(*mult_uncorr_errors.shape) / 100
            ).prod(axis=1)

            mult_corr_errors = mult_errors.loc[:, mult_errors.columns == "CORR"].to_numpy()
            mult_shift *= (
                1 + mult_corr_errors * np.random.randn(1, mult_corr_errors.shape[1]) / 100
            ).prod(axis=1)

            mult_shifts.append(mult_shift)

            # store the multiplicative errors with correlations between datasets for later use
            special_mult.append(
                mult_errors.loc[:, ~mult_errors.columns.isin(INTRA_DATASET_SYS_NAME)]
            )

            # mask out the data we want to check are all positive
            if "ASY" in cd.commondataproc:
                check_positive_masks.append(np.zeros_like(pseudodata, dtype=bool))
            else:
                check_positive_masks.append(np.ones_like(pseudodata, dtype=bool))

        # if we sort here (which sorts columns), then permuting datasets doesn't change the result
        # non-overlapping systematics are set to NaN by concat, fill with 0 instead.
        special_add_errors = pd.concat(special_add, axis=0, sort=True).fillna(0).to_numpy()
        special_mult_errors = pd.concat(special_mult, axis=0, sort=True).fillna(0).to_numpy()


        all_pseudodata = (
            np.concatenate(pseudodatas, axis=0)
            + special_add_errors @ np.random.randn(special_add_errors.shape[1])
        ) * (
            np.concatenate(mult_shifts, axis=0)
            * (1 + special_mult_errors * np.random.randn(1, special_mult_errors.shape[1]) / 100).prod(axis=1)
        )

        if np.all(all_pseudodata[np.concatenate(check_positive_masks, axis=0)] >= 0):
            break

    return all_pseudodata


@check_darwin_single_process
def fitted_pseudodata_internal(fit, experiments, num_fitted_replicas, t0pdfset=None, NPROC=None):
    """A function to obtain information about the pseudodata that went
        into an N3FIT fit.

        Parameters
        ----------
        fit: :py:class:`validphys.core.FitSpec`
        experiments:
            List of :py:class:`validphys.core.ExeperimentSpec`
        num_nnfit_replicas: ``int``
            Provided for by :py:mod:`validphys.fitdata`. Equal to the number of
            pre-postfit replicas.
        t0pdfset: :py:class:`validphys.core.PDF`
        NPROC: ``int``
            Integer specifying how many cores to run on. Default is
            ``mp.cpu_count()``

        Example
        -------
        Create a ``YAML`` file say ``runcard_for_pseudodata.yaml``

        .. code-block:: YAML
            :caption: runcard_for_pseudodata.yaml

            pdf: PN3_DIS_130519
            fit: PN3_DIS_130519

            experiments:
              from_: fit

            theory:
              from_: fit

            t0pdfset:
              from_: datacuts

            datacuts:
              from_: fit

            theoryid:
              from_: theory

            use_cuts: fromfit

        Then run

            >>> with open("./runcard_for_pseudodata.yaml", 'r') as stream:
            ...     from reportengine.compat import yaml
            ...     runcard = yaml.safe_load(stream)
            >>> from validphys.api import API
            >>> API.get_pseudodata_internal(**runcard)

        Notes
        -----
            - This is a wrapper for the ``fitted_pseudodata`` action
              which knows that ``experiments``, *must* come from fit
              and similarly ``PDF`` and ``theoryid`` *must* be the same as
              that of ``fit`` and so on.
            - This function returns the pseudodata for the replicas
              pre-postfit. Postfit discards some replicas and rearranges
              the order. The correpsondence is done by the
              :py:func:`get_pseudodata`
              function.
            - This code runs in parallel to increase efficiency.
    """
    if t0pdfset is not None:
        t0pdfset = t0pdfset.load_t0()

    # The + 1 coming from the fact that we wish to
    # include the last replica
    replica = range(1, num_fitted_replicas + 1)

    trvlseed, nnseed, mcseed, genrep = [
        fit.as_input().get("fitting").get(i)
        for i in ["trvlseed", "nnseed", "mcseed", "genrep"]
    ]

    seeds = initialize_seeds(replica, trvlseed, nnseed, mcseed, genrep)

    def task(d, mcseeds, trvlseeds, replicas):
        all_exp_infos = [[] for _ in range(len(mcseeds))]
        for exp in experiments:
            all_exp_dicts = reader.common_data_reader(
                exp, t0pdfset, replica_seeds=mcseeds, trval_seeds=trvlseeds
            )
            for i, exp_dict in enumerate(all_exp_dicts):
                all_exp_infos[i].append(exp_dict)
        for i, j in zip(all_exp_infos, replicas):
            d[j] = i

    if NPROC == 1:
        pseudodata_dicts = dict()
        task(pseudodata_dicts, seeds.mcseeds, seeds.trvlseeds, replica)
    else:
        with mp.Manager() as manager:
            d = manager.dict()

            if NPROC is None:
                NPROC = mp.cpu_count()
                log.warning(
                    f"Using all {NPROC} cores available, this may be dangerous "
                    "especially for use on a cluster. Consider setting the NPROC "
                    "variable to something sensible."
                )
            processes = []

            # convert sub arrays back to lists, use tolist to get builtin python
            # types.
            list_split = lambda lst, n: [
                arr.tolist() for arr in np.array_split(lst, n)
            ]
            batched_mcseeds = list_split(seeds.mcseeds, NPROC)
            batched_trvlseeds = list_split(seeds.trvlseeds, NPROC)
            batched_replica_num = list_split(replica, NPROC)
            for mc_batch, trvl_batch, replica_batch in zip(
                batched_mcseeds, batched_trvlseeds, batched_replica_num
            ):
                p = mp.Process(
                    target=task,
                    args=(d, mc_batch, trvl_batch, replica_batch,),
                )
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
            pseudodata_dicts = dict(d)
    return pseudodata_dicts


def get_pseudodata(fitted_pseudodata, fitted_replica_indexes):
    """Pseudodata used during fitting but correctly accounting for
    the postfit reordering.
    """
    # By collecting over `fitcontext` we create a list of length
    # one.
    fitted_pseudodata = fitted_pseudodata[0]
    return [fitted_pseudodata[i] for i in fitted_replica_indexes]


def _datasets_mask(experiment_list):
    """Function to obtain a per datasets training/validation
    mask given the mask for the corresponding experiment.

    Returns
    -------
    dict:
        - tr_mask: training mask for the datasets in the experiment
        - vl_mask: validation mask for the datasets in the experiment
    """
    tr_mask = experiment_list["trmask"]
    vl_mask = experiment_list["vlmask"]
    slices = []
    start = 0
    for i in experiment_list["datasets"]:
        ndata = i["ndata"]
        slices.append(start + ndata)
        start += ndata

    return {
        "trmask": np.split(tr_mask, slices[:-1]),
        "vlmask": np.split(vl_mask, slices[:-1]),
    }


def training_validation_pseudodata(get_pseudodata):
    """Generator to yield a dictionary of training and validation DataFrame
    per replica indexed appropriately using a MultiIndex
    """
    exp_infos = get_pseudodata
    columns = ["experiment", "dataset", "id"]
    # Loop over all initial replicas
    for replica in exp_infos:
        tr_records, tr_central_values = [], []
        vl_records, vl_central_values = [], []
        # Loop over experiments in given replica
        for experiment in replica:
            split_masks = _datasets_mask(experiment)
            tr_mask, vl_mask = split_masks["trmask"], split_masks["vlmask"]
            # While we're here extend the central_values of the experiment
            tr_central_values.extend(np.squeeze(experiment["expdata"]))
            vl_central_values.extend(np.squeeze(experiment["expdata_vl"]))
            # Loop over datasets in experiment
            for i, dataset in enumerate(experiment["datasets"]):
                tr_dataset_mask = tr_mask[i]
                vl_dataset_mask = vl_mask[i]
                tr_indices = np.array((range(dataset["ndata"])))[tr_dataset_mask]
                vl_indices = np.array((range(dataset["ndata"])))[vl_dataset_mask]
                for tr_idat in tr_indices:
                    tr_records.append(
                        dict(
                            [
                                ("experiment", experiment["name"]),
                                ("dataset", dataset["name"]),
                                ("id", tr_idat),
                            ]
                        )
                    )
                for vl_idat in vl_indices:
                    vl_records.append(
                        dict(
                            [
                                ("experiment", experiment["name"]),
                                ("dataset", dataset["name"]),
                                ("id", vl_idat),
                            ]
                        )
                    )

        tr_df = pd.DataFrame(tr_records, columns=columns)
        vl_df = pd.DataFrame(vl_records, columns=columns)

        tr_df.set_index(columns, inplace=True)
        vl_df.set_index(columns, inplace=True)

        tr_index = tr_df.index
        vl_index = vl_df.index
        tr_vl_dict = {
            "trdata": pd.DataFrame(tr_central_values, index=tr_index, columns=["data"]),
            "vldata": pd.DataFrame(vl_central_values, index=vl_index, columns=["data"]),
        }
        yield tr_vl_dict
