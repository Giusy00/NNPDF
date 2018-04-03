%NNPDF Report for fit {@ current fit @}

PDF plots
---------

{@with pdfnormalize@}
## {@normtitle@}
{@with basespecs@}
### {@basistitle@}
{@plot_pdfs@}
{@endwith@}
{@endwith@}

$\chi^2$
--------
{@fits_chi2_table@}


Experiment plots
---------------
{@with matched_datasets_from_dataspecs@}
[Detailed plots for dataset ' {@dataset_name@} ']({@dataset_report report@})
{@endwith@}
