#!/usr/bin/env python
"""
    vp-pdffromfit - command line tool to obtain an LHAPDF from a NNPDF fit

    To obtain the PDF from an fit, simply run
    vp-pdffromfit <path-to-fit> <PDF name>. Optional flags allow for the
    resulting pdf to be placed in the LHAPDF directory, as well as modifying
    various fields of the info file. In addition, it is possible to compress
    the resulting PDF also using tar archiving.
"""

import argparse
import logging
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile

from lhapdf import paths

from reportengine import colors
from reportengine.compat import yaml

from validphys.renametools import change_name


# Taking command line arguments
def process_args():
    parser = argparse.ArgumentParser(
        description="Script to obtain an LHAPDF grid from a fit"
    )
    parser.add_argument("Fit", help="Path to fit")
    parser.add_argument("PDF", help="Name of the desired PDF set output")
    parser.add_argument(
        "--author",
        action="append",
        help='''The author to be added to the PDF .info file.
                Apply this argument multiple times for multiple authors,
                quotation marks can be used for an author name containing several words,
                e.g "The NNPDF collaboration"''',
    )
    parser.add_argument(
        "--description",
        help="""The set description to be added to the PDF .info file.
                Quotations should be used for this field.""",
    )
    parser.add_argument(
        "--data-version",
        type=int,
        help="The data version to be added to the PDF .info file.",
    )
    parser.add_argument(
        "--index", help="The set index to be added to the PDF .info file."
    )
    parser.add_argument(
        "--reference",
        help="The reference to be added to the PDF .info file, usually an arXiv reference.",
    )
    parser.add_argument(
        "-l",
        "--lhapdf_path",
        action="store_true",
        help="Place the output LHAPDF in the LHAPDF directory.",
    )
    parser.add_argument(
        "-c", "--compress", action="store_true", help="Compress the resulting fit."
    )
    args = parser.parse_args()
    return args


def fixup_ref(pdf_path: pathlib.Path, field_dict):
    """Function to handle alterations of the info file.
    The argparser namespace is read in as a dictionary which
    is then used to write to the resulting output file.

    If the user did not provide a field then we revert to the
    pre existing field.
    """
    pdf_name = pdf_path.name
    # Some older fits have the PDF in nnfit
    if (pdf_path / f"nnfit" / pdf_name).is_dir():
        infopath = pdf_path / f"nnfit/{pdf_name}/{pdf_name}.info"
    else:
        infopath = pdf_path / f"postfit/{pdf_name}/{pdf_name}.info"

    with open(infopath) as f:
        y = yaml.YAML()
        res = y.load(infopath)
        # If a field entry is not provided, then we revert to the existing
        # field in pre-existing info file.
        if field_dict["author"]:  # Note: bool(None) is False
            res["Authors"] = field_dict["author"]

        if field_dict["description"]:
            res["SetDesc"] = field_dict["description"]

        if field_dict["data_version"]:
            res["DataVersion"] = field_dict["data_version"]

        if field_dict["index"]:
            res["SetIndex"] = field_dict["index"]

        if field_dict["reference"]:
            res["Reference"] = field_dict["reference"]

    with open(infopath, "w") as f:
        y.default_flow_style = True
        y.dump(res, f)


def pdf_path(path: pathlib.Path) -> pathlib.Path:
    pdf_name = path.name
    # Ensure backwards compatability with older fits
    if (path / f"nnfit/{pdf_name}").is_dir():
        pdf_path = path / f"nnfit/{pdf_name}"
    else:
        pdf_path = path / f"postfit/{pdf_name}"
    return pdf_path


def compress(lhapdf_path: pathlib.Path):
    """ Function to compress the resulting PDF. Dereferences are handled
    in order to account for possible symbolic linking of grids.
    """
    output = lhapdf_path.name + ".tar.gz"
    with tarfile.open(output, "w:gz", dereference=True) as tar:
        tar.add(str(lhapdf_path), arcname=os.path.basename(str(lhapdf_path)))


def main():
    args = process_args()
    fit_path = pathlib.Path(args.Fit).resolve()
    pdf_name = args.PDF

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(colors.ColorHandler())

    if not fit_path.is_dir():
        log.error(
            f"Could not find fit. Path '{fit_path.absolute()}' is not a directory."
        )
        sys.exit(1)
    if not (fit_path / "filter.yml").exists():
        log.error(
            f"Path {fit_path.absolute()} does not appear to be a fit. "
            "File 'filter.yml' not found in the directory"
        )
        sys.exit(1)

    with tempfile.TemporaryDirectory(dir=fit_path.parent) as tmp:
        tmp = pathlib.Path(tmp)
        copied_fit = tmp / fit_path.name
        shutil.copytree(fit_path, copied_fit)

        fixup_ref(copied_fit, vars(args))

        new_path = change_name(copied_fit, pdf_name)
        lhapdf_path = pdf_path(new_path)

        if args.lhapdf_path:
            dest_path = pathlib.Path(paths()[-1]) / pdf_name
        else:
            dest_path = new_path.parent.with_name(pdf_name)

        if dest_path.exists():
            log.error(f"Destination path {dest_path.absolute()} already exists.")
            sys.exit(1)

        lhapdf_path = lhapdf_path.rename(dest_path)
        log.info(f"PDF generated and placed in {lhapdf_path.parent}")

        if args.compress:
            log.info("Compressing output")
            compress(lhapdf_path)
