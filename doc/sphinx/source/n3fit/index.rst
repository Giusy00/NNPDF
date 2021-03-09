Fitting code: n3fit
===================

`n3fit` is the next generation fitting code for NNPDF developed by the N3PDF team.

We present a new regression model for the determination of parton distribution functions (PDF) using
techniques inspired from deep learning projects. In the context of the NNPDF methodology, we
implement a new efficient computing framework based on graph generated models for PDF
parametrization and gradient descent optimization. The best model configuration is derived from a
robust cross-validation mechanism through a hyperparametrization tune procedure. We show that
results provided by this new framework outperforms the current state-of-the-art PDF fitting
methodology in terms of best model selection and computational resources usage.

References: Towards a new generation of parton densities with deep learning models
`(hep-ph/1907.05075) <https://arxiv.org/abs/1907.05075>`_.


There are currently two example fits using the new code `n3fit` of the NNPDF 3.1 dataset uploaded to
the validphys server that can be obtained with `vp-get`, these correspond to hyperoptimized DIS and
Global runs with a chi2 similar to the corresponding `nnfit` server:

- Global: `PN3_Global_ada_150519`
- DIS: `PN3_DIS_130519`

In the sections below we provide a methodological overview about the `n3fit` design.

.. toctree::
   :maxdepth: 1

   methodology
   hyperopt
   runcard_detailed
