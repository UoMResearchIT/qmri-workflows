'''
_summary_
'''
import numpy as np
import os

from QbiPy.tools.runner import QbiRunner, bool_option
from QbiPy.image_io.analyze_format import write_nifti_img
from PreclinicalMRI.dynamic import oe

#---------------------------------------------------------
def add_options(runner):
    parser = runner.parser

    #General input arguments
    parser.add('--roi_path', type=str, nargs='?', default=None,
        help='Relative path to roi mask file')

    #OE input options
    parser.add('--oe_path', type=str, nargs='?', default='oxygen/oe',
        help='Relative path to OE 4D-image volumes')
    parser.add('--oe_im_ext', type=str, nargs='?', default='.nii.gz',
        help='File extension of the OE volumes')
    parser.add('--oe_meta_ext', type=str, nargs='?', default='.json',
        help='File extension of the OE volumes meta-info')
    parser.add('--oe_limits', type=int, nargs=4, required=True,
        help='Limits for the OE volumes, 4 element integer list')
    parser.add('--T1_path', type=str, nargs='?', default='madym_output/T1_IR/T1.nii.gz',
        help='Relative path to T1 image')
    parser.add('--efficiency_path', type=str, nargs='?', default='madym_output/T1_IR/efficiency.nii.gz',
        help='Relative path to T1 efficiency image')
    
    #Summary stats options
    parser.add('--average_fun', type=str, nargs='?', default='median',
        help='Method used for temporal average {median, mean}.')
    parser.add('--alternative', type=str, nargs='?', default='less',
        help='Apply 1-sided or 2-sided t-test: less = baseline lower than enhancing. Use "equal" for 2-sided.')
    parser.add('--equal_var', type=bool_option, nargs='?', default=True, 
        const = True, help='Assume equal variance in pre/post enhancing periods')
    parser.add('--sig_level', type=float, nargs='?', default=0.05,
        help='Significance level for p-value map thresholds')
    
    #Output dir
    parser.add('--maps_dir', type=str, nargs='?', default='OE_output_maps',
        help='Location of saved output maps, relative to data_dir')
    
#---------------------------------------------------------
def run_OE_deltaR1(
    data_dir:str,
    oe_limits:np.array, 
    oe_path:str,
    oe_im_ext:str,
    oe_meta_ext:str,
    T1_path:str,
    efficiency_path:str,
    average_fun:str,
    alternative:str,
    equal_var:bool,
    maps_dir:str
):
    print('Running OE_deltaR1')
    oe_data = oe.compute_dataset_delta_R1(
        data_dir = data_dir, 
        oe_limits = oe_limits, 
        oe_path = oe_path,
        oe_im_ext = oe_im_ext,
        oe_meta_ext = oe_meta_ext,
        T1_path = T1_path,
        efficiency_path = efficiency_path,
        average_fun = average_fun,
        alternative = alternative,
        equal_var = equal_var)
    
    maps_dir = os.path.join(data_dir, maps_dir)
    os.makedirs(maps_dir, exist_ok = True)

    for key,value in oe_data.items():
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
    runner.run(run_OE_deltaR1, args)

#----------------------------------------------------------
if __name__ == '__main__':
    main()
