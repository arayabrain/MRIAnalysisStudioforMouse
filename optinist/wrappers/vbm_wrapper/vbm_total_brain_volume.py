import json
import os
import sys
import traceback

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_total_brain_volume(
    analysis_info_in: AnalysisInfo,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Calculate total brain volumes for VBM analysis.

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
    assert (analysis_info_in.node_analysis_type == NodeAnalysisType.SEGMENT2) or \
           (analysis_info_in.node_analysis_type == NodeAnalysisType.SMOOTHING)

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directories.
    project_path = utils.get_project_path(params['project_id'])
    segment2_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'], NodeAnalysisType.SEGMENT2)

    # Create the output derivatives directory if it does not exist.
    brain_volume_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'],
                                                               NodeAnalysisType.TOTAL_BRAIN_VOLUME)

    # Get the previous node analysis info in order to check if the analysis is skipped.
    previous_node_analysis_info = utils.get_previous_node_analysis_info(params)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(brain_volume_dir_path)

    # Perform total brain volume calculation.
    analysis_info_out = process_vbm_total_brain_volume(analysis_info_in, segment2_dir_path, brain_volume_dir_path,
                                                       params['skip_analyzed'], previous_node_analysis_info,
                                                       unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, segment2_dir_path, brain_volume_dir_path, params['skip_analyzed'])

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def process_vbm_total_brain_volume(analysis_info_in: AnalysisInfo, segment2_dir_path: str, brain_volume_dir_path: str,
                                   skip_analyzed: bool, previous_node_analysis_info: Dict,
                                   unused_output_dir_path_list: List[str]) -> AnalysisInfo:
    """ Perform total brain volume calculation.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        segment2_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_segment2 node.
        brain_volume_dir_path : str
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
    analysis_info_out = analysis_info_in.create_new_analysis_info(NodeAnalysisType.TOTAL_BRAIN_VOLUME)

    # Process by each workflow input derivatives.
    for wf_input_path in analysis_info_in.workflow_input_file_path_list:
        # Workflow input file name without the extension.
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        try:
            # Skip analysis.
            if utils.skip_node_analysis(wf_input_path, skip_analyzed, previous_node_analysis_info):
                utils.remove_from_unused_list(join_filepath([brain_volume_dir_path, wf_input_name]),
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
                result = utils.check_derivatives_existence(segment2_dir_path, wf_input_name)
                if not result['exist']:
                    raise VbmException(f'[Error ({wf_input_name})] Input data not found in '
                                       f'{os.path.basename(result["missing_dir_path"])}.')
                # Delete the old output data if they exist.
                if utils.check_derivatives_existence(brain_volume_dir_path, wf_input_name)['exist']:
                    utils.delete_derivatives_data(brain_volume_dir_path, wf_input_name)

            # Calculate a total brain volume.
            analysis_info_out.set_analysis_start_time(wf_input_path)
            output_dir_path = utils.create_directory([brain_volume_dir_path, wf_input_name])
            output_file_path_list = calc_total_brain_volume(wf_input_name, segment2_dir_path, brain_volume_dir_path)

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


def calc_total_brain_volume(wf_input_name: str, segment2_dir_path: str, brain_volume_dir_path: str) -> List[str]:
    """ Calculate a total brain volume.

    Parameters
        ----------
        wf_input_name : str
            Workflow input file name without the extension.
        segment2_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_segment2 node.
        brain_volume_dir_path : str
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

    # Set a SelectFiles node.
    print(join_filepath(([segment2_dir_path, wf_input_name])))
    templates = {
        'segment2_c1': '{subject_id}/c1{subject_id}.nii',
        'segment2_c2': '{subject_id}/c2{subject_id}.nii'
    }
    select_files_node = Node(SelectFiles(templates), name='select_files')
    select_files_node.inputs.base_directory = segment2_dir_path
    select_files_node.inputs.subject_id = wf_input_name
    selected_files = select_files_node.run()

    # Load image data from NIfTI files.
    c1_nifti = nb.load(selected_files.outputs.segment2_c1)
    c2_nifti = nb.load(selected_files.outputs.segment2_c2)
    c1_image_data = c1_nifti.get_fdata()
    c2_image_data = c2_nifti.get_fdata()

    # Calculate the total brain volume.
    c1_volume_size = abs(np.linalg.det(c1_nifti.affine))
    c2_volume_size = abs(np.linalg.det(c2_nifti.affine))
    c1_brain_volume = sum(sum(sum(c1_image_data))) * c1_volume_size / 1000
    c2_brain_volume = sum(sum(sum(c2_image_data))) * c2_volume_size / 1000
    total_brain_volume = c1_brain_volume + c2_brain_volume

    # Save the volume in a CSV file.
    output_subdir_path = join_filepath(([brain_volume_dir_path, wf_input_name]))
    utils.create_directory(output_subdir_path)
    output_file_path = join_filepath([output_subdir_path, 'tbv.csv'])
    with open(output_file_path, mode='wt', encoding='utf-8') as file:
        file.write(str(total_brain_volume))

    # Return the paths of the output files saved in the analysis.
    return utils.get_derivatives_file_paths(brain_volume_dir_path, wf_input_name)


def create_dataset_description_file(function_name: str, input_dir_path: str, output_dir_path: str, skip_analyzed: bool):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path)]
    dataset_description = utils.get_dataset_description_template('Total brain volume', function_name,
                                                                 input_dir_name_list)
    dataset_description['Parameters']['skip_analyzed'] = skip_analyzed

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
