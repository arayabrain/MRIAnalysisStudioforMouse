from datetime import datetime
import os
from optinist.api.dir_path import DIRPATH

from optinist.api.dataclass.dataclass import *

""" vbm_template.py
A workflow algorithm node template to be used in the voxel-based morphometry (VBM) analysis.
"""


def vbm_template(
    image: ImageData,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):

    print(image.params)

    print('vbm_template processing...')
    print('OPTINIST_DIR', DIRPATH.OPTINIST_DIR)

    # Set the paths of the workflow input files.
    wf_input_file_path_list = [
        'proj_root/mouse1/sub-mouse1_ses-20230501123456_rec-1_run-1_T2W.nii',
        'proj_root/mouse2/sub-mouse2_ses-20230502123456_rec-1_run-1_T2W.nii', ]

    # Create an AnalysisInfo object.
    project_path = r'../../test_data/cjs/test_project'
    analysis_info = AnalysisInfo(wf_input_file_path_list, project_path)

    # Set the data.
    output_file_path_dict = {}
    analysis_status_dict = {}
    for wf_input_path in wf_input_file_path_list:
        input_file_name = os.path.splitext(os.path.basename(wf_input_path))[0]
        folder_path = os.path.dirname(wf_input_path)
        output_file_path = os.path.join(folder_path, input_file_name + '_nodeA.nii')
        analysis_info.set_output_file_paths(wf_input_path, output_file_path)
        analysis_info.set_analysis_status(wf_input_path, AnalysisStatus.PROCESSED)
    analysis_info.analysis_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    analysis_info.analysis_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return {'analysis_info_out': analysis_info}
