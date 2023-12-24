import json
import os
import sys
import traceback

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_normalization(
    analysis_info_in: AnalysisInfo,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Normalize brain MRI images by Nipype-SPM12 for VBM analysis.

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

    import nipype.interfaces.spm as spm

    # Make sure of the connection type.
    assert analysis_info_in.node_analysis_type == NodeAnalysisType.DARTEL

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directories.
    project_path = utils.get_project_path(params['project_id'])
    segment2_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'], NodeAnalysisType.SEGMENT2)
    dartel_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'], NodeAnalysisType.DARTEL)

    # Create the output derivatives directory if it does not exist.
    normalization_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'],
                                                                NodeAnalysisType.NORMALIZATION)

    # Set SPM12 standalone with MATLAB runtime.
    vbm_config = utils.load_config()
    matlab_command = utils.create_matlab_command(vbm_config['spm_script'], vbm_config['matlab_runtime'])
    spm.SPMCommand.set_mlab_paths(matlab_cmd=matlab_command, use_mcr=True)

    # Get the previous node analysis info in order to check if the analysis is skipped.
    previous_node_analysis_info = utils.get_previous_node_analysis_info(params)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(normalization_dir_path)

    # Perform the brain MRI image normalization processing by Nipype-SPM12.
    analysis_info_out = process_vbm_normalization(analysis_info_in, segment2_dir_path, dartel_dir_path,
                                                  normalization_dir_path, params['skip_analyzed'],
                                                  previous_node_analysis_info, unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, [segment2_dir_path, dartel_dir_path], normalization_dir_path,
                                    params['skip_analyzed'])

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def process_vbm_normalization(analysis_info_in: AnalysisInfo, segment2_dir_path: str, dartel_dir_path: str,
                              normalization_dir_path: str, skip_analyzed: bool, previous_node_analysis_info: Dict,
                              unused_output_dir_path_list: List[str]) -> AnalysisInfo:
    """ Perform the brain MRI image normalization processing by Nipype-SPM12.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        segment2_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_segment2 node.
        dartel_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_dartel node.
        normalization_dir_path : str
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
    analysis_info_out = analysis_info_in.create_new_analysis_info(NodeAnalysisType.NORMALIZATION)

    # Process by each workflow input derivatives.
    for wf_input_path in analysis_info_in.workflow_input_file_path_list:
        # Workflow input file name without the extension.
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        try:
            # Skip analysis.
            if utils.skip_node_analysis(wf_input_path, skip_analyzed, previous_node_analysis_info):
                utils.remove_from_unused_list(join_filepath([normalization_dir_path, wf_input_name]),
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
                result = utils.check_derivatives_existence([segment2_dir_path, dartel_dir_path], wf_input_name)
                if not result['exist']:
                    raise VbmException(f'[Error ({wf_input_name})] Input data not found in '
                                       f'{os.path.basename(result["missing_dir_path"])}.')
                # Delete the old output data if they exist.
                if utils.check_derivatives_existence(normalization_dir_path, wf_input_name)['exist']:
                    utils.delete_derivatives_data(normalization_dir_path, wf_input_name)

            # Normalize brain MRI images.
            analysis_info_out.set_analysis_start_time(wf_input_path)
            output_dir_path = utils.create_directory([normalization_dir_path, wf_input_name])
            output_file_path_list = normalize_brain_images(wf_input_name, os.path.dirname(segment2_dir_path),
                                                           normalization_dir_path)

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


def normalize_brain_images(wf_input_name: str, root_derivatives_dir_path: str, normalization_dir_path: str) -> List[str]:
    """ Normalize brain MRI images by Nipype-SPM12.
    See https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.spm.preprocess.html#createwarped
    for the details of the Nipype CreateWarped parameters.

    Parameters
        ----------
        wf_input_name : str
            Workflow input file name without the extension.
        root_derivatives_dir_path : str
            Path of the root derivatives directory.
        normalization_dir_path : str
            Path of the directory storing the analysis results performed by this node.

    Returns
        ----------
        output_file_path_list : list[str]
            Paths of the output files generated in the analysis.
    """

    from nipype import Node, Workflow
    from nipype.interfaces.io import SelectFiles, DataSink
    from nipype.interfaces.spm import CreateWarped
    from nipype.interfaces.utility import Merge

    # Set a SelectFiles node.
    templates = {
        'segment2_c1': 'segment2/{subject_id}/c1{subject_id}.nii',
        'segment2_c2': 'segment2/{subject_id}/c2{subject_id}.nii',
        'flow_field': 'dartel/{subject_id}/u_*_Template.nii'
    }
    select_files_node = Node(SelectFiles(templates), name='select_files')
    select_files_node.inputs.base_directory = root_derivatives_dir_path
    select_files_node.inputs.subject_id = wf_input_name

    # Set a normalization node.
    normalization_node = Node(CreateWarped(), name='normalization')
    normalization_node.inputs.modulate = True

    # Merge nodes.
    Node(Merge(2), name='merge')

    # Set a DataSink node.
    sink_node = Node(DataSink(), name='data_sink')
    sink_node.inputs.base_directory = normalization_dir_path

    # Create a workflow.
    wf = Workflow(name='vbm_normalization')
    wf.connect(select_files_node, 'flow_field', normalization_node, 'flowfield_files')
    wf.connect(select_files_node, 'segment2_c1', normalization_node, 'image_files')
    wf.connect(normalization_node, 'warped_files', sink_node, wf_input_name)

    # Run the workflow.
    wf.run()

    # Return the paths of the output files saved in the analysis.
    return utils.get_derivatives_file_paths(normalization_dir_path, wf_input_name)


def create_dataset_description_file(function_name: str, input_dir_path_list: List[str], output_dir_path: str,
                                    skip_analyzed: bool):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path) for input_dir_path in input_dir_path_list]
    dataset_description = utils.get_dataset_description_template('Normalization', function_name, input_dir_name_list)
    dataset_description['Parameters']['skip_analyzed'] = skip_analyzed

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
