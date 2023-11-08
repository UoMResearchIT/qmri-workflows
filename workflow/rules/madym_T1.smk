'''
Wrapper for madym_T1
'''
import os
from snakemake.utils import validate

configfile: workflow.source_path("../../config/madym_T1.config.yaml")
validate(config, workflow.source_path("../schemas/madym_T1.schema.yaml"))

envvars:
    "MADYM_ROOT"

rule madym_T1:
    container:
        "docker://registry.gitlab.com/manchester_qbi/manchester_qbi_public/madym_cxx/madym_release_no_gui:u22.04"
       # "preclinicalmri_depends_no_gui:latest"
    input:
        # TODO: adjust for other formats, see img_fmt_r in madym_T1.schema.yaml
        expand("{T1_dir}/{vols}{ext}",
               T1_dir = config["T1_dir"],
               vols = config["T1_vols"],
               ext = [".nii.gz", ".json"])
    output:
        # TODO: adjust for other formats, see img_fmt_w in madym_T1.schema.yaml
        expand("{output_dir}/{key}{ext}",
               output_dir = config["output_dir"],
               key = ["T1", "M0","efficiency"],
               ext = [".xtr", ".nii.gz"]),
        os.path.join(config["output_dir"], "error_tracker.nii.gz")
        # touch(os.path.join(config["output_dir"], "madym_T1.done"))
    log:
        log = config["log_file"],
        cfg = config["config_out"],
        audit = os.path.join(config["audit_dir"], config["audit_name"])
    script:
       "../scripts/madym_T1.py"