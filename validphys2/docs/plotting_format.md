NNPDF plottng format
====================

A "plotting file" determines how the predictions for given dataset
should be represented on a plot. The plotting files should be
considered part of the implementation of the dataset, and should be
read by various tools that want to sensibly represent the data.

Naming convention
-----------------

Given a dataset  labeled `<DATASET>`, every file found in the
`commondata` folder (`nnpdfcpp/data/commondata`) that matches the
regular expression

````
PLOTTING_<DATASET>(_.*)?\.ya?ml
````

(that is, the string `"PLOTTING_"` followed by the name of the
dataset, possibly followed by an underscore and an arbitrary string,
and ending in `.yaml` or `.yml`) is to be considering a plotting file
for that dataset. In case there is more than one such file, plots will
be generated for both.

For example, given the dataset "HERA1CCEP", the following are valid
plotting file names:

````
PLOTTING_HERA1CCEP.yml
PLOTTING_HERA1CCEP_TEST.yaml
PLOTTING_HERA1CCEP_OTHER.yaml
````

And the following are invalid and will be ignored:

````
PLOTTING_HERA1CCEP.txt
PLOTTING_HERA1CCEPTEST.yaml
````

Format
------

The plot file specifies the variable as a function of which the data
is to be plotted (in the  *x* axis) as well as the variables as
a function of which the data will be split in different lines in the
same figure or in different figures. The possible variables
('*labels*') are described below.

The format also allows to control several plotting properties, such
that whether to use log scale, or the axes labels.

# Labels

The kinematic variables  are in principle deduced from the type of
process declared for the data. They are deduced from the starting
substring of the process type.  Currently they are:


````
'DIS': ('$x$', '$Q^2$', '$y$'),
'DYP': ('$y$', '$M^2$', '$\\sqrt{s}$'),
'EWJ_JPT': ('$p_T$', '$M^2$', '$\\sqrt{s}$'),
'EWJ_JRAP': ('$\\eta/y$', '$M^2$', '$\\sqrt{s}$'),
'EWJ_MLL': ('$M_{ll}$', '$M_{ll}^2$', '$\\sqrt{s}$'),
'EWJ_PT': ('$p_T$', '$M^2$', '$\\sqrt{s}$'),
'EWJ_RAP': ('$\\eta/y$', '$M^2$', '$\\sqrt{s}$'),
'EWK_MLL': ('$M_{ll}$', '$M_{ll}^2$', '$\\sqrt{s}$'),
'EWK_PT': ('$p_T$', '$M^2$', '$\\sqrt{s}$'),
'EWK_RAP': ('$\\eta/y$', '$M^2$', '$\\sqrt{s}$'),
'HIG_RAP': ('$y$', '$M_H^2$', '$\\sqrt{s}$'),
'HQP_MQQ': ('$M^{QQ}$', '$\\mu^2$', '$\\sqrt{s}$'),
'HQP_PTQ': ('$p_T^Q$', '$\\mu^2$', '$\\sqrt{s}$'),
'HQP_PTQQ': ('$p_T^{QQ}$', '$\\mu^2$', '$\\sqrt{s}$'),
'HQP_YQ': ('$y^Q$', '$\\mu^2$', '$\\sqrt{s}$'),
'HQP_YQQ': ('$y^{QQ}$', '$\\mu^2$', '$\\sqrt{s}$'),
'INC': ('$0$', '$\\mu^2$', '$\\sqrt{s}$'),
'JET': ('$\\eta$', '$p_T^2$', '$\\sqrt{s}$'),
'PHT': ('$\\eta_\\gamma$', '$E_{T,\\gamma}^2$', '$\\sqrt{s}$')
````

This mapping is declared as `CommonData.kinLabel_latex` in the C++
code.

The three kinematic variables are referred to as 'k1', 'k2' and 'k3'
in the plot files. For example, for DIS processes, 'k1' refers to 'x',
'k2' to 'Q', and 'k3 to 'y'. It is possible to define
a **kinematics_override** key. The value must be a function defined
in:

`validphys2/src/validphys/plotoptions/kintransforms.py`

The function must take three parameters: `(k1, k2 k3)` as defined in the
dataset implementation, and return three new values `(k1', k2', k3')`
which are the "transformed" kinematical variables, which will be used
for plotting purposes every time the kinematic variables k1, k2 and k3
are referred to. The function must implement a "new_labels" decorator,
specifying the names for the new variables. An example of such
transform is:

````
@utils.new_labels('$2k_1$', '$3k_1$', '$4k_3$')
def dummy_transform(k1,k2,k3):
    return k1*2, k2*3, k3*4
````


Additional labels can be specified by declaring an **extra_labels**
key in the plotting file, and specifying for each new label a value
for each point in the dataset.

For example:

````
extra_labels:
    idat2bin:  [0, 0, 0, 0, 0, 0, 0, 0, 100, 100, 100, 100, 100, 200, 200, 200, 300, 300, 300, 400, 400, 400, 500, 500, 600, 600, 700, 700, 800, 800, 900, 1000, 1000, 1100]
````

defines one label where the values for each of the datapoints are
given in the list.

Finally, every function defined in:


`validphys2/src/validphys/plotoptions/labelers.py`

is a valid label. These functions take as keyword arguments the
(possibly transformed) kinematical variables, as well as any extra
label declared in the plotting file. For example, one might declare:

````
def high_xq(k1, k2, k3, **kwargs):
    return k1 > 1e-2 and k2 > 1000

````

Note that it is convenient to always declare the '\*\*kwargs'
parameter so that the code doesn't crash when the function is called
with extra arguments. Similarly to the kinematics transforms, it is
possible to decorate them with a `@label` describing a nicer latex
label than the function name. For example:

````
@label(r"$I(x>10^{-2})\times I(Q > 1000 GeV)$")
def high_xq(k1, k2, k3, **kwargs):
    return (k1 > 1e-2) & (k2 > 1000)

````

# Plotting and grouping

The variable as function of which the data is plotted, is simply
declared as 

````
x: <label>
````

For example:

````
x: k1
````

If a `line_by` key is specified, variables with different values for
each of the labels listed, will be represented as different lines. For
example,

````
line_by:
  - k2
````

for DIS would mean that the data in the same Q bin is plotted in the
same line.

Similarly, it is possible to define an `figure_by` key: Points
with different values for the listed keys will be split across
separated figure. For example:

````
figure_by:
  - idat2bin
  - high_xq
````

# Transforming the result

By default the y axis represents the central value and error. However
it is possible to define a results_transform in the plotting file:

````
result_transform: qbinexp
````

The value must be a function declared in

`validphys2/src/validphys/plotoptions/results_transform.py`

taking the error, the central value as well as all the labels, and
returning a new error and central value. For example:

````
def qbinexp(cv, error, **labels):
    q = labels['k2']
    qbin = bins(q)
    return 10**qbin*cv, 10**qbin*error
````

# Plotting options

Several plotting options can be specified.
These include

 - x/y_scale: 'linear' or 'log'.
 - x/y_label: Any string, possibly latex formatted. Note that the
	 x_label will be deduced automatically.

Example
------

A complete example (all keys are optional) looks like this:

``` 
x: k3
kinematics_override: dummy_transform #defined in transforms.py
line_by:
  - k2

figure_by:
  - idat2bin #defined below
  - high_xq  #defined in labelers.py

extra_labels:
    idat2bin:  [0, 0, 0, 0, 0, 0, 0, 0, 100, 100, 100, 100, 100, 200, 200, 200, 300, 300, 300, 400, 400, 400, 500, 500, 600, 600, 700, 700, 800, 800, 900, 1000, 1000, 1100]

````
