import json
import os
import sys
import traceback
from typing import Dict, List, Optional, Tuple, Union

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
from optinist.wrappers.vbm_wrapper.vbm.nifti_image import NiftiImage
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_alignment(
    image_data: ImageData,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Set the new affine transformation matrix to NIfTI files based on the alignment parameters.

    Parameters
        ----------
        image_data : ImageData
            Come from the MRI data node.
            It has a set of NIfTI file IDs and the associated alignment parameters decided by alignment operations.
            Each image data is stored in the image_data.params['alignments'] list as the following dict.
                image_id (int): A file ID
                x_pos'   (int): X translation
                x_resize (int): X scaling
                x_rotate (int): X rotation
                y_pos    (int): Y translation
                y_resize (int): Y scaling
                y_rotate (int): Y rotation
                z_pos    (int): Z translation
                z_resize (int): Z scaling
                z_rotate (int): Z rotation
        params : dict
            Parameters defined in the vbm_template.yaml in addition to project ID, analysis ID, and node ID.
                project_id : Project ID
                analysis_id: Analysis ID
                node_id    : Node ID
    """

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the workflow input NIfTI file paths and alignment parameters.
    wf_input_path_list, alignment_params_list = set_workflow_input_data(image_data, params)

    # Create an output AnalysisInfo object.
    project_path = utils.get_project_path(params['project_id'])
    factors_dict = utils.get_factors(wf_input_path_list, project_path)
    analysis_info_out = AnalysisInfo(wf_input_path_list, factors_dict, NodeAnalysisType.ALIGNMENT)
    for wf_input_path in wf_input_path_list:
        analysis_info_out.set_property(wf_input_path, 'subject_name', utils.get_subject_name(wf_input_path))

    # Get the cleaned workflow input file paths from the AnalysisInfo object.
    wf_input_path_list = analysis_info_out.workflow_input_file_path_list

    # Create the output derivatives directory if it does not exist.
    alignment_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'],
                                                            NodeAnalysisType.ALIGNMENT)

    # Get the previous node analysis info in order to check if the analysis is skipped.
    previous_node_analysis_info = utils.get_previous_node_analysis_info(params)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(alignment_dir_path)

    # Perform the alignment processing by Nibabel.
    process_vbm_alignment(wf_input_path_list, alignment_params_list, analysis_info_out, alignment_dir_path,
                          params['skip_analyzed'], previous_node_analysis_info, unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, alignment_dir_path, params['skip_analyzed'])

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def set_workflow_input_data(image_data: ImageData, params: Dict) -> Tuple[List[str], List]:
    """ Set the workflow input NIfTI file paths and alignment parameters. """

    wf_input_path_list = []
    alignment_params_list = []
    image_id_list = []
    for image_data_params in image_data.params['alignments']:
        # Get the path of the NIfTI file from the Project Database based on the file ID.
        wf_input_path = utils.get_image_file_path(params['project_id'], image_data_params['image_id'])
        wf_input_path_list.append(wf_input_path)
        image_id_list.append(image_data_params['image_id'])

        # Rearrange the associated alignment parameters in a list.
        alignment_params_list.append(
            np.array([
                image_data_params['x_pos'],
                image_data_params['y_pos'],
                image_data_params['z_pos'],
                image_data_params['x_rotate'],
                image_data_params['y_rotate'],
                image_data_params['z_rotate'],
                image_data_params['x_resize'],
                image_data_params['y_resize'],
                image_data_params['z_resize']
            ]))

    # Save the image file IDs as the workflow input file IDs.
    utils.save_wf_input_file_id_list(params['project_id'], params['analysis_id'], image_id_list)

    return wf_input_path_list, alignment_params_list


def process_vbm_alignment(wf_input_path_list: List[str], alignment_params_list: List, analysis_info_out: AnalysisInfo,
                          alignment_dir_path: str, skip_analyzed: bool, previous_node_analysis_info: Dict,
                          unused_output_dir_path_list: List[str]):
    """ Perform the alignment processing by Nibabel.

    Parameters
        ----------
        wf_input_path_list : list[str]
            Paths of workflow input NIfTI files.
        alignment_params_list : list[ndarray[int]]
            A list of the parameters for aligning the brain MRI image.
            The element order follows that of wf_input_path_list.
            Parameters are as follows (Right notations are for SPM12).
                x_pos   : right (mm)
                y_pos   : forward (mm)
                z_pos   : up (mm)
                x_rotate: pitch (rad)
                y_rotate: roll (rad)
                z_rotate: yaw (rad)
                x_resize: resize (x)
                y_resize: resize (y)
                z_resize: resize (z)
        analysis_info_out : AnalysisInfo
            Store the info about VBM analysis performed in this node.
        alignment_dir_path : str
            Path of the directory storing the aligned NIfTI files.
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
    """

    # Process by each workflow input NIfTI file.
    for wf_input_path, alignment_params in zip(wf_input_path_list, alignment_params_list):
        # Workflow input file name without the extension.
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        try:
            # Skip analysis.
            if utils.skip_alignment(wf_input_path, skip_analyzed, previous_node_analysis_info, alignment_params):
                utils.remove_from_unused_list(join_filepath([alignment_dir_path, wf_input_name]),
                                              unused_output_dir_path_list)
                analysis_info_out.set_output_file_paths(wf_input_path, wf_input_path)
                analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.SKIPPED)
                print(f'Alignment {wf_input_name} skipped.')
                continue
            else:
                # Check if the workflow input file exists.
                if not os.path.isfile(wf_input_path):
                    raise VbmException(f'Workflow input file ({wf_input_name}) is not found.')

            print(f'Alignment {wf_input_name} not skipped.')
            # Set the new affine transformation matrix calculated with the alignment parameters to the NIfTI file.
            analysis_info_out.set_analysis_start_time(wf_input_path)
            output_dir_path = utils.create_directory([alignment_dir_path, wf_input_name])
            output_file_path = set_affine_matrix(wf_input_path, alignment_params, output_dir_path)

            # Remove this output directory from the unused list.
            utils.remove_from_unused_list(output_dir_path, unused_output_dir_path_list)

            # Set the analysis info.
            analysis_info_out.set_output_file_paths(wf_input_path, output_file_path)
            analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.PROCESSED)
        except:
            error_message = traceback.format_exc()
            print(f'[Error ({wf_input_name})]\n{error_message}')
            analysis_info_out.set_message(wf_input_path, error_message)
        finally:
            analysis_info_out.set_analysis_end_time(wf_input_path)


def set_affine_matrix(nifti_file_path: str, alignment_params, alignment_subdir_path: str) -> str:
    """ Set the affine transformation matrix calculated with the alignment parameters to a NIfTI file.

    Parameters
        ----------
        nifti_file_path : str
            Input NIfTI file path.
        alignment_params : ndarray[int]
            Parameters for aligning a brain MRI image as follows (Right notations are for SPM12).
                x_pos   : right (mm)
                y_pos   : forward (mm)
                z_pos   : up (mm)
                x_rotate: pitch (rad)
                y_rotate: roll (rad)
                z_rotate: yaw (rad)
                x_resize: resize (x)
                y_resize: resize (y)
                z_resize: resize (z)
        alignment_subdir_path : str
            Path of the directory storing the aligned NIfTI file.

    Returns
        ----------
        aligned_file_path : str
            Path of the aligned NIfTI file.
    """

    # Create a NiftiImage object.
    nifti = NiftiImage(nifti_file_path)

    # Update the affine transformation matrix.
    nifti.update_affine_matrix(np.append(alignment_params, [0, 0, 0]))

    # Set the output NIfTI file path.
    wf_input_file_name = os.path.basename(nifti_file_path)
    aligned_file_path = join_filepath([alignment_subdir_path, wf_input_file_name])

    nifti.save(aligned_file_path)

    return aligned_file_path


def create_dataset_description_file(function_name: str, output_dir_path: str, skip_analyzed: bool):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = ['Project root directory and/or ' + os.path.basename(output_dir_path)]
    dataset_description = utils.get_dataset_description_template('Alignment', function_name, input_dir_name_list)
    dataset_description['Parameters']['skip_analyzed'] = skip_analyzed

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
