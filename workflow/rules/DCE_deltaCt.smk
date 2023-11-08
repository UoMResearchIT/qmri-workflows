'''
Wrapper for PreclinicalMRI.dynamic.compute_dataset_delta_Ct
'''
import os
from snakemake.utils import validate

configfile: workflow.source_path("../../config/DCE_deltaCt.config.yaml")
validate(config, workflow.source_path("../schemas/DCE_deltaCt.schema.yaml"))

for key in ['dce_path', 'T1_path', 'maps_dir']:
    config[key] = data_path(config[key])

for ext in ['dce_im_ext','dce_meta_ext']:
    check_extension(config[ext])

rule DCE_deltaCt:
    # conda:
    #  "../envs/conda_env.yml"
    input:
        images = f"{config['dce_path']}{config['dce_im_ext']}",
        metadata = f"{config['dce_path']}{config['dce_meta_ext']}",
        T1_path = config['T1_path'],
        # roi_path = f"{config['roi_path']}",
    output:
        expand("{maps_dir}/{key}{ext}",
            maps_dir = config["maps_dir"],
            key = ['C_t', 'delta_C', 'C_baseline', 'C_enhancing', 'C_p_vals', 'S_p_vals'],
            ext = ".nii.gz")
    log:
        DCE_deltaCt = "logs/qMRI_processes/DCE_deltaCt.log"
    script:
        "../scripts/DCE_deltaCt.py"
