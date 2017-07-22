#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 10:38:21 2016

@author: zah
"""
import subprocess
import logging
import shutil
import uuid
import base64
import sys
import contextlib
import pathlib

from reportengine.colors import t

log = logging.getLogger(__name__)

#TODO: This should go to nnprofile
upload_host = 'nnpdf@pcteserver.mi.infn.it'

target_dir = "WEB/validphys-reports/"

root_url = 'http://pcteserver.mi.infn.it/~nnpdf/validphys-reports/'

class BadSSH(Exception): pass

def check_auth():
    ssh_command_line = ('ssh', '-o', 'PreferredAuthentications=publickey',
                        '-q', upload_host, 'exit')

    str_line = ' '.join(repr(ele) for ele in ssh_command_line)

    log.info("Checking SSH connection to %s.", upload_host)

    try:
        subprocess.run(ssh_command_line, check=True)
    except subprocess.CalledProcessError as e:
        raise BadSSH(("Could not validate the SSH key. "
        "The command\n%s\nreturned a non zero exit status. "
        "Please make sure thet your public SSH key is on the server.")
        % str_line) from e
    except OSError as e:
        raise BadSSH("Could not run the command\n%s\n: %s" % (str_line, e)) from e

    log.info("Connection seems OK.")

def check_rsync():
    if not shutil.which('rsync'):
        raise BadSSH("Could not find the rsync command. "
        "Please make sure it is installed.")

def check_upload():
    check_rsync()
    check_auth()


def upload_output(output_path, specific_file=None):
    """Rsync ``output_path`` to the server and print the resulting URL. If
    specific_file is given"""
    #Set the date to now
    pathlib.Path(output_path).touch()
    randname = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()
    newdir = target_dir + randname

    rsync_command = ('rsync', '-aLz', '--chmod=D775', f"{output_path}/", f'{upload_host}:{newdir}')

    log.info(f"Uploading output ({output_path}) to {upload_host}")
    try:
        subprocess.run(rsync_command, check=True)
    except subprocess.CalledProcessError as e:
        msg = f"Failed to upload output: {e}"
        raise BadSSH(msg) from e
    else:
        #Allow None and so on
        if not specific_file:
            specific_file = ''
        url = f'{root_url}{randname}/{specific_file}'
        log.info(f"Upload completed. The result is available at:\n{t.bold_blue(url)}")

@contextlib.contextmanager
def upload_context(output, specific_file=None):
    """Before entering the context, check that uploading is feasible.
    On exiting the context, upload output.
    """
    check_upload()
    yield
    upload_output(output, specific_file)

@contextlib.contextmanager
def upload_or_exit_context(output, specific_file=None):
    """Like upload context, but log and sys.exit on error"""
    try:
        with upload_context(output=output, specific_file=specific_file):
            yield
    except BadSSH as e:
        log.error(e)
        sys.exit()