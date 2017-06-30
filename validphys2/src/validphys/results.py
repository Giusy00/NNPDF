# -*- coding: utf-8 -*-
"""
results.py

Tools to obtain theory predictions and basic statistical estimators.
"""
from __future__ import generator_stop

from collections import OrderedDict, namedtuple, Sequence
import itertools
import logging

import numpy as np
import scipy.linalg as la
import pandas as pd

from NNPDF import ThPredictions, CommonData
from NNPDF.experiments import Experiment
from reportengine.checks import require_one, remove_outer, check_not_empty
from reportengine.table import table
from reportengine import collect

from validphys.checks import assert_use_cuts_true
from validphys.core import DataSetSpec, PDF, ExperimentSpec
from validphys.calcutils import all_chi2, central_chi2

log = logging.getLogger(__name__)



class Result: pass


#TODO: Eventually,only one of (NNPDFDataResult, StatsResult) should survive
class NNPDFDataResult(Result):
    """A result fills its values from a libnnpf data object"""
    def __init__(self, dataobj):
        self._central_value = dataobj.get_cv()

    @property
    def central_value(self):
        return self._central_value

    def __len__(self):
        return len(self.central_value)

class StatsResult(Result):
    def __init__(self, stats):
        self.stats = stats

    @property
    def central_value(self):
        return self.stats.central_value()

    @property
    def std_error(self):
        return self.stats.std_error()




class DataResult(NNPDFDataResult):

    def __init__(self, dataobj):
        super().__init__(dataobj)
        self._covmat = dataobj.get_covmat()
        self._sqrtcovmat = dataobj.get_sqrtcovmat()

    @property
    def label(self):
        return "Data"

    @property
    def std_error(self):
        return np.sqrt(np.diag(self.covmat))

    @property
    def covmat(self):
        return self._covmat

    @property
    def sqrtcovmat(self):
        """Lower part of the Cholesky decomposition"""
        return self._sqrtcovmat


class ThPredictionsResult(NNPDFDataResult):

    def __init__(self, dataobj, stats_class, label=None):
        self.stats_class = stats_class
        self.label = label
        self._std_error = dataobj.get_error()
        self._rawdata = dataobj.get_data()
        super().__init__(dataobj)

    @property
    def std_error(self):
        return self._std_error

    @staticmethod
    def make_label(pdf, dataset):
        """Deduce a reasonsble label for the result based on pdf and dataspec"""
        th = dataset.thspec
        if hasattr(pdf,'label'):
            if hasattr(th, 'label'):
                label = ' '.join((pdf.label, th.label))
            else:
                label = pdf.label
        elif hasattr(th, 'label'):
            label = th.label
        else:
            label = ('%s@<Theory %s>' % (pdf, th.id))
        return label


    @classmethod
    def from_convolution(cls, pdf, dataset, loaded_pdf=None, loaded_data=None):
        if loaded_pdf  is None:
            loaded_pdf = pdf.load()
        if loaded_data is None:
            loaded_data = dataset.load()
        th_predictions = ThPredictions(loaded_pdf, loaded_data)


        label = cls.make_label(pdf, dataset)


        return cls(th_predictions, pdf.stats_class, label)

class PositivityResult(StatsResult):
    @classmethod
    def from_convolution(cls, pdf, posset):
        loaded_pdf = pdf.load()
        loaded_pos = posset.load()
        data = loaded_pos.GetPredictions(loaded_pdf)
        stats = pdf.stats_class(data.T)
        return cls(stats)

    @property
    def rawdata(self):
        return self.stats.data



def experiments_index(experiments):
    """Return an empy dataframe with index
       per experiment per dataset per point"""
    records = []
    for exp_index, experiment in enumerate(experiments):
        loaded_exp = experiment.load()
        set_lens = [len(loaded_exp.GetSet(i)) for i in
                    range(len(experiment.datasets))]
        #TODO: This code is very ugly and slow...
        cum_sum = [sum(set_lens[:i+1]) for i in range(len(set_lens))]
        curr_ds_domain = iter(enumerate(cum_sum))
        index_offset = 0
        ds_id, curr_ds_len = next(curr_ds_domain)
        for index in range(cum_sum[-1]):
            if index >= curr_ds_len:
                index_offset = curr_ds_len
                ds_id, curr_ds_len = next(curr_ds_domain)
            dataset = experiment.datasets[ds_id]

            records.append(OrderedDict([
                                 ('experiment', str(experiment.name)),
                                 ('dataset', str(dataset.name)),
                                 ('id', index - index_offset),
                                  ]))

    columns = ['experiment', 'dataset', 'id']
    df = pd.DataFrame(records, columns=columns)
    df.set_index(columns, inplace=True)
    return df.index

