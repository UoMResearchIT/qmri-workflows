import os
from snakemake.utils import validate

# report: "../report/workflow.rst"
# container: "preclinicalmri_depends_no_gui:latest"

# configfile: workflow.source_path("../config/common.config.yaml")
validate(config, workflow.source_path("../schemas/common.schema.yaml"))

def data_path(path, check_existing = False):
    """
    Parse config[path_key] as a relative path
    """
    if path is None or path == "":
        path = []
    else:
        path = os.path.expanduser(os.path.expandvars(path))
        path = os.path.relpath(path)

    if check_existing:
        assert os.path.exists(path), f"{path} does not exist"

    return path

def abs_path(path, check_existing = False):
    """
    Parse config[path_key] as an absolute path
    """
    path = data_path(path, check_existing)
    return os.path.abspath(path)

def check_extension(ext):
    assert ext.startswith('.'), f"File extension {ext} should start with a dot"


config["data_dir"] = abs_path(config["data_dir"], check_existing = True)
# config["data_dir"] = data_path(config["data_dir"], check_existing = True)
workdir: config["data_dir"]


# import os
# import sys
# import socket
# import getpass

# from contextlib import redirect_stdout, redirect_stderr
# from datetime import datetime

# def run_with_logging(log_file, config, script):

#     date_str = datetime.today().strftime('%Y%m%d %H:%M:%S')

#     #Open program log file
#     with open(log_file, 'wt') as log:

#         print(f'Log opened at {date_str}', file=log)
#         # print(f'User: {getpass.getuser()};   Host: {socket.gethostname()}', file=log)

#         for option, value in config.__dict__.items():
#             print(f'{option} = {value}', file = log)
        
#         with redirect_stderr(log), redirect_stdout(log):
#             import script

#     return success
