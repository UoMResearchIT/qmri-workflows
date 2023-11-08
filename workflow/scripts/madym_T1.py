import os
import re

from QbiMadym import madym_T1
from QbiMadym.utils import local_madym_root

import subprocess
command = 'madym_T1.exe'
try:
    command = os.path.join(local_madym_root(),'madym_T1')
    subprocess.run([command, "--version"], stdout = subprocess.PIPE, stderr = subprocess.PIPE, check=True)
except subprocess.CalledProcessError:
    raise NameError(f"{command} is not available.")

madym_T1.run(
    # 
    working_directory = os.getcwd(),
    config_file = None,
    # cmd_exe = command,
    # 
    output_dir = snakemake.config["output_dir"],
    img_fmt_w = "NIFTI_GZ",
    
    # Input
    # T1_dir = snakemake.config["T1_dir"],
    T1_vols = [os.path.join(snakemake.config["T1_dir"], vol) for vol in snakemake.config["T1_vols"]],
    img_fmt_r = "NIFTI_GZ",
    roi_name = snakemake.config["roi_path"],
    error_name = snakemake.config["error_name"],

    # Params
    method = snakemake.config["method"],
    B1_name = snakemake.config["B1_name"],
    B1_scaling = snakemake.config["B1_scaling"],
    noise_thresh = snakemake.config["T1_noise"],
    nifti_scaling = snakemake.config["nifti_scaling"],
    nifti_4D = snakemake.config["nifti_4D"],
    use_BIDS = snakemake.config["use_BIDS"],
    voxel_size_warn_only = snakemake.config["voxel_size_warn_only"],
    #
    no_log = False,
    quiet = False,
    overwrite = True,
    return_maps = False,
    dummy_run = False,

    no_audit = snakemake.config["no_audit"],
    audit_dir = snakemake.config["audit_dir"],

    program_log_name = "smk.log", # see below (*)
    config_out = "smk.cfg",
    audit_name = "smk.audit"

    # madym_T1_lite options (not exposed)
    #   ScannerParams = None,
    #   signals = None,
    #   TR = None,
    #   B1_values = None,
    #   output_name = 'madym_analysis.dat',
)

# (*) Logs are time-stamped and auto-renamed by madym:
#
#  {output_dir}/madym_T1_{date}_{time}_smk.log
#  {output_dir}/madym_T1_{date}_{time}_smk.cfg
#  {output_dir}/madym_T1_{date}_{time}_override_smk.cfg
#  {audit_dir}/madym_T1_{date}_{time}_smk.audit
#
# Rename to consistent snakemake.log entries
for item in snakemake.log.keys():

    if item == "log" or item == "cfg":
        dir = snakemake.config["output_dir"]
    elif item == "audit":
        dir = snakemake.config["audit_dir"]
    else:
        raise NameError("Unexpected log key: " + item)

    for filename in os.listdir(dir):
        match = re.match(r'madym_T1_(\d+)_(\d+)(_\w)?_smk\.' + item, filename)
        if match:
            if match.group(3) is None:
                logname = snakemake.log[item]
            else:
                # Modify log.ext to e.g. log_override.ext
                logname = re.sub(r'(\.\w+)$', match.group(3) + r'\1', snakemake.log[item])
            os.rename(os.path.join(dir, filename), logname)
