================================
Hyperoptimization algorithm
================================


Idea
----

The main advantages of the points presented above consists in the possibility to test several models in a fraction of time in comparison to the `nnfit` framework.

This is of key importance for a proper hyper-parameter scan where everything is potentially interconnected.

Implementation
--------------

The hyperparameter scan capabilities are implemented using the hyperopt framework which systematically scans over a selection of parameter using Bayesian optimization and measures model performance to select the best architecture. The hyperopt library implements the tree-structured of Parzen estimator which is a robust sequential model based optimization approach `[SMBO] <https://en.wikipedia.org/wiki/Hyperparameter_optimization>`_.

We optimize on a combination of the best validation loss and stability of the fits. In other words, we select the architecture which produces the lowest validation loss after we trim those combinations which are deemed to be unstable.

Interpretation
--------------

While performing the hyperparameter scan we found that optimizing only looking at the validation loss produced results which would usually be considered overfitted: very low training and validation chi2 and complex replica patterns. Thanks to the high performance of the `n3fit` procedure the usual cross-validation algorithm used in the NNPDF framework was not enough to prevent overlearning for all architectures.

The cross-validation implemented in NNPDF is successful on avoiding the learning of the noise within a dataset. However, we observe that this choice is not enough to prevent overfitting due to correlations within points in a same dataset when using hyperopt with `n3fit`.

In order to eliminate architectures that allowed overlearning we proceed by including a testing set where the model generalization power is tested. This is a set of datasets where none of the points are used in the fitting either for training or validation. Defining the best appropriate test dataset for PDF fits is particularly challenging due to the nature of the model regression through convolutions. For the present results the test set is defined by removing from the training setdatasets with duplicate process type and smaller leading-order kinematic range coverage. We call the loss produced by the removed datasets "testing loss" and we use it as a third criterion (beyond stability and combined with the value of the validation loss) to discard combinations of hyperparameters.

.. math::
    L_{hyperopt} = \frac{1}{2} (L_{validation} + L_{training})


With this procedure we are able to find combinations of hyperparameters which produce good fits for which we are confident no obvious overfitting can be generated.
