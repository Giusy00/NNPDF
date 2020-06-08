import pandas as pd

from validphys.api import API
from validphys.commondataparser import load_commondata
from validphys.loader import Loader


def test_basic_commondata_loading():
    l = Loader()
    cd = l.check_commondata(setname="H1HERAF2B")
    res = load_commondata(cd)
    # Test commondata loading
    assert res.ndata == 12
    assert isinstance(res.commondata_table, pd.DataFrame)
    # Test systype loading
    assert res.nsys == 25
    assert isinstance(res.systype_table, pd.DataFrame)
    # Test a dataset with no systematics
    emptysyscd = l.check_commondata(setname="CMSWCHARMRAT")
    emptysysres = load_commondata(emptysyscd)
    assert emptysysres.nsys == 0
    assert emptysysres.systype_table.empty is True
