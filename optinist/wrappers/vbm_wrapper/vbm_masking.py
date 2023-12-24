import json
import os
import sys
import traceback

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_masking(
    analysis_info_in: AnalysisInfo,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Mask brain MRI images by Nipype for VBM analysis.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        params : Dict
            Parameters defined in the vbm_template.yaml in addition to project ID, analysis ID, and node ID.
            project_id : Project ID
            analysis_id: Analysis ID
            node_id    : Node ID

    Returns
        ----------
        analysis_info_out : AnalysisInfo
            Info about VBM analysis performed in this node.
    """

    # Make sure of the connection type.
    assert analysis_info_in.node_analysis_type == NodeAnalysisType.SEGMENT1, 'This node connection is not allowed.'

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directories.
    project_path = utils.get_project_path(params['project_id'])
    alignment_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'], NodeAnalysisType.ALIGNMENT)
    segment1_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'], NodeAnalysisType.SEGMENT1)

    # Create the output derivatives directory if it does not exist.
    masking_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'], NodeAnalysisType.MASKING)

    # Get the previous node analysis info in order to check if the analysis is skipped.
    previous_node_analysis_info = utils.get_previous_node_analysis_info(params)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(masking_dir_path)

    # Perform the brain image masking processing by Nipype.
    analysis_info_out = process_vbm_masking(analysis_info_in, alignment_dir_path, segment1_dir_path,
                                            masking_dir_path, params['skip_analyzed'], previous_node_analysis_info,
                                            unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, [alignment_dir_path, segment1_dir_path], masking_dir_path,
                                    params['skip_analyzed'])

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def process_vbm_masking(analysis_info_in: AnalysisInfo, alignment_dir_path: str, segment1_dir_path: str,
                        masking_dir_path: str, skip_analyzed: bool, previous_node_analysis_info: Dict,
                        unused_output_dir_path_list: List[str]) -> AnalysisInfo:
    """ Perform the brain image masking processing by Nipype.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        alignment_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_alignment node.
        segment1_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_segment1 node.
        masking_dir_path : str
            Path of the directory storing the analysis results performed by this node.
        skip_analyzed: bool
            True for checking if the analysis can be skipped for inputs that have been already analyzed before,
            otherwise reanalyze anyway.
        previous_node_analysis_info : dict
            Key: Workflow input file path
            Value : dict
                output_file_paths (list[str])): Paths of the output files generated in the node analysis.
                success (str): Analysis status message ('success' or 'error').
                message (str): Any additional message.
        unused_output_dir_path_list : list[str]
            Paths of the previously generated output directories, but not included in the analysis.

    Returns
        ----------
        analysis_info_out : AnalysisInfo
            Info about VBM analysis performed in this node.
    """

    # Create an output AnalysisInfo template.
    analysis_info_out = analysis_info_in.create_new_analysis_info(NodeAnalysisType.MASKING)

    # Process by each workflow input derivatives.
    for wf_input_path in analysis_info_in.workflow_input_file_path_list:
        # Workflow input file name without the extension.
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        try:
            # Skip analysis.
            if utils.skip_node_analysis(wf_input_path, skip_analyzed, previous_node_analysis_info):
                utils.remove_from_unused_list(join_filepath([masking_dir_path, wf_input_name]),
                                              unused_output_dir_path_list)
                analysis_info_out.set_output_file_paths(wf_input_path,
                                                        analysis_info_in.get_output_file_paths(wf_input_path))
                analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.SKIPPED)
                continue
            # Check a previous error.
            elif analysis_info_in.get_analysis_status(wf_input_path) == AnalysisStatus.ERROR or \
                    analysis_info_in.get_analysis_status(wf_input_path) == AnalysisStatus.PREVIOUS_ERROR:
                analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.PREVIOUS_ERROR)
                raise VbmException(f'[Error ({wf_input_name})] Error occurred in the previous node analysis.\n'
                                   f'{analysis_info_in.get_message(wf_input_path)}')
            else:
                # Check if the input data exist.
                result = utils.check_derivatives_existence([alignment_dir_path, segment1_dir_path], wf_input_name)
                if not result['exist']:
                    raise VbmException(f'[Error ({wf_input_name})] Input data not found in '
                                       f'{os.path.basename(result["missing_dir_path"])}.')
                # Delete the old output data if they exist.
                if utils.check_derivatives_existence(masking_dir_path, wf_input_name)['exist']:
                    utils.delete_derivatives_data(masking_dir_path, wf_input_name)

            # Mask brain MRI images.
            analysis_info_out.set_analysis_start_time(wf_input_path)
            output_dir_path = utils.create_directory([masking_dir_path, wf_input_name])
            output_file_path_list = mask_brain_images(wf_input_name, os.path.dirname(alignment_dir_path),
                                                      masking_dir_path)

            # Remove this output directory from the unmanaged list.
            utils.remove_from_unused_list(output_dir_path, unused_output_dir_path_list)

            # Set the analysis info.
            analysis_info_out.set_output_file_paths(wf_input_path, output_file_path_list)
            analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.PROCESSED)
        except:
            error_message = traceback.format_exc()
            print(f'[Error ({wf_input_name})]\n{error_message}')
            analysis_info_out.set_message(wf_input_path, error_message)
        finally:
            analysis_info_out.set_analysis_end_time(wf_input_path)

    return analysis_info_out


def mask_brain_images(wf_input_name: str, root_derivatives_dir_path: str, masking_dir_path: str) -> List[str]:
    """ Mask brain MRI images by Nipype.

    Parameters
        ----------
        wf_input_name : str
            Workflow input file name without the extension.
        root_derivatives_dir_path : str
            Path of the root derivatives directory.
        masking_dir_path : str
            Path of the directory storing the analysis results performed by this node.

    Returns
        ----------
        output_file_path_list : list[str]
            Paths of the output files generated in the analysis.
    """

    import nibabel as nb
    from nipype import Node
    from nipype.interfaces.io import SelectFiles
    import numpy as np

    # Select input files.
    templates = {
        'alignment': 'alignment/{subject_id}/{subject_id}.nii',
        'segment1_c1': 'segment1/{subject_id}/c1{subject_id}.nii',
        'segment1_c2': 'segment1/{subject_id}/c2{subject_id}.nii',
        'segment1_c3': 'segment1/{subject_id}/c3{subject_id}.nii'}
    select_files_node = Node(SelectFiles(templates), name='select_files')
    select_files_node.inputs.base_directory = root_derivatives_dir_path
    select_files_node.inputs.subject_id = wf_input_name
    selected_files = select_files_node.run()

    # Load image data from NIfTI files.
    c1_nifti = nb.load(selected_files.outputs.segment1_c1)
    c2_nifti = nb.load(selected_files.outputs.segment1_c2)
    c3_nifti = nb.load(selected_files.outputs.segment1_c3)
    c1_image_data = c1_nifti.get_fdata()
    c2_image_data = c2_nifti.get_fdata()
    c3_image_data = c3_nifti.get_fdata()

    # Create mask images.
    x, y, z = c1_image_data.shape
    mask_image_data = np.zeros((x, y, z))
    for n in range(z):
        for k in range(y):
            for m in range(x):
                if c1_image_data[m, k, n] > 0 or c2_image_data[m, k, n] > 0 or c3_image_data[m, k, n] > 0:
                    mask_image_data[m, k, n] = 1

    # Save the mask image data.
    mask_nifti = nb.Nifti1Image(mask_image_data, affine=c1_nifti.affine)
    masking_subdir_path = utils.create_directory([masking_dir_path, wf_input_name])
    mask_file_path = join_filepath([masking_subdir_path, 'mask.nii'])
    nb.save(mask_nifti, mask_file_path)

    # Apply the mask to the brain MRI images.
    aligned_nifti = nb.load(selected_files.outputs.alignment)
    aligned_image_data = aligned_nifti.get_fdata()
    masked_image_data = mask_image_data * aligned_image_data
    masked_nifti = nb.Nifti1Image(masked_image_data, affine=aligned_nifti.affine)
    file_name = os.path.basename(selected_files.outputs.alignment)
    masked_file_path = join_filepath([masking_subdir_path, file_name])
    nb.save(masked_nifti, masked_file_path)

    # Return the paths of the output files saved in the analysis.
    return utils.get_derivatives_file_paths(masking_dir_path, wf_input_name)


def create_dataset_description_file(function_name: str, input_dir_path_list: List[str], output_dir_path: str,
                                    skip_analyzed: bool):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path) for input_dir_path in input_dir_path_list]
    dataset_description = utils.get_dataset_description_template('Masking', function_name, input_dir_name_list)
    dataset_description['Parameters']['skip_analyzed'] = skip_analyzed

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
