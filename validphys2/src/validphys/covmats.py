"""Module for handling logic and manipulation of covariance and correlation
matrices on different levels of abstraction
"""
import logging

import numpy as np
import pandas as pd
import scipy.linalg as la

from reportengine import collect
from reportengine.table import table

from validphys.calcutils import regularize_covmat, get_df_block
from validphys.checks import (
    check_dataset_cuts_match_theorycovmat,
    check_norm_threshold,
    check_pdf_is_montecarlo,
    check_speclabels_different,
    check_data_cuts_match_theorycovmat,
)
from validphys.convolution import central_predictions
from validphys.core import PDF, DataGroupSpec, DataSetSpec
from validphys.results import ThPredictionsResult

log = logging.getLogger(__name__)

INTRA_DATASET_SYS_NAME = ("UNCORR", "CORR", "THEORYUNCORR", "THEORYCORR")


def covmat_from_systematics(commondata, central_values=None):
    """Take the statistical uncertainty and systematics table from
    a :py:class:`validphys.coredata.CommonData` object and
    construct the covariance matrix accounting for correlations between
    systematics.

    If the systematic has the name ``SKIP`` then it is ignored in the
    construction of the covariance matrix.

    ADDitive or MULTiplicative systypes are handled by either multiplying
    the additive or multiplicative uncertainties respectively. We convert
    uncertainties so that they are all in the same units as the data:
        - Additive (ADD) systematics are left unchanged
        - multiplicative (MULT) systematics need to be converted from a
        percentage by multiplying by the central value
        and dividing by 100.

    Finally, the systematics are split into the five possible archetypes
    of systematic uncertainties: uncorrelated (UNCORR), correlated (CORR),
    theory uncorrelated (THEORYUNCORR), theory correlated (THEORYCORR) and
    special correlated (SPECIALCORR) systematics.

    Uncorrelated contributions from statistical error, uncorrelated and
    theory uncorrelated are added in quadrature to the diagonal of the covmat.

    The contribution to the covariance matrix arising due to
    correlated systematics is schematically ``A_correlated @ A_correlated.T``,
    where A_correlated is a matrix N_dat by N_sys. The total contribution
    from correlated systematics is found by adding together the result of
    mutiplying each correlated systematic matrix by its transpose
    (correlated, theory_correlated and special_correlated).

    For more information on the generation of the covariance matrix see the
    `paper <https://arxiv.org/pdf/hep-ph/0501067.pdf>`_
    outlining the procedure, specifically equation 2 and surrounding text.

    Paramaters
    ----------
    commondata : validphys.coredata.CommonData
        CommonData which stores information about systematic errors,
        their treatment and description.
    central_values: None, np.array
        1-D array containing alternative central values to combine with the
        multiplicative errors to calculate their absolute contributions. By
        default this is None, and the experimental central values are used but
        can be used to calculate, for example, the t0 covariance matrix by
        using the predictions from the central member of the t0 pdf.

    Returns
    -------
    cov_mat : np.array
        Numpy array which is N_dat x N_dat (where N_dat is the number of data
        points after cuts) containing uncertainty and correlation information.

    Example
    -------
    >>> from validphys.commondataparser import load_commondata
    >>> from validphys.loader import Loader
    >>> from validphys.calcutils import covmat_from_systematics
    >>> l = Loader()
    >>> cd = l.check_commondata("NMC")
    >>> cd = load_commondata(cd)
    >>> covmat_from_systematics(cd)
    array([[8.64031971e-05, 8.19971921e-05, 6.27396915e-05, ...,
            2.40747732e-05, 2.79614418e-05, 3.46727332e-05],
           [8.19971921e-05, 1.41907442e-04, 6.52360141e-05, ...,
            2.36624379e-05, 2.72605623e-05, 3.45492831e-05],
           [6.27396915e-05, 6.52360141e-05, 9.41928691e-05, ...,
            1.79244824e-05, 2.08603130e-05, 2.56283708e-05],
           ...,
           [2.40747732e-05, 2.36624379e-05, 1.79244824e-05, ...,
            5.67822050e-05, 4.09077450e-05, 4.14126235e-05],
           [2.79614418e-05, 2.72605623e-05, 2.08603130e-05, ...,
            4.09077450e-05, 5.55150870e-05, 4.15843357e-05],
           [3.46727332e-05, 3.45492831e-05, 2.56283708e-05, ...,
            4.14126235e-05, 4.15843357e-05, 1.43824457e-04]])
    """
    return construct_covmat(
        commondata.stat_errors.to_numpy(),
        commondata.systematic_errors(central_values)
    )


