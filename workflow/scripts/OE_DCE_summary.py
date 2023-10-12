'''
Collate all intermediate processing results and produce final
set of summary maps, figures and statistics
'''
import os
import glob
import numpy as np
from scipy.interpolate import RegularGridInterpolator

from QbiPy.tools.runner import QbiRunner, bool_option
from QbiPy.image_io.analyze_format import write_nifti_img, read_analyze
from PreclinicalMRI.dynamic import timeseries

#---------------------------------------------------------
copy_map_locations = [
    #IR T1-mapping
    ('madym_output/T1_IR/T1', 'T1_IR'),
    #- p1_estimate (?)
    #- p2_estimate (?)
    #OE time-series
    ('OE_output_maps/delta_R1', 'OE_delta_R1'),
    ('OE_output_maps/R1_p_vals', 'OE_R1_p_vals'),
    ('OE_output_maps/S_p_vals', 'OE_S_p_vals'),
    #VFA T1-mapping
    ('madym_output/T1_VFA/T1', 'T1_VFA'),
    #DCE time-series
    ('DCE_output_maps/delta_C', 'DCE_delta_C'),
    ('DCE_output_maps/C_p_vals', 'DCE_C_p_vals'),
    ('DCE_output_maps/S_p_vals', 'DCE_S_p_vals'),
    ('madym_output/ETM_pop/IAUC60', 'DCE_IAUC60'),
    ('madym_output/ETM_pop/Ktrans', 'DCE_Ktrans'),
    ('madym_output/ETM_pop/v_e', 'DCE_v_e'),
    ('madym_output/ETM_pop/v_p', 'DCE_v_p'),

]

p_val_map_locations = [
    ('OE_output_maps/R1_p_vals', 'OE_R1_p_vals'),
    ('OE_output_maps/S_p_vals', 'OE_S_p_vals'),
    ('DCE_output_maps/C_p_vals', 'DCE_C_p_vals'),
    ('DCE_output_maps/S_p_vals', 'DCE_S_p_vals')
]

converted_map_locations = [
    ('madym_output/T1_IR/T1', 'R1_IR', 'reciprocal'),
    ('madym_output/T1_VFA/T1', 'R1_VFA', 'reciprocal'),
    ('madym_output/ETM_pop/IAUC60', 'DCE_IAUC60_mask', 'zero-mask')
]


#---------------------------------------------------------
def add_options(runner):
    parser = runner.parser

    #General input arguments
    parser.add('--summary_dir', type=str, nargs='?', default='summary_outputs',
        help='')
    parser.add('--final_maps_dir', type=str, nargs='?', default='masked_maps',
        help='')
    parser.add('--roi_masks_dir', type=str, nargs='?', default='roi_masks',
        help='')
    parser.add('--suffixes', type=str, nargs=3, default=['sig_5pct', 'sig_5pct_bf', 'sig_forman'],
        help='')

#---------------------------------------------------------
def run_OE_DCE_summary(
    summary_dir:str,
    final_maps_dir:str,
    roi_masks_dir:list,
    suffixes:list,
    data_dir:str
):
    #Get ROI masks in roi_masks_dir
    roi_paths = glob.glob(os.path.join(data_dir, roi_masks_dir, '*.nii')) + \
        glob.glob(os.path.join(data_dir, roi_masks_dir, '*.nii.gz'))

    for roi_path in roi_paths:
        #Load in the roi
        roi = load_roi(data_dir, roi_path, (64,128,30))
        roi_name = os.path.splitext(os.path.basename(roi_path))[0]   
        
        #Create a folder for the final masked output masks
        masked_map_dir = os.path.join(
            data_dir, summary_dir, final_maps_dir, roi_name)
        os.makedirs(masked_map_dir, exist_ok=True)
        print(f'Creating final maps for {masked_map_dir}')

        #Create a stats file, writing the column headers
        stats_filepath = os.path.join(
            data_dir, summary_dir, f'{roi_name}_map_stats.csv')
        make_map_stats_headers(stats_filepath)

        #Process maps that just need masking an copying
        for map_location in copy_map_locations:
            make_roi_masked_maps(
                data_dir, map_location, roi, masked_map_dir, stats_filepath)
            
        #Create binary significance maps from p-value maps
        for p_val_map_location in p_val_map_locations:  
            make_significance_maps(
                data_dir, p_val_map_location, masked_map_dir, roi, suffixes)
            
        #Create converted maps
        for map_location in converted_map_locations:
            make_converted_maps(
                data_dir, map_location, roi, masked_map_dir, stats_filepath)

#---------------------------------------------------------
def make_significance_maps(
        data_dir, p_val_map_location, masked_map_dir, roi, suffixes):
    
    #Read p-value map
    print(f'Making significance maps for {p_val_map_location[0]}')
    p_val_map = load_map(data_dir, p_val_map_location[0])
    
    #Create binary significance maps
    n_vox = np.sum(roi)
    sig_maps = timeseries.enhancing_maps(p_val_map, n_vox)

    #Write them to the output folder
    p_val_map_name = os.path.basename(p_val_map_location[0])
    for map,suffix in zip(sig_maps, suffixes):
        sig_map_path = os.path.join(
            masked_map_dir, f'{p_val_map_name}_{suffix}.nii.gz')
        write_nifti_img(
            img_data = map, 
            filename = sig_map_path, 
            sform_matrix=np.eye(4), 
            scale = 1.0, 
            dtype = None)
        
