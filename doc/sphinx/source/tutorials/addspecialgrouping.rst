.. _add_special_label:

How to add a new metadata group
===============================

in :ref:`data_specification` it is described how a user can define a custom
grouping at the level of the runcard, by specifying ``custom_group`` in each
``dataset_input`` and then specifying ``metadata_group=custom_group``. This is
great for testing, but what if you define a grouping that you want to reuse and
you want others to be able to use it easily as well?

The answer is to add that grouping to the metadata of the datasets, then
once the code is reinstalled the custom grouping will always be available.

Step 1: Choose a name for your grouping
---------------------------------------

The hardest part of any science research is to choose a name which is both
descriptive but also reflects your wit and intelligence. Failing the latter
try to choose a name which is suitably unique and possibly allows for newer
iterations in the future. An example of this would be the name given to the
grouping which groups data by the process type, according to the
`theory uncertainties paper <https://arxiv.org/abs/1906.10698>`__:
``nnpdf31_process``.
The suffix of 'process' indicates what the grouping is related to and the prefix
indicates that our hubris hasn't prevented us from permitting the possibility
that we can come up with a more
refined version of this grouping in the future, which can have its own prefix.

Remember that each group within the grouping will also need its own name, so
try not to exhaust yourself too much before coming up with the group names as
well.

The metadata file is your canvas but with great power comes great
responsibility.

Step 2: Add the grouping and group name to the metadata (PLOTTING) file
-----------------------------------------------------------------------

.. note::
   Throughout this section the PLOTTING file may be referred to as the
   metadata.

Once you have a name for your grouping and a name for each of your groups you
can add these as key, value pairs to the PLOTTING files of each dataset for
which you want to be able to apply this grouping. The PLOTTING files are
found in the git repository in ``nnpdfcpp/data/commondata`` and follow the naming
convention ``PLOTTING_<DATASET NAME>.yaml``.

It's a good idea to add
this to the PLOTTING file of *all* datasets if possible, or else anybody
who tries to use your grouping in the future is sure to get very frustrated.

Say I called my grouping ``nnpdf40_process`` and the group which a particular
dataset belongs to is ``DIS NC`` then I would add the following the PLOTTING file

.. code:: yaml

    nnpdf40_process: DIS NC

At this stage it's worth pointing out that it's best that both grouping
and group names are naturally interpretable as a string.

Step 3: Make sure the grouping is parsed from the metadata
----------------------------------------------------------

A perhaps surprising step in this tutorial is that you must tell the part of
the code which parses the metadata about your new key or else it will get
very upset.

This involves going into :py:mod:`validphys.plotoptions.core` and adding a
special ``parse`` method to
:py:class:`validphys.plotoptions.core.PlotConfigParser`. There are pre-existing
examples that you can use as templates. For the example used above I would have
to add:

.. code:: python

    def parse_nnpdf40_process(self, proc: str):
        return proc

the name of the variable (in this case ``proc``) is unimportant, however the
type hint in the signature should be ``str`` to confirm that the key is read
from the config file as a string.

.. note::
   The reason the group name should be a string is because it is sometimes
   passed to the c++ code through the swig interface, which is very strict
   about the typing you use.

in addition to this, you must add the new grouping to
:py:class:`validphys.plotoptions.core.PlotInfo` as a keyword arguments of
the ``__init__`` function and subsequently as an attribute of the class
as follows:

.. code:: python

    class PlotInfo:
        def __init__(
            self,
            kinlabels,
            dataset_label,
            *,
    ...
            nnpdf40_process,
    ...
        self.nnpdf40_process = nnpdf40_process

The keyword argument must be placed after the asterix as per standard ``python``
syntax.

.. note::
    It is possible to give a default value by setting a default in the
    signature of the function. If you do not set a default then every single dataset
    **must** have that key in its metadata. You may observe that ``experiment``
    and ``nnpdf31_process`` are required keys. Any dataset which does not
    feature these keys in its metadata can be considered broken or not fully
    implemented.

Step 4: recompile, reinstall and profit
---------------------------------------

Now everything is in place, you just need to recompile and reinstall the code
which will put the updated metadata files in your environment. Following the
example used throughout I can now specify
``metadata_group: nnpdf40_process`` and any action which leverages the
metadata grouping mechanism will now group datasets by the new key.