def datasets_covmat_from_systematics(
    list_of_commondata, list_of_central_values=None
):
    """Given a list containing :py:class:`validphys.coredata.CommonData` s,
    construct the full covariance matrix.

    This is similar to :py:meth:`covmat_from_systematics`
    except that special corr systematics are concatenated across all datasets
    before being multiplied by their transpose to give off block-diagonal
    contributions. The other systematics contribute to the block diagonal in the
    same way as :py:meth:`covmat_from_systematics`.

    Parameters
    ----------
    list_of_commondata : list[validphys.coredata.CommonData]
        list of CommonData objects.
    list_of_central_values: None, list[np.array]
        list of 1-D arrays which contain alternative central values which are
        combined with the multiplicative errors to calculate their absolute
        contribution. By default this is None and the experimental central
        values are used.

    Returns
    -------
    cov_mat : np.array
        Numpy array which is N_dat x N_dat (where N_dat is the number of data points after cuts)
        containing uncertainty and correlation information.

    Example
    -------
    >>> from validphys.commondataparser import load_commondata
    >>> from validphys.covmats import datasets_covmat_from_systematics
    >>> from validphys.loader import Loader
    >>> l = Loader()
    >>> cd1 = l.check_commondata("ATLASLOMASSDY11EXT")
    >>> cd2 = l.check_commondata("ATLASZHIGHMASS49FB")
    >>> ld1, ld2 = map(load_commondata, (cd1, cd2))
    >>> datasets_covmat_from_systematics((ld1, ld2))
    array([[2.91814548e+06, 4.66692123e+06, 2.36823008e+06, 8.62587330e+05,
            2.78209614e+05, 1.11790645e+05, 1.75129920e+03, 7.97466600e+02,
            4.00296960e+02, 2.22039720e+02, 1.46202210e+02, 8.36558100e+01,
    """
    special_corrs = []
    block_diags = []

    if list_of_central_values is None:
        # want to just pass None to systematic_errors method
        list_of_central_values = [None for _ in list_of_commondata]

    for cd, central_values in zip(list_of_commondata, list_of_central_values):
        errors = cd.systematic_errors(central_values)
        # separate out the special uncertainties which can be correlated across
        # datasets
        is_intra_dataset_error = errors.columns.isin(INTRA_DATASET_SYS_NAME)
        block_diags.append(construct_covmat(
            cd.stat_errors.to_numpy(), errors.loc[:, is_intra_dataset_error]))
        special_corrs.append(errors.loc[:, ~is_intra_dataset_error])

    # concat systematics across datasets
    special_sys = pd.concat(special_corrs, axis=0, sort=False)
    # non-overlapping systematics are set to NaN by concat, fill with 0 instead.
    special_sys.fillna(0, inplace=True)

    diag = la.block_diag(*block_diags)
    return diag + special_sys.to_numpy() @ special_sys.to_numpy().T


def construct_covmat(stat_errors: np.array, sys_errors: pd.DataFrame):
    """Basic function to construct a covariance matrix (covmat), given the
    statistical error and a dataframe of systematics.

    Errors with name UNCORR or THEORYUNCORR are added in quadrature with
    the statistical error to the diagonal of the covmat.

    Other systematics are treated as correlated; their covmat contribution is
    found by multiplying them by their transpose.

    Parameters
    ----------
    stat_errors: np.array
        a 1-D array of statistical uncertainties
    sys_errors: pd.DataFrame
        a dataframe with shape (N_data * N_sys) and systematic name as the
        column headers. The uncertainties should be in the same units as the
        data.

    Notes
    -----
    This function doesn't contain any logic to ignore certain contributions to
    the covmat, if you wanted to not include a particular systematic/set of
    systematics i.e all uncertainties with MULT errors, then filter those out
    of ``sys_errors`` before passing that to this function.

    """
    diagonal = stat_errors ** 2

    is_uncorr = sys_errors.columns.isin(("UNCORR", "THEORYUNCORR"))
    diagonal += (sys_errors.loc[:, is_uncorr].to_numpy() ** 2).sum(axis=1)

    corr_sys_mat = sys_errors.loc[:, ~is_uncorr].to_numpy()
    return np.diag(diagonal) + corr_sys_mat @ corr_sys_mat.T


