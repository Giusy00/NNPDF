"""
    Module containing an LHAPDF class compatible with validphys
    using the official lhapdf python interface.
    It exposes an interface (almost) compatible with libNNPDF::LHAPDFSet
    The ``.members`` and ``.central_member`` of the ``LHAPDFSet`` are
    LHAPDF objects (the typical output from ``mkPDFs``) and can be used normally.
    For MC PDFs the ``central_member`` is the average of all replicas (members 1-100)
    while for Hessian PDFs the ``central_member`` is also ``member[0]``
    Examples
    --------
    >>> from validphys.lhapdfset import LHAPDFSet, ER_MC
    >>> pdf = LHAPDFSet("NNPDF40_nnlo_as_01180", ER_MC)
    >>> pdf.get_members()
    100
    >>> len(pdf.members)
    100
    >>> pdf.central_member.alphasQ(91.19)
    0.11800
    >>> pdf.member[0].xfxQ2(0.5, 15625)
    {-5: 6.983360500601136e-05,
    -4: 0.0021818063617227604,
    -3: 0.00172453472243952,
    -2: 0.0010906577230485718,
    -1: 0.0022049272225017286,
    1: 0.020051104853608722,
    2: 0.0954139944889494,
    3: 0.004116641378803191,
    4: 0.002180124185625795,
    5: 6.922722705177504e-05,
    21: 0.007604124516892057}
"""
import logging
from typing import NamedTuple
import numpy as np
import lhapdf

log = logging.getLogger(__name__)


class PDFErrorType(NamedTuple):
    """Namedtuple containing the information about the error type of the PDF"""

    name: str
    monte_carlo: bool
    libNNPDF: int
    t0: bool
    description: str


ER_NONE = PDFErrorType("erType_ER_NONE", False, 0, False, "No error info")
ER_MC = PDFErrorType("erType_ER_MC", True, 1, False, "Monte Carlo")
ER_MC68 = PDFErrorType("erType_ER_MC68", True, 2, False, "Monte Carlo 68pc")
ER_MCT0 = PDFErrorType("erType_ER_MCT0", False, 3, True, "Monte Carlo t0")
ER_EIG = PDFErrorType("erType_ER_EIG", False, 4, False, "Eigenvector 68pc")
ER_EIG90 = PDFErrorType("erType_ER_EIG90", False, 5, False, "Eigenvector 90pc")
ER_SYMEIG = PDFErrorType("erType_ER_SYMEIG", False, 6, False, "Symmetric eigenvectors")


class LHAPDFSet:
    """Wrapper for the lhapdf python interface.
    Once instantiated this class will load the PDF set according to whether it is to be
    treated as a T0 set (only the CV) or not.
    For Monte Carlo sets the central value (member 0) is by default not included when taking
    the resutls for all members (i.e., when using ``grid_values``).
    However, it is possible to add member 0 by changing the ``include_cv`` attribute to True.
    Temporarily: it exposes all libNNPDF error attributes that were exposed and used prior to
    the introduction of this class
    """

    def __init__(self, name, error_type):
        log.info("PDF: %s ErrorType: %s", name, error_type)
        self._name = name
        self._error_type = error_type
        if self.is_t0:
            # If at this point we already know this is a T0 set, load only the CV
            self._lhapdf_set = [lhapdf.mkPDF(name)]
        else:
            self._lhapdf_set = lhapdf.mkPDFs(name)
        self._flavors = None

    @property
    def is_monte_carlo(self):
        """Check whether the error type is MC"""
        return self._error_type == "replicas"

    @property
    def is_t0(self):
        """Check whether we are in t0 mode"""
        return self._error_type == "t0"

    @property
    def n_members(self):
        """Return the number of active members in the PDF set"""
        return len(self.members)

    @property
    def members(self):
        """Return the members of the set, this depends on the error type:
            t0: returns only member 0
            MC: skip member 0
            Hessian: return all
        """
        if self.is_t0:
            return self._lhapdf_set[0:1]
        if self.is_monte_carlo:
            return self._lhapdf_set[1:]
        return self._lhapdf_set

    @property
    def central_member(self):
        """Returns a reference to member 0 of the PDF list"""
        return self._lhapdf_set[0]

    def xfxQ(self, x, q, member_idx, flavour):
        """Return the PDF value for one single point for one single member"""
        member_pdf = self.members[member_idx]
        res = member_pdf.xfxQ(x, q)
        return res[flavour]

    @property
    def flavors(self):
        """Returns the list of accepted flavors by the LHAPDF set"""
        if self._flavors is None:
            self._flavors = self.members[0].flavors()
        return self._flavors

    def grid_values(self, flavors: np.ndarray, xgrid: np.ndarray, qgrid: np.ndarray):
        """Returns the PDF values for every member for the required
        flavours, points in x and pointx in q
        The return shape is
            (members, flavors, xgrid, qgrid)
        Return
        ------
            ndarray of shape (members, flavors, xgrid, qgrid)
        Examples
        --------
        >>> import numpy as np
        >>> from validphys.lhapdfset import LHAPDFSet, ER_MC
        >>> pdf = LHAPDFSet("NNPDF40_nnlo_as_01180", ER_MC)
        >>> xgrid = np.random.rand(10)
        >>> qgrid = np.random.rand(3)
        >>> flavs = np.arange(-4,4)
        >>> flavs[4] = 21
        >>> results = pdf.grid_values(flavs, xgrid, qgrid)
        """
        # Grid values loop
        ret = np.array(
            [
                [[member.xfxQ(flavors, x, q) for x in xgrid] for q in qgrid]
                for member in self.members
            ]
        )

        # Finally return in the documented shape
        return np.transpose(ret, (0, 3, 2, 1))
