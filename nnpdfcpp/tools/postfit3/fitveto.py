"""
fitveto.py

Module for the determination of passing fit replicas.

Current active vetoes:
   Positivity - Replicas with FitInfo.is_positive == False
   ChiSquared - Replicas with ChiSquared > NSIGMA_DISCARD*StandardDev + Average
   ArclengthX - Replicas with ArcLengthX > NSIGMA_DISCARD*StandardDev + Average
"""

import numpy

# Threshold for distribution vetos
NSIGMA_DISCARD = 4


def available(mask):
    """ Converts a boolean mask into a list of passing elements """
    replicas = []
    for i in range(0, len(mask)):
        if mask[i]:
            replicas.append(i)
    return replicas


def distribution_veto(dist):
    """ For a given distribution (a list of floats), returns a boolean mask
    specifying the passing elements """
    replica_mask = [True for i in dist]
    while True:
        passing = [dist[i] for i in available(replica_mask)]
        average_pass = sum(passing)/len(passing)
        stderr_pass  = numpy.std(passing)
        # NOTE that this has always not been abs
        # i.e replicas that are lower than the average by more than 4std pass
        new_mask = [i - average_pass < NSIGMA_DISCARD*stderr_pass for i in dist]
        if sum(new_mask) == sum(replica_mask):
            break
        replica_mask = new_mask
    return replica_mask


def determine_vetoes(fitinfo: list):
    """ Assesses whether replica fitinfo passes standard NNPDF vetoes
    Returns a dictionary of vetoes and their passing boolean masks.
    Included in the dictionary is a 'Total' veto.
    """
    # Setup distributions to veto upon
    distributions = {"ChiSquared": [i.chi2 for i in fitinfo]}
    #TODO ensure that all replicas have the same amount of arclengths
    for i in range(0, len(fitinfo[0].arclengths)):
        distributions["ArcLength_"+str(i)] = [j.arclengths[i] for j in fitinfo]

    # Positivity veto
    vetoes = {"Positivity": [replica.is_positive for replica in fitinfo]}
    # Distribution vetoes
    for key in distributions:
        vetoes[key] = distribution_veto(distributions[key])

    vetoes["Total"] = [True for replica in fitinfo]
    for key in vetoes:
        vetoes["Total"] = [x & y for (x, y) in zip(vetoes["Total"], vetoes[key])]
    return vetoes