def experimental_covmat(commondata, cuts):
    """Returns the experimental covariance matrix. Details of how
    the covmat is constructed can be found in :py:func:`covmat_from_systematics`.
    The experimental covariance matrix uses the experimental central values
    to calculate the absolute uncertainties from the multiplicative systematics.

    Parameters
    ----------
    commondata: validphys.core.CommonDataSpec

    Returns
    -------
    covmat: np.array

    """
    #TODO: make a cut commondata action to avoid mistakes
    lcd = commondata.pyload()
    cut_lcd = lcd.with_cuts(cuts)
    return covmat_from_systematics(cut_lcd)


def t0_covmat(t0set, dataset, cuts):
    """Like :py:func:`experimental_covmat` except uses the ``t0pdf`` predictions
    to calculate the absolute constributions to the covmat from multiplicative
    uncertainties. The t0 predictions are the predictions generated from the
    central pdf, note that in the case that the ``t0pdf`` has replicas
    errortype this is not the same as the central value of the replica
    predictions in the case of hadronic observables.

    Parameters
    ----------
    t0set: validphys.core.PDF
        pdf set used to generate t0 predictions
    commondata: validphys.core.CommonDataSpec
        commondata object for which to generate the covmat.

    Returns
    -------
    covmat: np.array

    """
    # flatten values since t0_pred is 2D with shape n_data * 1
    t0_pred = central_predictions(dataset, t0set).to_numpy().squeeze()
    lcd = dataset.commondata.pyload()
    cut_lcd = lcd.with_cuts(cuts)
    return covmat_from_systematics(cut_lcd, t0_pred)

dataset_inputs_cuts = collect("cuts", ("data_input",))

def dataset_inputs_experimental_covmat(
    dataset_inputs_commondata, dataset_inputs_cuts):
    """Like :py:func:`experimental_covmat` except for all data"""
    #TODO: simply collect cut commondata instead of this
    cut_ld_cd = [
        cd.pyload().with_cuts(cuts)
        for cd, cuts in zip(dataset_inputs_commondata, dataset_inputs_cuts)
    ]
    return datasets_covmat_from_systematics(cut_ld_cd)

def dataset_inputs_t0_covmat(t0set, data, dataset_inputs_cuts):
    """Like :py:func:`t0_covmat` except for all data"""
    t0_preds = [
        central_predictions(dataset, t0set).to_numpy().squeeze()
        for dataset in data.datasets
    ]
    cut_ld_cd = [
        ds.commondata.pyload().with_cuts(cuts)
        for ds, cuts in zip(data.datasets, dataset_inputs_cuts)
    ]
    return datasets_covmat_from_systematics(cut_ld_cd, t0_preds)


def sqrt_covmat(covariance_matrix):
    """Function that computes the square root of the covariance matrix.

    Parameters
    ----------
    covariance_matrix : np.array
        A positive definite covariance matrix, which is N_dat x N_dat (where
        N_dat is the number of data points after cuts) containing uncertainty
        and correlation information.

    Returns
    -------
    sqrt_mat : np.array
        The square root of the input covariance matrix, which is N_dat x N_dat
        (where N_dat is the number of data points after cuts), and which is the
        the lower triangular decomposition. The following should be ``True``:
        ``np.allclose(sqrt_covmat @ sqrt_covmat.T, covariance_matrix)``.

    Notes
    -----
    The square root is found by using the Cholesky decomposition. However, rather
    than finding the decomposition of the covariance matrix directly, the (upper
    triangular) decomposition is found of the corresponding correlation matrix
    and then the output of this is rescaled and then transposed as
    ``sqrt_matrix = (decomp * sqrt_diags).T``, where ``decomp`` is the Cholesky
    decomposition of the correlation matrix and ``sqrt_diags`` is the square root
    of the diagonal entries of the covariance matrix. This method is useful in
    situations in which the covariance matrix is near-singular. See
    `here <https://www.gnu.org/software/gsl/doc/html/linalg.html#cholesky-decomposition>`_
    for more discussion on this.

    The lower triangular is useful for efficient calculation of the :math:`\chi^2`

    Example
    -------
    >>> from validphys.commondataparser import load_commondata
    >>> from validphys.loader import Loader
    >>> from validphys.calcutils import covmat_from_systematics
    >>> from validphys.results import sqrt_covmat
    >>> l = Loader()
    >>> cd = l.check_commondata("NMC")
    >>> cd = load_commondata(cd)
    >>> cov = covmat_from_systematics(cd)
    >>> sqrtcov = sqrt_covmat(cov)
    array([[9.29533200e-03, 0.00000000e+00, 0.00000000e+00, ...,
            0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
           [8.82133011e-03, 8.00572153e-03, 0.00000000e+00, ...,
            0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
           [6.74959124e-03, 7.11446377e-04, 6.93755946e-03, ...,
            0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
           ...,
           [2.58998530e-03, 1.01842488e-04, 5.34315873e-05, ...,
            4.36182637e-03, 0.00000000e+00, 0.00000000e+00],
           [3.00811652e-03, 9.05569142e-05, 7.09658356e-05, ...,
            1.18572366e-03, 4.31943367e-03, 0.00000000e+00],
           [3.73012316e-03, 2.05432491e-04, 4.40226875e-05, ...,
            9.61421910e-04, 5.31447414e-04, 9.98677667e-03]])
    """
    dimensions = covariance_matrix.shape

    if covariance_matrix.size == 0:
        raise ValueError("Attempting the decomposition of an empty matrix.")
    elif dimensions[0] != dimensions[1]:
        raise ValueError("The input covariance matrix should be square but "
                         f"instead it has dimensions {dimensions[0]} x "
                         f"{dimensions[1]}")

    sqrt_diags = np.sqrt(np.diag(covariance_matrix))
    correlation_matrix = covariance_matrix / sqrt_diags[:, np.newaxis] / sqrt_diags
    decomp = la.cholesky(correlation_matrix)
    sqrt_matrix = (decomp * sqrt_diags).T
    return sqrt_matrix


