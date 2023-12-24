import json
import os
import sys
import traceback

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_stats_analysis(
    analysis_info_in: AnalysisInfo,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Perform statistical analysis with the model created by the vbm_stats_modeling node for VBM analysis.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        params : dict
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
    assert analysis_info_in.node_analysis_type == NodeAnalysisType.STATS_MODELING

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directories.
    project_path = utils.get_project_path(params['project_id'])
    model_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'],
                                                    NodeAnalysisType.STATS_MODELING)

    # Create the output derivatives directory if it does not exist.
    stats_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'],
                                                        NodeAnalysisType.STATS_ANALYSIS)

    # Set SPM12 standalone with MATLAB runtime.
    vbm_config = utils.load_config()
    matlab_command = utils.create_matlab_command(vbm_config['spm_script'], vbm_config['matlab_runtime'])
    spm.SPMCommand.set_mlab_paths(matlab_cmd=matlab_command, use_mcr=True)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(stats_dir_path)

    # Process statistical analysis by Nipype-SPM12.
    analysis_info_out = process_stats_analysis(analysis_info_in, model_dir_path, stats_dir_path,
                                               unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, model_dir_path, stats_dir_path)

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def process_stats_analysis(analysis_info_in: AnalysisInfo, model_dir_path: str, stats_dir_path: str,
                           unused_output_dir_path_list: List[str]) -> AnalysisInfo:
    """ Process statistical analysis by Nipype-SPM12.

    Parameters
        ----------
        analysis_info_in : AnalysisInfo
            The info about VBM analysis performed in the previous node.
        model_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_stats_modeling node.
        stats_dir_path : str
            Path of the directory storing the analysis results performed by this node.
        unused_output_dir_path_list : list[str]
            Paths of the previously generated output directories, but not included in the analysis.

    Returns
        ----------
        analysis_info_out : AnalysisInfo
            Info about VBM analysis performed in this node.
    """

    # Create an output AnalysisInfo template.
    analysis_info_out = analysis_info_in.create_new_analysis_info(NodeAnalysisType.STATS_ANALYSIS)

    # Get the path lists of the workflow input files categorized by the between-factor and within-factor.
    grouped_wf_input_paths = analysis_info_in.get_grouped_workflow_input_file_paths()

    # Get contrast pair names from the directory name.
    model_subdir_path_list = utils.get_subdir_path_list(model_dir_path)
    contrasts_name_list = [os.path.basename(dir_path) for dir_path in model_subdir_path_list]

    # Process by each valid contrast pair.
    for contrasts_name in contrasts_name_list:
        # Get the paths of the workflow input files belonging to the contrasts.
        contrast1_key, contrast2_key = utils.get_contrast_pair_keys(contrasts_name)
        contrast1_input_path_list = sorted(grouped_wf_input_paths[contrast1_key])
        contrast2_input_path_list = sorted(grouped_wf_input_paths[contrast2_key])

        total_input_path_list = contrast1_input_path_list + contrast2_input_path_list
        try:
            # wf_input_path: workflow input file path.
            for wf_input_path in total_input_path_list:
                wf_input_name = utils.get_file_name_without_extension(wf_input_path)
                # Check a previous error.
                if analysis_info_in.get_analysis_status(wf_input_path) == AnalysisStatus.ERROR or \
                        analysis_info_in.get_analysis_status(wf_input_path) == AnalysisStatus.PREVIOUS_ERROR:
                    analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.PREVIOUS_ERROR)
                    raise VbmException(f'[Error ({wf_input_name})] Error occurred in the previous node analysis.\n'
                                       f'{analysis_info_in.get_message(wf_input_path)}')

            # Check if the input data exist.
            result = utils.check_derivatives_existence(model_dir_path, contrasts_name)
            if not result['exist']:
                raise VbmException(f'[Error ({contrasts_name})] Input data not found in '
                                   f'{os.path.basename(result["missing_dir_path"])}.')

            # Delete the old output data if they exist.
            if utils.check_derivatives_existence(stats_dir_path, contrasts_name)['exist']:
                utils.delete_derivatives_data(stats_dir_path, contrasts_name)

            # Perform statistical analysis by Nipype-SPM12.
            output_dir_path = utils.create_directory([stats_dir_path, contrasts_name])
            output_file_path_list = perform_statistical_analysis(contrasts_name, model_dir_path, stats_dir_path)

            # Remove this output directory from the unmanaged list.
            utils.remove_from_unused_list(output_dir_path, unused_output_dir_path_list)

            # Set the analysis info.
            for wf_input_path in total_input_path_list:
                analysis_info_out.set_output_file_paths(wf_input_path, output_file_path_list)
                analysis_info_out.set_analysis_status(wf_input_path, AnalysisStatus.PROCESSED)
        except:
            error_message = traceback.format_exc()
            for wf_input_path in total_input_path_list:
                print(f'[Error ({utils.get_file_name_without_extension(wf_input_path)})] {error_message}')
                analysis_info_out.set_message(wf_input_path, error_message)

    return analysis_info_out


