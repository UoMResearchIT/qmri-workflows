'''
_summary_
'''
import os
import numpy as np

from QbiPy.tools.runner import QbiRunner, bool_option
from QbiPy.image_io.analyze_format import write_nifti_img
from PreclinicalMRI.dynamic import dce

#---------------------------------------------------------
def add_options(runner):
    parser = runner.parser

    #General input arguments
    parser.add('--roi_path', type=str, nargs='?', default=None,
        help='Relative path to roi mask file')

    #DCE input options
    parser.add('--dce_path', type=str, nargs='?', default='dynamic',
        help='Relative path to DCE 4D-image volumes')
    parser.add('--dce_im_ext', type=str, nargs='?', default='.nii.gz',
        help='File extension of the DCE volumes')
    parser.add('--dce_meta_ext', type=str, nargs='?', default='.json',
        help='File extension of the DCE volumes meta-info')
    parser.add('--dce_limits', type=int, nargs=4, required=True,
        help='Limits for the DCE volumes, 4 element integer list')
    parser.add('--T1_path', type=str, nargs='?', default='madym_output/T1_VFA/T1.nii.gz',
        help='Relative path to T1 image')
    parser.add('--relax_coeff', type=float, nargs='?', default=3.4,
        help='Relaxivity constant for contrast agent - units... ')
    
    #Summary stats options
    parser.add('--average_fun', type=str, nargs='?', default='median',
        help='Method used for temporal average {median, mean}.')
    parser.add('--alternative', type=str, nargs='?', default='less',
        help='Apply 1-sided or 2-sided t-test: less = baseline lower than enhancing. Use "two-sided" for 2-sided.')
    parser.add('--equal_var', type=bool_option, nargs='?', default=True, 
        const = True, help='Assume equal variance in pre/post enhancing periods')
    
    # TODO: Unused?
    # parser.add('--sig_level', type=float, nargs='?', default=0.05,
    #     help='Significance level for p-value map thresholds')
    
    #Output dir
    parser.add('--maps_dir', type=str, nargs='?', default='DCE_output_maps',
        help='Location of saved output maps, relative to data_dir')

#---------------------------------------------------------
def run_DCE_deltaCt(
    data_dir:str,
    dce_limits:np.array, 
    dce_path:str,
    dce_im_ext:str,
    dce_meta_ext:str,
    T1_path:str,
    roi_path:str,
    relax_coeff:float,
    average_fun:str,
    alternative:str,
    equal_var:bool,
    maps_dir:str
):
    print('Running DCE_deltaCt')
    dce_data = dce.compute_dataset_delta_Ct(
        data_dir, 
        dce_limits, 
        dce_path = dce_path,
        dce_im_ext = dce_im_ext,
        dce_meta_ext = dce_meta_ext,
        T1_path = T1_path,
        roi_path = roi_path,
        relax_coeff = relax_coeff,
        average_fun = average_fun,
        alternative = alternative,
        equal_var = equal_var,
        debug = 0)
    
    maps_dir = os.path.join(data_dir, maps_dir)
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

#---------------------------------------------------------
def main(args = None):
    runner = QbiRunner()
    add_options(runner)
    runner.run(run_DCE_deltaCt, args)

#----------------------------------------------------------
if __name__ == '__main__':
    main()