#TODO: Use collect to calculate results outside this
@table
def experiment_result_table(experiments, pdf, experiments_index):
    """Generate a table containing the data central value, the central prediction,
    and the prediction for each PDF member."""

    result_records = []
    for exp_index, experiment in enumerate(experiments):
        loaded_exp = experiment.load()



        data_result = DataResult(loaded_exp)
        th_result = ThPredictionsResult.from_convolution(pdf, experiment,
                                                         loaded_data=loaded_exp)


        for index in range(len(data_result.central_value)):
            replicas = (('rep_%05d'%(i+1), th_result._rawdata[index,i]) for
                        i in range(th_result._rawdata.shape[1]))

            result_records.append(OrderedDict([
                                 ('data_central', data_result.central_value[index]),
                                 ('theory_central', th_result.central_value[index]),
                                  *replicas
                                 ]))

    if not result_records:
        log.warn("Empty records for experiment results")
        return pd.DataFrame()
    df =  pd.DataFrame(result_records, columns=result_records[0].keys(),
                       index=experiments_index)
    return df

@table
def experiments_covmat(experiments, experiments_index):
    """Export the covariance matrix for the experiments. It exports the full
    (symmetric) matrix, with the 3 first rows and columns being:

        - experiment name

        - dataset name

        - index of the point within the dataset.
    """
    data = np.zeros((len(experiments_index),len(experiments_index)))
    df = pd.DataFrame(data, index=experiments_index, columns=experiments_index)
    for experiment in experiments:
        name = experiment.name
        loaded_exp = experiment.load()
        mat = loaded_exp.get_covmat()
        df.loc[[name],[name]] = mat
    return df

@table
def experiments_invcovmat(experiments, experiments_index):
    """Compute and export the inverse covariance matrix.
    Note that this inverts the matrices with the LU method which is
    suboptimal."""
    data = np.zeros((len(experiments_index),len(experiments_index)))
    df = pd.DataFrame(data, index=experiments_index, columns=experiments_index)
    for experiment in experiments:
        name = experiment.name
        loaded_exp = experiment.load()
        #Improve this inversion if this method tuns out to be important
        mat = la.inv(loaded_exp.get_covmat())
        df.loc[[name],[name]] = mat
    return df

@table
def closure_pseudodata_replicas(experiments, pdf, nclosure:int,
                                experiments_index, nnoisy:int=0):
    """Generate closure pseudodata replicas from the given pdf.

    nclosure: Number of Level 1 pseudodata replicas.

    nnoisy:   Number of Level 2 replicas generated out of each pseudodata replica.

    The columns of the table are of the form (clos_0, noise_0_n0 ..., clos_1, ...)
    """

    #TODO: Do this somewhere else
    from NNPDF import randomgenerator
    randomgenerator.RandomGenerator.InitRNG(0,0)
    data = np.zeros((len(experiments_index), nclosure*(1+nnoisy)))

    cols = []
    for i in range(nclosure):
        cols += ['clos_%04d'%i, *['noise_%04d_%04d'%(i,j) for j in range(nnoisy)]]


    loaded_pdf = pdf.load()

    for exp in experiments:
        #Since we are going to modify the experiments, we copy them
        #(and work on the copies) to avoid all
        #sorts of weirdness with other providers. We don't want this to interact
        #with ExperimentSpec at all, because it could do funny things with the
        #cache when calling load(). We need to copy this yet again, for each
        # of the noisy replicas.
        closure_exp = Experiment(exp.load())

        #TODO: This is probably computed somewhere else... All this code is
        #very error prone.
        #The predictions are for the unmodified experiment.
        predictions = [ThPredictions(loaded_pdf, d.load()) for d in exp]


        exp_location = experiments_index.get_loc(closure_exp.GetExpName())

        index = itertools.count()
        for i in range(nclosure):
            #Generate predictions with experimental noise, a different for
            #each closure set.
            closure_exp.MakeClosure(predictions, True)
            data[exp_location, next(index)] = closure_exp.get_cv()
            for j in range(nnoisy):
                #If we don't copy, we generate noise on top of the noise,
                #which is not what we want.
                replica_exp = Experiment(closure_exp)
                replica_exp.MakeReplica()

                data[exp_location, next(index)] = replica_exp.get_cv()


    df = pd.DataFrame(data, index=experiments_index,
                      columns=cols)

    return df


