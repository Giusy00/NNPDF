"""
test_rebuilddata.py

filter some simple closure data and then check that rebuild data runs on it
and produces sensible results

"""

import subprocess as sp
import tempfile
import pathlib
import shutil

from reportengine import api

from n3fit.scripts.n3fit_exec import N3FitConfig

from validphys.app import providers
from validphys.config import Environment
from validphys.tableloader import sane_load
from validphys.tests.test_regressions import make_table_comp
from validphys.scripts.vp_rebuild_data import REBUILD_CONFIG

FIT_NAME = "dummy_closure_runcard"

REGRESSION_FOLDER = pathlib.Path(__file__).with_name("regressions")

def parse_test_output(filename):
    """Parse a dump of a matrix like experiments_covmat."""
    df = sane_load(filename, header=0, index_col=[0,1,2])
    return df

@make_table_comp(parse_test_output)
def test_filter_rebuild_closure_data():
    runcard_name = FIT_NAME + ".yml"
    runcard = REGRESSION_FOLDER / runcard_name

    # create a /tmp folder
    tmp_name = tempfile.mkdtemp(prefix="nnpdf-")
    tmp_path = pathlib.Path(tmp_name)
    # cp runcard to tmp folder
    shutil.copy(runcard, tmp_path)
    # filter the runcard
    sp.run(f"vp-setupfit {runcard_name}".split(), cwd=tmp_path, check=True)

    sp.run(f"vp-rebuild-data {FIT_NAME}".split(), cwd=tmp_path, check=True)

    API = api.API(providers, N3FitConfig, Environment, output=str(tmp_path/FIT_NAME))
    df = API.groups_data_values(**REBUILD_CONFIG, pdf="NNPDF31_nnlo_as_0118")
    print(df.to_frame())
    return df.to_frame()
