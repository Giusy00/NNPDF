# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 19:27:44 2016

@author: Zahari Kassabov
"""
import pandas as pd

from reportengine.configparser import Config, ConfigError, named_element_of
from reportengine.utils import get_functions
from NNPDF import CommonData

from validphys.utils import split_by
from validphys.plotoptions import labelers, kintransforms, resulttransforms

default_labels = ('idat', 'k1', 'k2', 'k3')

labeler_functions = get_functions(labelers)
transform_functions = get_functions(kintransforms)
result_functions = get_functions(resulttransforms)


kinlabels_latex = CommonData.kinLabel_latex.asdict()

def get_plot_kinlabels(commondata):
    """Return the LaTex kinematic labels for a given Commondata"""
    #Since there is no 1:1 correspondence between latex keys and GetProc,
    #we match the first key such that the proc label starts with it.

    l = commondata.GetProc(0)
    key = next(k for k in kinlabels_latex if l.startswith(k))
    return kinlabels_latex[key]

def get_info(commondata, file=None, cuts=None):
    return PlotInfo.from_commondata(commondata, file=file, cuts=cuts)

class PlotInfo:
    def __init__(self, kinlabels, x=None ,extra_labels=None,
                 figure_by=None, line_by=None, kinematics_override=None,
                 result_transform=None, y_label=None, x_scale=None,
                 y_scale=None):
        self.kinlabels = kinlabels
        if x is None:
            x = 'idat'
        self.x = x
        self.extra_labels = extra_labels
        self.figure_by = figure_by
        self.line_by = line_by
        self.kinematics_override = kinematics_override
        self.result_transform = result_transform
        self.y_label = y_label
        self.x_scale = x_scale
        self.y_scale = y_scale

    def name_to_label(self, name):
        try:
            ix = ('k1', 'k2', 'k3').index(name)
        except ValueError:
            return name
        return self.kinlabels[ix]

    @property
    def xlabel(self):
        return self.name_to_label(self.x)



    def group_label(self, same_vals, groupby):
        if not groupby:
            return ''
        pieces = []
        for column, val in zip(groupby, same_vals):
            label = self.name_to_label(column)
            pieces.append('%s = %s' % (label, val))
        return '%s' % ' '.join(pieces)



    @classmethod
    def from_commondata(cls, commondata, file=None, cuts=None):

        if file:
            config = PlotConfigParser.from_yaml(file, commondata, cuts=cuts)
            plot_params = config.process_all_params()
        else:
            plot_params = {}

        if 'kinematics_override' in plot_params:
            kinlabels = plot_params['kinematics_override'].new_labels
        else:
            kinlabels = get_plot_kinlabels(commondata)
        return cls(kinlabels=kinlabels, **plot_params)


class PlotConfigParser(Config):

    def __init__(self, input_params ,commondata, cuts=None, **kwargs):
        self.commondata = commondata
        self.cuts = cuts
        super().__init__(input_params, **kwargs)

    @named_element_of('extra_labels')
    def parse_label(self, elems:list):
        if self.cuts is not None:
            elems = [elems[c] for c in self.cuts]
        if len(elems) != len(self.commondata):
            raise ConfigError("The number of elements in %s (%d) must be the same as "
                              "the number of points in the CommonData (%d)" %
                              (elems, len(elems), len(self.commondata)))
        return elems

    @staticmethod
    def resolve_name(val, extra_labels):
        if extra_labels is None:
            all_labels = list(default_labels)
        else:
            all_labels = list(extra_labels.keys()) + list(default_labels)
        if val in all_labels:
            return val
        if val in labeler_functions:
            extra_labels[val] = labeler_functions[val]
            return val

        raise ConfigError("Unknown label %s" % val, val, all_labels +
                          list(labeler_functions),
                              display_alternatives='all')

    def parse_x(self, x:str, extra_labels=None):
        return self.resolve_name(x, extra_labels)

    def parse_figure_by(self, gb:list, extra_labels=None):
        return [self.resolve_name(val, extra_labels) for val in gb]

    def parse_line_by(self, lb:list, extra_labels=None):
        return self.parse_figure_by(lb, extra_labels)

    def parse_kinematics_override(self, tr:str):
        if not tr in transform_functions:
            raise ConfigError("Unknown transform function '%s'" % tr, tr,
                              transform_functions)
        return transform_functions[tr]

    def parse_result_transform(self, tr:str):
        if not tr in result_functions:
            raise ConfigError("Unknown transform function '%s'" % tr, tr,
                              result_functions)
        return result_functions[tr]

    def parse_y_label(self, label:str):
        return label

    def _parse_scale(self, scale:str):
        if not (scale == 'linear' or scale=='log'):
            raise ConfigError("Scale must be 'linear' or 'log'")
        return scale

    def parse_x_scale(self, scale:str):
        return self._parse_scale(scale)

    def parse_y_scale(self, scale:str):
        return self._parse_scale(scale)


def kitable(commondata, info):
    def _expand(f,x):
        return f(**x)
    table = pd.DataFrame(commondata.get_kintable(), columns=default_labels[1:])
    table.index.name = default_labels[0]
    if info.kinematics_override:
        table = table.apply(lambda x: _expand(info.kinematics_override, x),
                            broadcast=True,
                            axis=1)
    #TODO: This is a little bit ugly. We want to call the functions
    #with all the
    #extra labels
    if info.extra_labels:
        funcs, vals = split_by(info.extra_labels.items(),
                               lambda x: callable(x[1]))
    else:
        funcs, vals = (), ()


    for label, value in vals:
        table[label] = value

    nreal_labels = len(table.columns)

    for label, func in funcs:
        #Pass only the "real" labels and not the derived functions
        table[label] = table.iloc[:,:nreal_labels].apply(lambda x: _expand(func,x), axis=1)

    return table

def transform_result(cv, error, kintable, info):
    if not info.result_transform:
        return cv, error
    f = info.result_transform
    newcv = []
    newerror = []
    for c, e, (_, labels) in zip(cv, error, kintable.iterrows()):
        nc,ne = f(c,e,**labels)
        newcv.append(nc)
        newerror.append(ne)
    return newcv, newerror