def groups_covmat_no_table(
       groups_data, groups_index, groups_covmat_collection):
    """Export the covariance matrix for the groups. It exports the full
    (symmetric) matrix, with the 3 first rows and columns being:

        - group name

        - dataset name

        - index of the point within the dataset.
    """
    data = np.zeros((len(groups_index),len(groups_index)))
    df = pd.DataFrame(data, index=groups_index, columns=groups_index)
    for group, group_covmat in zip(
            groups_data, groups_covmat_collection):
        name = group.name
        df.loc[[name],[name]] = group_covmat
    return df


@table
def groups_covmat(groups_covmat_no_table):
    """Duplicate of groups_covmat_no_table but with a table decorator."""
    return groups_covmat_no_table


@table
def groups_sqrtcovmat(
        groups_data, groups_index, groups_sqrt_covmat):
    """Like groups_covmat, but dump the lower triangular part of the
    Cholesky decomposition as used in the fit. The upper part indices are set
    to zero.
    """
    data = np.zeros((len(groups_index),len(groups_index)))
    df = pd.DataFrame(data, index=groups_index, columns=groups_index)
    for group, group_sqrt_covmat in zip(
            groups_data, groups_sqrt_covmat):
        name = group.name
        group_sqrt_covmat[np.triu_indices_from(group_sqrt_covmat, k=1)] = 0
        df.loc[[name],[name]] = group_sqrt_covmat
    return df


@table
def groups_invcovmat(
        groups_data, groups_index, groups_covmat_collection):
    """Compute and export the inverse covariance matrix.
    Note that this inverts the matrices with the LU method which is
    suboptimal."""
    data = np.zeros((len(groups_index),len(groups_index)))
    df = pd.DataFrame(data, index=groups_index, columns=groups_index)
    for group, group_covmat in zip(
            groups_data, groups_covmat_collection):
        name = group.name
        #Improve this inversion if this method tuns out to be important
        invcov = la.inv(group_covmat)
        df.loc[[name],[name]] = invcov
    return df


@table
def groups_normcovmat(groups_covmat, groups_data_values):
    """Calculates the grouped experimental covariance matrix normalised to data."""
    df = groups_covmat
    groups_data_array = np.array(groups_data_values)
    mat = df/np.outer(groups_data_array, groups_data_array)
    return mat


@table
def groups_corrmat(groups_covmat):
    """Generates the grouped experimental correlation matrix with groups_covmat as input"""
    df = groups_covmat
    covmat = df.values
    diag_minus_half = (np.diagonal(covmat))**(-0.5)
    mat = diag_minus_half[:,np.newaxis]*df*diag_minus_half
    return mat