def results(dataset:(DataSetSpec), pdf:PDF, t0set:(PDF, type(None))=None):
    """Tuple of data and theory results for a single pdf.
    The theory is specified as part of the dataset.
    An experiment is also allowed.
    (as a result of the C++ code layout)."""

    data = dataset.load()

    if t0set:
        #Copy data to avoid chaos
        data = type(data)(data)
        log.debug("Setting T0 predictions for %s" % dataset)
        data.SetT0(t0set.load_t0())

    return DataResult(data), ThPredictionsResult.from_convolution(pdf, dataset,
                                                 loaded_data=data)

def experiment_results(experiment, pdf:PDF, t0set:(PDF, type(None))=None):
    """Like `results` but for a whole experiment"""
    return results(experiment, pdf, t0set)

#It's better to duplicate a few lines than to complicate the logic of
#``results`` to support this.
#TODO: The above comment doesn't make sense after adding T0. Deprecate this
def pdf_results(dataset:(DataSetSpec,  ExperimentSpec), pdfs:Sequence, t0set:(PDF, type(None))):
    """Return a list of results, the first for the data and the rest for
    each of the PDFs."""

    data = dataset.load()

    if t0set:
        #Copy data to avoid chaos
        data = type(data)(data)
        log.debug("Setting T0 predictions for %s" % dataset)
        data.SetT0(t0set.load_t0())

    th_results = []
    for pdf in pdfs:
        th_result = ThPredictionsResult.from_convolution(pdf, dataset,
                                                         loaded_data=data)
        th_results.append(th_result)


    return (DataResult(data), *th_results)

@require_one('pdfs', 'pdf')
@remove_outer('pdfs', 'pdf')
def one_or_more_results(dataset:(DataSetSpec, ExperimentSpec),
                        pdfs:(type(None), Sequence)=None,
                        pdf:(type(None), PDF)=None,
                        t0set:(PDF, type(None))=None):
    """Generate a list of results, where the first element is the data values,
    and the next is either the prediction for pdf or for each of the pdfs.
    Which of the two is selected intelligently depending on the namespace,
    when executing as an action."""
    if pdf:
        return results(dataset, pdf, t0set)
    else:
        return pdf_results(dataset, pdfs, t0set)
    raise ValueError("Either 'pdf' or 'pdfs' is required")


Chi2Data = namedtuple('Chi2Data', ('replica_result', 'central_result', 'ndata'))

def abs_chi2_data(results):
    """Return a tuple (member_chi², central_chi², numpoints) for a
    given dataset"""
    data_result, th_result = results

    chi2s = all_chi2(results)

    central_result = central_chi2(results)

    return Chi2Data(th_result.stats_class(chi2s[:, np.newaxis]),
                    central_result, len(data_result))

def abs_chi2_data_experiment(experiment_results):
    """Like `abs_chi2_data` but for a whole experiment"""
    return abs_chi2_data(experiment_results)

def _chs_per_replica(chs):
    th, _, l = chs
    return th.data.ravel()/l


@table
def experiments_chi2_table(experiments, pdf, experiments_chi2,
                           each_dataset_chi2):
    """Return a table with the chi² to the experiments and each dataset on
    the experiments."""
    dschi2 = iter(each_dataset_chi2)
    records = []
    for experiment, expres in zip(experiments, experiments_chi2):
        stats = chi2_stats(expres)
        stats['experiment'] = experiment.name
        records.append(stats)
        for dataset, dsres in zip(experiment, dschi2):
            stats = chi2_stats(dsres)
            stats['experiment'] = dataset.name
            records.append(stats)
    return pd.DataFrame(records)

@table
def correlate_bad_experiments(experiments, replica_data, pdf):
    """Generate a table for each replica with entries
    ("Replica_mean_chi2", "Worst_dataset","Worst_dataset_chi2")."""
    datasets = [ds for exp in experiments for ds in exp.datasets]
    mchi2 = [0.5*(val.training + val.validation) for val in replica_data]

    chs = [_chs_per_replica(abs_chi2_data(results(ds, pdf))) for ds in datasets]
    worst_indexes = np.argmax(chs, axis=0)
    mchi2 = np.mean(chs, axis=0)
    print(worst_indexes)
    worst_values = np.max(chs, axis=0)
    worst_ds = [datasets[i].name for i in worst_indexes]
    v = np.array([mchi2, worst_ds, worst_values])
    print(v)
    df = pd.DataFrame(v.T,
                      index=np.arange(1, len(pdf)),
                      columns=["Replica_mean_chi2", "Worst_dataset",
                      "Worst_dataset_chi2"])
    df.sort_values(df.columns[0], inplace=True, ascending=False)
    return df

