import pandas as pd

from validphys.commondataparser import load_commondata
from validphys.loader import Loader


def test_basic_commondata_loading():
    l = Loader()
    cd = l.check_commondata(setname="H1HERAF2B")
    res = load_commondata(cd)
    # Test commondata loading
    assert res.commondata.ndata == 12
    assert isinstance(res.commondata.commondata_table, pd.DataFrame)
    # Test systype loading
    assert res.systypes.nsys == 25
    assert isinstance(res.systypes.systype_table, pd.DataFrame)
