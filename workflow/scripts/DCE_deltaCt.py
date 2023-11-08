'''
Wrapper for PreclinicalMRI.dynamic.compute_dataset_delta_Ct
'''
import os
import numpy as np
from contextlib import redirect_stdout, redirect_stderr

from QbiPy.image_io.analyze_format import write_nifti_img
from PreclinicalMRI.dynamic import dce

with open(snakemake.log["DCE_deltaCt"], "w") as log:
    with redirect_stderr(log), redirect_stdout(log):

        print('Running DCE_deltaCt')
        dce_data = dce.compute_dataset_delta_Ct(
            os.getcwd(), 
            snakemake.config["dce_limits"], 
            dce_path = snakemake.config["dce_path"],
            dce_im_ext = snakemake.config["dce_im_ext"],
            dce_meta_ext = snakemake.config["dce_meta_ext"],
            T1_path = snakemake.config["T1_path"],
            roi_path = snakemake.config["roi_path"],
            relax_coeff = snakemake.config["relax_coeff"],
            average_fun = snakemake.config["average_fun"],
            alternative = snakemake.config["alternative"],
            equal_var = snakemake.config["equal_var"],
            debug = 0)

        maps_dir = snakemake.config["maps_dir"]
        os.makedirs(maps_dir, exist_ok = True)

        for key,value in dce_data.items():
            print(f'{key} has shape {value.shape}')
            nii_filepath = os.path.join(maps_dir, key + '.nii.gz')
            write_nifti_img(
                img_data = value, 
                filename = nii_filepath, 
                sform_matrix=np.eye(4), 
                scale = 1.0, 
                dtype = None)