@assert_use_cuts_true
@table
def closure_shifts(experiments_index, fit, use_cuts, experiments):
    """Save the differenve between the fitted data and the real commondata
    values.

    Actually shifts is what should be saved in the first place, rather than
    thi confusing fiddling with Commondata, but until we can implement this at
    the C++ level, we just dave it here.
    """
    name, fitpath = fit
    result = np.zeros(len(experiments_index))
    for experiment in experiments:
        for dataset in experiment:
            dspath = fitpath/'filter'/dataset.name
            cdpath = dspath/("DATA_" + dataset.name + ".dat")
            try:
                syspath = next( (dspath/'systypes').glob('*.dat'))
            except StopIteration as e:
                raise FileNotFoundError("No systype "
                "file found in filter folder %s" % (dspath/'systypes')) from e
            cd = CommonData.ReadFile(str(cdpath), str(syspath))
            loc = experiments_index.get_loc((experiment.name, dataset.name))
            result[loc] = cd.get_cv() - dataset.load().get_cv()
    return pd.DataFrame(result, index=experiments_index)




def positivity_predictions(pdf, posdataset):
    """Return an object containing the values of the positivuty observable."""
    return PositivityResult.from_convolution(pdf, posdataset)

positivity_predictions_for_pdfs = collect(positivity_predictions, ('pdfs',))

def count_negative_points(possets_predictions):
    """Return the number of replicas with negative predictions for each bin
    in the positivity observable."""
    return np.sum([(r.rawdata < 0).sum(axis=1) for r in possets_predictions], axis=0)


chi2_stat_labels = {
    'central_mean': r'$<\chi^2_{0}>_{data}$',
    'npoints': r'$N_{data}$',
    'perreplica_mean': r'$\left< \chi^2 \right>_{rep,data}$',
    'perreplica_std': r'$\left<std_{rep}(\chi^2)\right>_{data}$',
    'chi2_per_data': r'$\frac{\chi^2}{N_{data}}$'
}

def chi2_stats(abs_chi2_data):
    """Compute severa estimators from the chi²:

     - central_mean

     - npoints

     - perreplica_mean

     - perreplica_std

     - chi2_per_data
    """
    rep_data, central_result, npoints = abs_chi2_data
    m = central_result.mean()
    rep_mean = rep_data.central_value().mean()
    return OrderedDict([
            ('central_mean'        ,  m),
            ('npoints'             , npoints),
            ('chi2_per_data', m/npoints),
            ('perreplica_mean', rep_mean),
            ('perreplica_std',  rep_data.std_error().mean()),
           ])


@table
def dataset_chi2_table(chi2_stats, dataset):
    """Show the chi² estimators for a given dataset"""
    return pd.DataFrame(chi2_stats, index=[dataset.name])


@table
def fits_experiments_chi2_table(fits, fits_experiments, fits_experiment_chi2_data):
    """A table with the chi2 for each included experiment in the fits,
    computed with the theory corresponding to each fit"""
    dfs = []
    for fit, experiments, exps_chi2 in zip(fits, fits_experiments, fits_experiment_chi2_data):
        records = []
        for experiment, exp_chi2 in zip(experiments, exps_chi2):
            records.append(dict(
                experiment=str(experiment),
                npoints=exp_chi2.ndata,
                mean_chi2 = exp_chi2.central_result.mean()/exp_chi2.ndata
            ))
        df = pd.DataFrame.from_records(records,
                 columns=('experiment', 'npoints', 'mean_chi2'),
                 index = ('experiment', )
             )
        df.columns = pd.MultiIndex.from_product(([str(fit)], ['ndata', '$\chi^2/ndata$']))
        dfs.append(df)
    res =  pd.concat(dfs, axis=1)
    return res


@table
def fits_datasets_chi2_table(fits, fits_experiments, fits_chi2_data):
    """A table with the chi2 for each included dataset in the fits, computed
    with the theory corresponding to the fit. The result are indexed in two
    levels by experiment and dataset."""

    chi2_it = iter(fits_chi2_data)

    dfs = []
    for fit, experiments in zip(fits, fits_experiments):
        records = []
        for experiment in experiments:
            for dataset, chi2 in zip(experiment.datasets, chi2_it):
                records.append(dict(
                    experiment=str(experiment),
                    dataset=str(dataset),
                    npoints=chi2.ndata,
                    mean_chi2 = chi2.central_result.mean()/chi2.ndata
                ))

        df = pd.DataFrame.from_records(records,
                 columns=('experiment', 'dataset', 'npoints', 'mean_chi2'),
                 index = ('experiment', 'dataset')
             )
        df.columns = pd.MultiIndex.from_product(([str(fit)], ['ndata', '$\chi^2/ndata$']))
        dfs.append(df)
    return pd.concat(dfs, axis=1)

