import json
import os
import sys
import traceback

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_segment1(
    analysis_info_in: AnalysisInfo,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Segment brain MRI images into some tissues such as the gray matter by Nipype-SPM12 for VBM analysis.

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
    assert analysis_info_in.node_analysis_type == NodeAnalysisType.ALIGNMENT, 'This node connection is not allowed.'

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directory.
    project_path = utils.get_project_path(params['project_id'])
    alignment_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'],
                                                        NodeAnalysisType.ALIGNMENT)

    # Create the output derivatives directory if it does not exist.
    segment1_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'],
                                                           NodeAnalysisType.SEGMENT1)

    # Set SPM12 standalone with MATLAB runtime.
    vbm_config = utils.load_config()
    matlab_command = utils.create_matlab_command(vbm_config['spm_script'], vbm_config['matlab_runtime'])
    spm.SPMCommand.set_mlab_paths(matlab_cmd=matlab_command, use_mcr=True)

    # Get the previous node analysis info in order to check if the analysis is skipped.
    previous_node_analysis_info = utils.get_previous_node_analysis_info(params)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(segment1_dir_path)

    # Perform the brain MRI image segmentation processing by Nipype-SPM12.
    analysis_info_out = process_vbm_segment1(analysis_info_in, alignment_dir_path, segment1_dir_path,
                                             params['skip_analyzed'], vbm_config['segment1']['tpm_path'],
                                             previous_node_analysis_info, unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, alignment_dir_path, segment1_dir_path, params['skip_analyzed'],
                                    vbm_config['segment1']['tpm_path'])

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def process_vbm_segment1(analysis_info_in: AnalysisInfo, alignment_dir_path: str, segment1_dir_path: str,
                         skip_analyzed: bool, tpm_path: str, previous_node_analysis_info: Dict,
                         unused_output_dir_path_list: List[str]) -> AnalysisInfo:
    """ Perform the brain MRI image segmentation processing by Nipype-SPM12.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        alignment_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_alignment node.
        segment1_dir_path : str
            Path of the directory storing the analysis results performed by this node.
        skip_analyzed: bool
            True for checking if the analysis can be skipped for inputs that have been already analyzed before,
            otherwise reanalyze anyway.
        tpm_path: str
            Path of the directory storing the tissue probability map (TPM) files.
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
    analysis_info_out = analysis_info_in.create_new_analysis_info(NodeAnalysisType.SEGMENT1)

    # Process by each workflow input derivatives.
    for wf_input_path in analysis_info_in.workflow_input_file_path_list:
        # Workflow input file name without the extension.
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        try:
            # Skip analysis.
            if utils.skip_node_analysis(wf_input_path, skip_analyzed, previous_node_analysis_info):
                utils.remove_from_unused_list(join_filepath([segment1_dir_path, wf_input_name]),
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
                result = utils.check_derivatives_existence(alignment_dir_path, wf_input_name)
                if not result['exist']:
                    raise VbmException(f'[Error ({wf_input_name})] Input data not found in '
                                       f'{os.path.basename(result["missing_dir_path"])}.')
                # Delete the old output data if they exist.
                if utils.check_derivatives_existence(segment1_dir_path, wf_input_name)['exist']:
                    utils.delete_derivatives_data(segment1_dir_path, wf_input_name)

            # Segment brain MRI images.
            analysis_info_out.set_analysis_start_time(wf_input_path)
            output_dir_path = utils.create_directory([segment1_dir_path, wf_input_name])
            output_file_path_list = segment_brain_images(wf_input_name, alignment_dir_path, segment1_dir_path, tpm_path)

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


def segment_brain_images(wf_input_name: str, alignment_dir_path: str, segment1_dir_path: str, tpm_path: str) -> List[str]:
    """ Segment brain MRI images into some tissues such as the gray matter by Nipype-SPM12.
    See https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.spm.preprocess.html#newsegment
    for the details of the Nipype NewSegment parameters.

    Parameters
        ----------
        wf_input_name : str
            Workflow input file name without the extension.
        alignment_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_alignment node.
        segment1_dir_path : str
            Path of the directory storing the analysis results performed by this node.
        tpm_path : str
            Path of the directory storing the tissue probability map (TPM) files.

    Returns
        ----------
        output_file_path_list : list[str]
            Paths of the output files generated in the analysis.
    """

    from nipype import Node, Workflow
    from nipype.interfaces.io import SelectFiles, DataSink
    from nipype.interfaces.spm import NewSegment

    # Set a SelectFiles node.
    templates = {'alignment': '{subject_id}/{subject_id}.nii'}
    select_files_node = Node(SelectFiles(templates), name='select_files')
    select_files_node.inputs.base_directory = alignment_dir_path
    select_files_node.inputs.subject_id = wf_input_name

    # Set a segmentation node.
    tissue1 = ((join_filepath([tpm_path, '01_GM.nii']), 1), 1, (True, True), (True, True))
    tissue2 = ((join_filepath([tpm_path, '02_WM.nii']), 1), 1, (True, True), (True, True))
    tissue3 = ((join_filepath([tpm_path, '03_CSF.nii']), 1), 2, (True, True), (True, True))
    tissue4 = ((join_filepath([tpm_path, '04.nii']), 1), 3, (True, False), (False, False))
    tissue5 = ((join_filepath([tpm_path, '05.nii']), 1), 4, (True, False), (False, False))
    tissue6 = ((join_filepath([tpm_path, '06.nii']), 1), 2, (False, False), (False, False))
    tissues = [tissue1, tissue2, tissue3, tissue4, tissue5, tissue6]
    segment_node = Node(NewSegment(tissues=tissues), name='segment')

    # Set a DataSink node.
    sink_node = Node(DataSink(), name='data_sink')
    sink_node.inputs.base_directory = segment1_dir_path

    # Create a workflow.
    wf = Workflow(name='vbm_segment1')
    wf.connect(select_files_node, 'alignment', segment_node, 'channel_files')
    wf.connect([(segment_node, sink_node,
                 [('transformation_mat', wf_input_name),
                  ('native_class_images', wf_input_name + '.@native'),
                  ('dartel_input_images', wf_input_name + '.@dartel'),
                  ('modulated_class_images', wf_input_name + '.@modulated'),
                  ('normalized_class_images', wf_input_name + '.@normalized'),
                  ])])

    # Run the workflow.
    wf.run()

    # Return the paths of the output files generated in the analysis.
    return utils.get_derivatives_file_paths(segment1_dir_path, wf_input_name)


def create_dataset_description_file(function_name: str, input_dir_path: str, output_dir_path: str,
                                    skip_analyzed: bool, tpm_path: str):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path)]
    dataset_description = utils.get_dataset_description_template('1st segmentation', function_name,
                                                                 input_dir_name_list)
    dataset_description['Parameters']['skip_analyzed'] = skip_analyzed
    dataset_description['Parameters']['tpm_path'] = tpm_path

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