@check_data_cuts_match_theorycovmat
def dataset_inputs_covmat(
        data: DataGroupSpec,
        fitthcovmat,
        t0set:(PDF, type(None)) = None,
        use_weights_in_covmat: bool = True,
        norm_threshold=None):
    """Like `covmat` except for a group of datasets"""
    if not use_weights_in_covmat:
        data = data.to_unweighted()

    loaded_data = data.load()

    if t0set:
        #Copy data to avoid chaos
        loaded_data = type(loaded_data)(loaded_data)
        log.debug("Setting T0 predictions for %s" % data)
        loaded_data.SetT0(t0set.load_t0())

    covmat = loaded_data.get_covmat()

    if fitthcovmat:
        loaded_thcov = fitthcovmat.load()
        ds_names = loaded_thcov.index.get_level_values(1)
        indices = np.in1d(ds_names, [ds.name for ds in data.datasets]).nonzero()[0]
        covmat += loaded_thcov.iloc[indices, indices].values
    if norm_threshold is not None:
        covmat = regularize_covmat(
            covmat,
            norm_threshold=norm_threshold
        )
    return covmat


@check_dataset_cuts_match_theorycovmat
def covmat(
    dataset:DataSetSpec,
    fitthcovmat,
    t0set:(PDF, type(None)) = None,
    use_weights_in_covmat: bool = True,
    norm_threshold=None,
    ):
    """Returns the covariance matrix for a given `dataset`. By default the
    data central values will be used to calculate the multiplicative contributions
    to the covariance matrix.

    The matrix can instead be constructed with
    the t0 proceedure if the user sets `use_t0` to True and gives a
    `t0pdfset`. In this case the central predictions from the `t0pdfset` will be
    used to calculate the multiplicative contributions to the covariance matrix.
    More information on the t0 procedure can be found here:
    https://arxiv.org/abs/0912.2276

    The user can specify `use_fit_thcovmat_if_present` to be True
    and provide a corresponding `fit`. If the theory covmat was used in the
    corresponding `fit` and the specfied `dataset` was used in the fit then
    the theory covariance matrix for this `dataset` will be added in quadrature
    to the experimental covariance matrix.

    Covariance matrix can be regularized according to
    `calcutils.regularize_covmat` if the user specifies `norm_threshold. This
    algorithm sets a minimum threshold for eigenvalues that the corresponding
    correlation matrix can have to be:

    1/(norm_threshold)^2

    which has the effect of limiting the L2 norm of the inverse of the correlation
    matrix. By default norm_threshold is None, to which means no regularization
    is performed.

    Parameters
    ----------
    dataset : DataSetSpec
        object parsed from the `dataset_input` runcard key
    fitthcovmat: None or ThCovMatSpec
        None if either `use_thcovmat_if_present` is False or if no theory
        covariance matrix was used in the corresponding fit
    t0set: None or PDF
        None if `use_t0` is False or a PDF parsed from `t0pdfset` runcard key
    use_weights_in_covmat: bool, default True
        Rescale the covmat by the dataset weights.
    norm_threshold: number
        threshold used to regularize covariance matrix

    Returns
    -------
    covmat : array
        a covariance matrix as a numpy array

    Examples
    --------

    >>> from validphys.api import API
    >>> inp = {
            'dataset_input': {'ATLASTTBARTOT'},
            'theoryid': 52,
            'use_cuts': 'no_cuts'
        }
    >>> cov = API.covmat(**inp)
    TODO: complete example
    """
    if not use_weights_in_covmat:
        dataset = dataset.to_unweighted()
    loaded_data = dataset.load()

    if t0set:
        #Copy data to avoid chaos
        loaded_data = type(loaded_data)(loaded_data)
        log.debug("Setting T0 predictions for %s" % dataset)
        loaded_data.SetT0(t0set.load_t0())

    covmat = loaded_data.get_covmat()
    if fitthcovmat:
        loaded_thcov = fitthcovmat.load()
        covmat += get_df_block(loaded_thcov, dataset.name, level=1)
    if norm_threshold is not None:
        covmat = regularize_covmat(
            covmat,
            norm_threshold=norm_threshold
        )
    return covmat


@check_pdf_is_montecarlo
def pdferr_plus_covmat(dataset, pdf, covmat):
    """For a given `dataset`, returns the sum of the covariance matrix given by
    `covmat` and the PDF error: a covariance matrix estimated from the
    replica theory predictions from a given monte carlo `pdf`

    Parameters
    ----------
    dataset: DataSetSpec
        object parsed from the `dataset_input` runcard key
    pdf: PDF
        monte carlo pdf used to estimate PDF error
    covmat: np.array
        experimental covariance matrix

    Returns
    -------
    covariance_matrix: np.array
        sum of the experimental and pdf error as a numpy array

    Examples
    --------

    `use_pdferr` makes this action be used for `covariance_matrix`

    >>> from validphys.api import API
    >>> from import numpy as np
    >>> inp = {
            'dataset_input': {'dataset' : 'ATLASTTBARTOT'},
            'theoryid': 53,
            'pdf': 'NNPDF31_nlo_as_0118',
            'use_cuts': 'nocuts'
        }
    >>> a = API.covariance_matrix(**inp, use_pdferr=True)
    >>> b = API.pdferr_plus_covmat(**inp)
    >>> np.allclose(a == b)
    True

    See Also
    --------
    covmat: Standard experimental covariance matrix
    """
    loaded_data = dataset.load()
    th = ThPredictionsResult.from_convolution(pdf, dataset, loaded_data=loaded_data)
    pdf_cov = np.cov(th._rawdata, rowvar=True)
    return pdf_cov + covmat


