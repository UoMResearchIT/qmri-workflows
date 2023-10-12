'''
Wrapper for PreclinicalMRI.dynamic.compute_dataset_delta_Ct
'''
import os
from snakemake.utils import validate

configfile: workflow.source_path("../../config/DCE_deltaCt.config.yaml")
validate(config, workflow.source_path("../schemas/DCE_deltaCt.schema.yaml"))

data_dir = config.get("data_dir")
assert os.path.exists(data_dir), f"The folder {data_dir} does not exist"
workdir: data_dir

def data_path(path_key):
    rel_path = config.get(path_key)
    return rel_path if rel_path is not None else []

rule DCE_deltaCt:
    conda:
      "../envs/conda_env.yml"
    input:
        images = f"{data_path('dce_path')}{config['dce_im_ext']}",
        metadata = f"{data_path('dce_path')}{config['dce_meta_ext']}",
        T1_path = data_path('T1_path'),
        roi_path = data_path('roi_path')
    output:
        expand("{maps_dir}/{key}{ext}",
            maps_dir = data_path("maps_dir"),
            key = ['C_t', 'delta_C', 'C_baseline', 'C_enhancing', 'C_p_vals', 'S_p_vals'],
            ext = ".nii.gz"),
    params:
        dce_limits = config["dce_limits"],
        relax_coeff = config["relax_coeff"],
        average_fun = config["average_fun"],
        alternative = config["alternative"],
        equal_var = config["equal_var"]
    log:
        config["output_dir"]
    script:
        "../scripts/DCE_deltaCt.py"
