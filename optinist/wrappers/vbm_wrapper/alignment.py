import numpy as np

from optinist.api.dataclass.dataclass import AnalysisInfo, AnalysisStatus
from optinist.wrappers.vbm_wrapper.nifti_image import NiftiImage


""" alignment.py
Update the affine transformation matrix in NIfTI files for given alignment.
"""


def align_images(
    # image_data: ImageData
    params_in: dict = None
) -> dict(analysis_info_out=AnalysisInfo):
    # Get the paths of the workflow input files.
    # wf_input_path_list = [get_wf_input_file_path(params['image_id']) for params in image_data.params]   DEBUG
    wf_input_path_list = [get_wf_input_file_path(params['image_id']) for params in params_in]

    # Initialize an AnalysisInfo object for output.
    project_path = r'../../test_data/cjs/test_project'
    analysis_info_out = AnalysisInfo(wf_input_path_list, project_path)

    # Update each NIfTI file.
    # for wf_input_path, params in zip(wf_input_path_list, image_data.params):   DEBUG
    for wf_input_path, params in zip(wf_input_path_list, params_in):
        try:
            # Set the alignment parameters.
            alignment_params = np.array(
                [params['a'],
                 params['b'],
                 params['c'],
                 params['d'],
                 params['e'],
                 params['f'],
                 params['g'],
                 params['h'],
                 params['i'],
                 params['j'],
                 params['k'],
                 params['l']])

            # Create a NiftiImage object.
            nifti = NiftiImage(wf_input_path)

            # Calculate a new affine transformation matrix, and overwrite the NIfTI file with the matrix.
            nifti.update_affine_matrix(alignment_params)

            # Set the same file path as output.
            analysis_info_out.set_output_file_paths(wf_input_path, [wf_input_path])
            analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.PROCESSED)
        except Exception as error:
            analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.ERROR)
            analysis_info_out.set_message(wf_input_path, error.args[0])

    return {'analysis_info_out': analysis_info_out}


# DEBUG
def get_wf_input_file_path(image_id):
    import os
    folder_path = r'../../test_data/cjs/test_project'
    file_name = 'T2_H477_SU007.nii'
    file_path = os.path.join(folder_path, file_name)

    return file_path