#---------------------------------------------------------
def make_roi_masked_maps(
        data_dir, map_location, roi, masked_map_dir, stats_filepath):
    #Read map
    print(f'Making masked map for {map_location[0]}')
    map = load_map(data_dir, map_location[0])

    #Mask with ROI
    masked_map = map.copy()
    masked_map[~roi] = 0

    #Save masked map to the output folder
    masked_map_path = os.path.join(masked_map_dir, map_location[1]+'.nii.gz')
    write_nifti_img(
        img_data = masked_map, 
        filename = masked_map_path, 
        sform_matrix=np.eye(4), 
        scale = 1.0, 
        dtype = None)
    
    #Compute summary stats
    stats = compute_roi_summary_stats(masked_map, roi)
    write_stats(stats_filepath, map_location[1], stats)

#---------------------------------------------------------
def make_converted_maps(
        data_dir, map_location, roi, masked_map_dir, stats_filepath):
    #Read map
    map = load_map(data_dir, map_location[0])

    #Apply conversion operation
    conversion_operation = map_location[2]
    if conversion_operation == 'reciprocal':
        masked_map = 1 / map

    elif conversion_operation == 'zero-mask':
        masked_map = map > 0
    else:
        raise ValueError(f'Conversion type {conversion_operation} not recognised.')
    print(f'Applying {conversion_operation} to {map_location[0]} -> {map_location[1]}')

    #Mask with ROI
    masked_map[~roi] = 0

    #Save masked map to the output folder
    masked_map_path = os.path.join(masked_map_dir, map_location[1]+'.nii.gz')
    write_nifti_img(
        img_data = masked_map, 
        filename = masked_map_path, 
        sform_matrix=np.eye(4), 
        scale = 1.0, 
        dtype = None)
    
    #Compute summary stats
    stats = compute_roi_summary_stats(masked_map, roi)
    write_stats(stats_filepath, map_location[1], stats)

#---------------------------------------------------------
def load_map(data_dir, map_name):
    map = read_analyze(os.path.join(data_dir, map_name + '.nii.gz'), 
                       flip_y=False, swap_axes=True)
    return map[0]

#---------------------------------------------------------
def load_roi(data_dir, roi_name, map_size):
    roi = read_analyze(os.path.join(data_dir, roi_name), flip_y=False, swap_axes=False)[0]
    ry = np.arange(roi.shape[0])
    rx = np.arange(roi.shape[1])
    rz = np.arange(roi.shape[2])
    my = np.arange(map_size[0])
    mx = np.arange(map_size[1])
    mz = np.arange(map_size[2]) 
    myi,mxi,mzi = np.meshgrid(my, mx, mz, indexing='ij')

    interp3d = RegularGridInterpolator((ry, rx, rz), roi)
    roi_i = interp3d((myi,mxi,mzi))
    print(f'Reshaped ROI from {roi.shape} to {roi_i.shape}')
    return roi_i > 0

#---------------------------------------------------------
def compute_roi_summary_stats(map, roi):
    roi_vals = map[roi]
    percentiles = np.nanpercentile(roi_vals, [5, 25, 75, 95])
    stats = {
        'mean': np.nanmean(roi_vals),
        'std': np.nanstd(roi_vals),
        'median': np.nanmedian(roi_vals),
        'iqr': percentiles[2] - percentiles[1],
        '5pct': percentiles[0],
        '25pct': percentiles[1],
        '75pct': percentiles[2],
        '95pct': percentiles[3]
    }
    return stats

#---------------------------------------------------------
def make_map_stats_headers(stats_filepath):
    #Hard-code these headers - TODO could be smarter and work-out from dict headers?
    stats_headers = [
        'Map name',
        'Mean',
        'Std dev.',
        'Median',
        'IQR',
        '5th %-ile',
        '25th %-ile',
        '75th %-ile',
        '95th %-ile'
    ]
    stats_headers_str = ', '.join(stats_headers)

    #Write the headers
    os.makedirs(os.path.dirname(stats_filepath), exist_ok=True)
    with open(stats_filepath, 'wt') as f:
        print(stats_headers_str, file = f)

#---------------------------------------------------------
def write_stats(stats_filepath, map_name, stats):
    with open(stats_filepath, 'at') as f:  
          
        print(
            f'{map_name}, '
            f'{stats["mean"]}, '
            f'{stats["std"]}, '
            f'{stats["median"]}, '
            f'{stats["iqr"]}, '
            f'{stats["5pct"]}, '
            f'{stats["25pct"]}, '
            f'{stats["75pct"]}, '
            f'{stats["95pct"]}',
            file = f
        )

#---------------------------------------------------------
def main(args = None):
    runner = QbiRunner()
    add_options(runner)
    runner.run(run_OE_DCE_summary, args)

#----------------------------------------------------------
if __name__ == '__main__':
    main()