def perform_statistical_analysis(contrasts_name: str, model_dir_path: str, stats_dir_path: str) -> List[str]:
    """ Perform statistical analysis by Nipype-SPM12.
    See https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.spm.model.html#estimatemodel and
    https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.spm.model.html#estimatecontrast
    for the details of the Nipype EstimateModel and EstimateContrast parameters, respectively.

    Parameters
        ----------
        contrasts_name : str
            Contrast pair name such as <Between-factor A><Within-factor X>-<Between-factor B><Within-factor X>.
        model_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_stats_modeling node.
        stats_dir_path : str
            Path of the directory storing the analysis results performed by this node.

    Returns
        ----------
        output_file_path_list : list[str]
            Paths of the output files generated in the analysis.
    """

    from nipype import Node, Workflow
    from nipype.interfaces.io import SelectFiles, DataSink
    from nipype.interfaces.spm.model import EstimateModel, EstimateContrast

    # Set a SelectFiles node.
    templates = {'spm_mat': '{subject_id}/SPM.mat'}
    select_files_node = Node(SelectFiles(templates), name='select_files')
    select_files_node.inputs.base_directory = model_dir_path
    select_files_node.inputs.subject_id = contrasts_name

    # Set an EstimateModel node.
    estimate_model_node = Node(EstimateModel(estimation_method={'Classical': 1}), name='estimate_model')

    # Get contrast names such as <Between-factor A><Within-factor X>.
    index = contrasts_name.find('>-<')
    contrast1_name = contrasts_name[:(index + 1)]
    contrast2_name = contrasts_name[(index + 2):]

    # Set an EstimateContrast node.
    estimate_contrast_node = Node(EstimateContrast(), name='estimate_contrast')
    contrast1 = (contrast1_name + '>' + contrast2_name, 'T', ['Group_{1}', 'Group_{2}'], [1, -1])
    contrast2 = (contrast1_name + '<' + contrast2_name, 'T', ['Group_{1}', 'Group_{2}'], [-1, 1])
    estimate_contrast_node.inputs.contrasts = [contrast1, contrast2]
    estimate_contrast_node.inputs.group_contrast = True

    # Set a DataSink node.
    sink_node = Node(DataSink(), name='data_sink')
    sink_node.inputs.base_directory = stats_dir_path

    # Create a workflow.
    wf = Workflow(name='vbm_stats_analysis')
    wf.connect(select_files_node, 'spm_mat', estimate_model_node, 'spm_mat_file')
    wf.connect([(estimate_model_node, estimate_contrast_node,
                 [('spm_mat_file', 'spm_mat_file'),
                  ('beta_images', 'beta_images'),
                  ('residual_image', 'residual_image'),
                  ])])
    wf.connect([(estimate_contrast_node, sink_node,
                 [('spm_mat_file', contrasts_name + '.@spm_mat'),
                  ('spmT_images', contrasts_name + '.@T'),
                  ('con_images', contrasts_name + '.@con'),
                  ])])

    # Run the workflow.
    wf.run()

    # Return the paths of the output files saved in the analysis.
    return utils.get_derivatives_file_paths(stats_dir_path, contrasts_name)


def create_dataset_description_file(function_name: str, input_dir_path: str, output_dir_path: str):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path)]
    dataset_description = utils.get_dataset_description_template('Statistical analysis', function_name,
                                                                 input_dir_name_list)

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
