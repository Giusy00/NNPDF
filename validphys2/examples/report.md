NNPDF Report
============

{@ description  @}


PDF plots
---------

{@ plot_pdfs @}

**Normalized**

{@normalize plot_pdfs  @}


Train-valid split
------------------

{@ plot_training_validation @}

$Chi2$
-------

{@ theory::pdfs experiments_chi2_table @}

Experiment plots
---------------

{@ with datanorm::theory::experiments::experiment  @}
{@ plot_fancy @}

