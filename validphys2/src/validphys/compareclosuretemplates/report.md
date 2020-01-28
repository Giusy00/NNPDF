% Comparing closure test {@current fit@} and {@reference fit@}.

Fit summary
-----------

We are comparing:

  - {@ current fit @} (`{@ current fit_id @}`): {@ current description @}
  - {@ reference fit @} (`{@ reference fit_id @}`): {@ reference description @}

{@ summarise_fits @}

Underlying PDF Summary
----------------------
{@ summarise_closure_underlying_pdfs @}

Closures test estimators
-----------------------
## Bias by experiment
### Scatter Plot
{@ plot_fits_bootstrap_bias @}
### Table
{@ biases_table(show_total=True) @}

## $\phi$ by experiment
### Scatter Plot
{@ plot_phi_scatter_dataspecs @}
### Table
{@ fits_experiments_phi_table @}

## $\Delta_{\chi^{2}}$
{@ plot_delta_chi2 @}
### By experiment
{@ delta_chi2_table @}
