Plotting non-trivial combinations of PDFs
=========================================

Suppose we are interested in plotting some (in general non-linear)
function of PDFs as a function of :math:`x`,
for example the strangeness fraction defined as

.. math::
   R_s = \frac{s + \bar{s}}{\bar{u} + \bar{d}}.

To achieve this we can make use of a PDF basis (the implementation
within ``validphys`` can be found in :py:mod:`validphys.pdfbases`).

We need to begin by assigning each parton a numerical index. This
convention is laid out by the PDG as follows:

==========  ===============
Index       Parton
==========  ===============
:math:`-6`  :math:`\bar{t}`
:math:`-5`  :math:`\bar{b}`
:math:`-4`  :math:`\bar{c}`
:math:`-3`  :math:`\bar{s}`
:math:`-2`  :math:`\bar{u}`
:math:`-1`  :math:`\bar{d}`
:math:`0`   :math:`g`
:math:`1`   :math:`d`
:math:`2`   :math:`u`
:math:`3`   :math:`s`
:math:`4`   :math:`c`
:math:`5`   :math:`b`
:math:`6`   :math:`t`
:math:`22`  :math:`\gamma`
:math:`21`  :math:`g`
==========  ===============

we see that for our quantity of interest, :math:`R_s`, we are interested
in indices :math:`-3`, :math:`3`, :math:`-2`, and :math:`-1`.
To achieve the desired plot, we must tell ``validphys`` what manipulation
it must make on the interpolation grids. The logic for grid manipulation
is handled by :py:meth:`validphys.pdfbases.Basis.apply_grid_values` which
is an abstract base class method and thus must be implemented manually
each time the user inherits from this class.
We shall define a function ``strange_fraction`` which will do exactly this.

The function should take in as arguments: ``func`` a callable which will
return ``grid_values``, a list of :math:`x` values ``xmat``, and a list of
:math:`Q` values in GeV ``qmat``. The object ``grid_values`` will be indexed as
``grid_values[replica_number][flavour][x][Q]``.

.. code:: python

  def strange_fraction(func, xmat, qmat):
      gv = func([-3, 3, -2, -1], xmat, qmat)
      sbar, s, ubar, dbar = (gv[:, [i], ...] for i in range(4))
      return (sbar + s) / (ubar + dbar)

However, ``validphys`` requires the notion of a :py:class:`validphys.pdfbases.Basis`
in order to perform plotting. For this we can decorate the above function using
:py:func:`validphys.pdfbases.scalar_function_transformation` which will instantiate
a new ``Basis`` inheriting :py:class:`validphys.pdfbases.ScalarFunctionTransformation`
object with ``strange_fraction`` as the ``apply_grid_values`` method.

The ``scalar_function_transformation`` function takes as an argument ``label``, which it will
use to label the plot title and axes. For our particular example, it will be sensible
to use ``Rs`` as the value for this argument.

In addition, it will be good practice to define this particular combination of PDFs as an element
of a particular basis. As such, we must give this particular element a label, which we will do so
by adding ``element_representations={"Rs": "R_{s}"}`` to the decorator arguments.

The final function is thus:

.. code:: python

   @scalar_function_transformation(label="Rs", element_representations={"Rs": "R_{s}"})
   def strange_fraction(func, xmat, qmat):
       gv = func([-3, 3, -2, -1], xmat, qmat)
       sbar, s, ubar, dbar = (gv[:, [i], ...] for i in range(4))
       return (sbar + s) / (ubar + dbar)

All that remains now is to construct the appropriate runcard, makes use of our newly
defined basis. One such example would be:

.. code:: yaml

  pdfs:
      - NNPDF31_nlo_as_0118

  Q: 10

  bases:
    - basis: strange_fraction

  template_text: |
      {@bases plot_pdfs@}

  actions_:
      - report(main=True)