def pdferr_plus_dataset_inputs_covmat(data, pdf, dataset_inputs_covmat):
    """Like `pdferr_plus_covmat` except for an experiment"""
    # do checks get performed here?
    return pdferr_plus_covmat(data, pdf, dataset_inputs_covmat)


def dataset_inputs_sqrt_covmat(dataset_inputs_covariance_matrix):
    """Like `sqrt_covmat` but for an group of datasets"""
    return sqrt_covmat(dataset_inputs_covariance_matrix)


def fit_name_with_covmat_label(fit, fitthcovmat):
    """If theory covariance matrix is being used to calculate statistical estimators for the `fit`
    then appends (exp + th) onto the fit name for use in legends and column headers to help the user
    see what covariance matrix was used to produce the plot or table they are looking at.
    """
    if fitthcovmat:
        label = str(fit) + " (exp + th)"
    else:
        label = str(fit)
    return label


@table
@check_norm_threshold
def datasets_covmat_differences_table(
    each_dataset, datasets_covmat_no_reg, datasets_covmat_reg, norm_threshold):
    """For each dataset calculate and tabulate two max differences upon
    regularization given a value for `norm_threshold`:

    - max relative difference to the diagonal of the covariance matrix (%)
    - max absolute difference to the correlation matrix of each covmat

    """
    records = []
    for ds, reg, noreg in zip(
        each_dataset, datasets_covmat_reg, datasets_covmat_no_reg):
        cov_diag_rel_diff = np.diag(reg)/np.diag(noreg)
        d_reg = np.sqrt(np.diag(reg))
        d_noreg = np.sqrt(np.diag(noreg))
        corr_reg = reg/d_reg[:, np.newaxis]/d_reg[np.newaxis, :]
        corr_noreg = noreg/d_noreg[:, np.newaxis]/d_noreg[np.newaxis, :]
        corr_abs_diff = abs(corr_reg - corr_noreg)
        records.append(dict(
                dataset=str(ds),
                covdiff= np.max(abs(cov_diag_rel_diff- 1))*100, #make percentage
                corrdiff=np.max(corr_abs_diff)
            ))
    df = pd.DataFrame.from_records(records,
        columns=("dataset", "covdiff", "corrdiff"),
        index = ("dataset",)
        )
    df.columns = ["Variance rel. diff. (%)", "Correlation max abs. diff."]
    return df


@check_speclabels_different
@table
def dataspecs_datasets_covmat_differences_table(
    dataspecs_speclabel, dataspecs_covmat_diff_tables
):
    """For each dataspec calculate and tabulate the two covmat differences
    described in `datasets_covmat_differences_table`
    (max relative difference in variance and max absolute correlation difference)

    """
    df = pd.concat( dataspecs_covmat_diff_tables, axis=1)
    cols = df.columns.get_level_values(0).unique()
    df.columns = pd.MultiIndex.from_product((dataspecs_speclabel, cols))
    return df


groups_covmat_collection = collect(
    'dataset_inputs_covariance_matrix', ('group_dataset_inputs_by_metadata',)
)

groups_sqrt_covmat = collect(
    'dataset_inputs_sqrt_covmat',
    ('group_dataset_inputs_by_metadata',)
)

dataspecs_covmat_diff_tables = collect(
    "datasets_covmat_differences_table", ("dataspecs",)
)

fits_name_with_covmat_label = collect('fit_name_with_covmat_label', ('fits',))

datasets_covmat_no_reg = collect(
    "covariance_matrix", ("data", "no_covmat_reg"))

datasets_covmat_reg = collect(
    "covariance_matrix", ("data",))

datasets_covmat = collect('covariance_matrix', ('data',))

datasets_covariance_matrix = collect(
    'covariance_matrix',
    ('experiments', 'experiment',)
)