@table
def fits_chi2_table(fits_experiments_chi2_table, fits_datasets_chi2_table):
    """Show the chi² of each and number of points of each dataset and experiment
    of each fit,
    computed with the theory corresponding to the fit. Dataset that are not
    included in some fit appear as "Not Fitted". This is itended for display
    purposes."""
    lvs = fits_experiments_chi2_table.index
    expanded_index = pd.MultiIndex.from_product((lvs, ["Total"]))
    edf = fits_experiments_chi2_table.set_index(expanded_index)
    ddf = fits_datasets_chi2_table
    dfs = []
    #TODO: Better way to do the merge preserving the order?
    for lv in lvs:
        dfs.append(pd.concat((edf.loc[lv],ddf.loc[lv]), copy=False, axis=0))

    res = pd.concat(dfs, axis=0, keys=lvs)
    return res.fillna("Not Fitted")

def total_experiments_chi2(experiments_chi2):
    """Return  the total chi²/ndata for the combination of all
    experiments."""
    val = 0
    n = 0
    for cd in experiments_chi2:
        val += cd.central_result
        n += cd.ndata
    return val/n

@table
@check_not_empty('experiments')
def perreplica_chi2_table(experiments, experiments_chi2):
    """Chi² per point for each replica for each experiment.
    Also outputs the total chi² per replica.
    The columns come in two levels: The first is the name of the experiment,
    and the second is the number of points."""

    chs = experiments_chi2
    total_chis = np.zeros((len(experiments) + 1, 1+ len(chs[0].replica_result.error_members())))
    ls = []
    for i,ch in enumerate(chs, 1):
        th, central, l = ch
        total_chis[i]= [central, *th.error_members()]
        ls.append(l)
    #total_chis/=total_l
    total_chis[0] = np.sum(total_chis[1:,:], axis=0)
    total_n = np.sum(ls)
    total_chis[0]/= total_n
    total_chis[1:,:]/= np.array(ls)[:, np.newaxis]

    columns = pd.MultiIndex.from_arrays(
            (['Total', *[str(exp) for exp in experiments]],
             [total_n, *ls]), names=['name', 'npoints'])
    return pd.DataFrame(total_chis.T, columns =columns)

@table
def theory_description(theoryid):
    """A table with the theory settings."""
    return pd.DataFrame(pd.Series(theoryid.get_description()), columns=[theoryid])

experiments_results = collect(experiment_results, ('experiments',))
each_dataset_results = collect(results, ('experiments', 'experiment'))

experiments_chi2 = collect(abs_chi2_data_experiment, ('experiments',))
each_dataset_chi2 = collect(abs_chi2_data, ('experiments', 'experiment'))

#These are convenient ways to iterate and extract varios data from fits
fits_chi2_data = collect(abs_chi2_data, ('fits', 'fitcontext', 'experiments', 'experiment'))
fits_experiment_chi2_data = collect('experiments_chi2', ('fits', 'fitcontext'))
fits_total_chi2 = collect('total_experiments_chi2', ('fits', 'fitcontext'))

fits_total_chi2_for_experiments = collect('total_experiment_chi2',
                                          ('fits', 'fittheoryandpdf',
                                           'expspec', 'experiment'))


fits_experiments = collect('experiments', ('fits', 'fitcontext'))
fits_pdfs = collect('pdf', ('fits', 'fitpdf'))


#Dataspec is so
dataspecs_results = collect('results', ('dataspecs',))
dataspecs_chi2_data = collect(abs_chi2_data, ('dataspecs', 'experiments', 'experiment'))
dataspecs_experiment_chi2_data = collect('experiments_chi2', ('dataspecs',))
dataspecs_total_chi2 = collect('total_experiments_chi2', ('dataspecs',))

dataspecs_speclabel = collect('speclabel', ('dataspecs',), element_default=None)
dataspecs_cuts = collect('cuts', ('dataspecs',))
dataspecs_experiments = collect('experiments', ('dataspecs',))
dataspecs_dataset = collect('dataset', ('dataspecs',))
dataspecs_commondata = collect('commondata', ('dataspecs',))
dataspecs_pdfs = collect('pdf', ('dataspecs',))
