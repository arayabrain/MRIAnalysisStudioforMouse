import csv
import itertools
import json
import os
import sys
import traceback

from optinist.api.dataclass.dataclass import *
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_stats_modeling(
    analysis_info_in: AnalysisInfo,
    params: dict=None
) -> dict(analysis_info_out=AnalysisInfo):
    """ Create two-sample t-test models for valid contrast pairs by Nipype-SPM12 for VBM analysis.

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
    assert (analysis_info_in.node_analysis_type == NodeAnalysisType.SMOOTHING) or \
           (analysis_info_in.node_analysis_type == NodeAnalysisType.TOTAL_BRAIN_VOLUME)

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directory.
    project_path = utils.get_project_path(params['project_id'])
    smoothing_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'],
                                                        NodeAnalysisType.SMOOTHING)
    brain_volume_dir_path = utils.get_derivatives_dir_path(project_path, params['analysis_id'],
                                                           NodeAnalysisType.TOTAL_BRAIN_VOLUME)

    # Create the output derivatives directory if it does not exist.
    model_dir_path = utils.create_derivatives_directory(project_path, params['analysis_id'],
                                                        NodeAnalysisType.STATS_MODELING)

    # Set SPM12 standalone with MATLAB runtime.
    vbm_config = utils.load_config()
    matlab_command = utils.create_matlab_command(vbm_config['spm_script'], vbm_config['matlab_runtime'])
    spm.SPMCommand.set_mlab_paths(matlab_cmd=matlab_command, use_mcr=True)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(model_dir_path)

    # Get the path lists of the workflow input files categorized by the between-factor and within-factor.
    grouped_wf_input_paths = analysis_info_in.get_grouped_workflow_input_file_paths()

    # Process two-sample t-test model creation by Nipype-SPM12.
    analysis_info_out = process_stats_model_creation(grouped_wf_input_paths, analysis_info_in, smoothing_dir_path,
                                                     brain_volume_dir_path, model_dir_path, unused_output_dir_path_list)

    # Throw an exception if none of the processings were successful.
    if analysis_info_out.get_analysis_status() == AnalysisStatus.ERROR:
        raise VbmException(f'All the processings were failed in {function_name} node. See experiment.yaml for details.')

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, [smoothing_dir_path, brain_volume_dir_path], model_dir_path)

    print(f'{function_name} finished.')

    return {'analysis_info_out': analysis_info_out}


def process_stats_model_creation(grouped_wf_input_paths: dict, analysis_info_in: AnalysisInfo,
                                 smoothing_dir_path: str, brain_volume_dir_path: str, model_dir_path: str,
                                 unused_output_dir_path_list: List[str]) -> AnalysisInfo:
    """ Process two-sample t-test model creation by Nipype-SPM12.

    Parameters
        ----------
        grouped_wf_input_paths : dict[tuple, list[str]]
            Path lists of the workflow input files categorized by the between-factor and within-factor.
        analysis_info_in : AnalysisInfo
            Info about VBM analysis performed in the previous node.
        smoothing_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_smoothing node.
        brain_volume_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_total_brain_volume node.
        model_dir_path : str
            Path of the directory storing the analysis results performed by this node.
        unused_output_dir_path_list : list[str]
            Paths of the previously generated output directories, but not included in the analysis.

    Returns
        ----------
        analysis_info_out : AnalysisInfo
            Info about VBM analysis performed in this node.
    """

    # Create an output AnalysisInfo template.
    analysis_info_out = analysis_info_in.create_new_analysis_info(NodeAnalysisType.STATS_MODELING)

    # Process by each valid contrast pair as follows.
    # 1. Between-factor pair (For groups consisting of a single element.)
    # 2. Within-factor pair with the same within-factor name (For groups consisting of two elements.)
    for contrast_pair in itertools.combinations(grouped_wf_input_paths.keys(), 2):
        contrast1_size = len(contrast_pair[0])
        contrast2_size = len(contrast_pair[1])
        # Check if a contrast pair is valid.
        if (contrast1_size == 1 and contrast2_size == 1) or \
                (contrast1_size == 2 and contrast2_size == 2 and contrast_pair[0][1] == contrast_pair[1][1]):
            # Get the contrast data.
            contrasts_name = utils.make_contrast_pair_name(contrast_pair)
            contrast1_input_path_list = sorted(grouped_wf_input_paths[contrast_pair[0]])
            contrast2_input_path_list = sorted(grouped_wf_input_paths[contrast_pair[1]])

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
                    else:
                        # Check if the input data exist.
                        result = utils.check_derivatives_existence([brain_volume_dir_path, smoothing_dir_path],
                                                                   wf_input_name)
                        if not result['exist']:
                            raise VbmException(f'[Error ({wf_input_name})] Input data not found in '
                                               f'{os.path.basename(result["missing_dir_path"])}.')

                # Delete the old output data if they exist.
                if utils.check_derivatives_existence(model_dir_path, contrasts_name)['exist']:
                    utils.delete_derivatives_data(model_dir_path, contrasts_name)

                # Create a two-sample t-test model by Nipype-SPM12.
                output_dir_path = utils.create_directory([model_dir_path, contrasts_name])
                output_file_path_list = create_two_sample_t_test_model(contrasts_name,
                                                                       contrast1_input_path_list,
                                                                       contrast2_input_path_list,
                                                                       smoothing_dir_path,
                                                                       brain_volume_dir_path,
                                                                       model_dir_path)

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


def create_two_sample_t_test_model(contrasts_name: str, contrast1_input_path_list: List[str],
                                   contrast2_input_path_list: List[str], smoothing_dir_path: str,
                                   brain_volume_dir_path: str, model_dir_path: str) -> List[str]:
    """ Create a two-sample t-test model by Nipype-SPM12.
    See https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.spm.model.html#twosamplettestdesign
    for the details of the Nipype TwoSampleTTestDesign parameters.

    Parameters
        ----------
        contrasts_name : str
            Contrast pair name.
        contrast1_input_path_list : list[str]
            Paths of workflow input files categorized by contrast1.
        contrast2_input_path_list : list[str]
            Paths of workflow input files categorized by contrast2.
        smoothing_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_smoothing node.
        brain_volume_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_total_brain_volume node.
        model_dir_path : str
            Path of the directory storing the analysis results performed by this node.

    Returns
        ----------
        output_file_path_list : list[str]
            Paths of the output files generated in the analysis.
    """

    from nipype import Node, Workflow
    from nipype.interfaces.io import DataSink
    from nipype.interfaces.spm.model import TwoSampleTTestDesign

    # Get contrast1 smoothed file paths.
    contrast1_smoothed_file_list = []
    for wf_input_path in contrast1_input_path_list:
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        path_list = utils.get_derivatives_file_paths(smoothing_dir_path, wf_input_name, f'smwc1{wf_input_name}.nii')
        contrast1_smoothed_file_list += path_list

    # Get contrast2 smoothed file paths.
    contrast2_smoothed_file_list = []
    for wf_input_path in contrast2_input_path_list:
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        path_list = utils.get_derivatives_file_paths(smoothing_dir_path, wf_input_name, f'smwc1{wf_input_name}.nii')
        contrast2_smoothed_file_list += path_list

    # Summarize the total brain volumes in a single file.
    brain_volume_list = []
    for wf_input_path in contrast1_input_path_list + contrast2_input_path_list:
        wf_input_name = utils.get_file_name_without_extension(wf_input_path)
        path_list = utils.get_derivatives_file_paths(brain_volume_dir_path, wf_input_name, 'tbv.csv')
        with open(path_list[0]) as file:
            reader = csv.reader(file)
            for row in reader:
                brain_volume_list.append(float(row[0]))
    model_subdir_path = join_filepath([model_dir_path, contrasts_name])
    total_brain_volume_file_path = join_filepath([model_subdir_path, 'tbv.csv'])
    with open(total_brain_volume_file_path, mode='wt', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(brain_volume_list)

    # Set a two-sample t-test modeling node.
    model_node = Node(TwoSampleTTestDesign(), name='vbm_stats_modeling')
    model_node.inputs.group1_files = contrast1_smoothed_file_list
    model_node.inputs.group2_files = contrast2_smoothed_file_list
    model_node.inputs.global_calc_values = brain_volume_list
    model_node.spm_mat_dir = model_subdir_path

    # Set a DataSink node.
    sink_node = Node(DataSink(), name='data_sink')
    sink_node.inputs.base_directory = model_dir_path

    # Creates a workflow.
    wf = Workflow(name='vbm_stats_modeling')
    wf.connect([(model_node, sink_node,
                 [('spm_mat_file', contrasts_name),
                  ])])

    # Run the workflow.
    wf.run()

    # Return the paths of the output files saved in the analysis.
    return utils.get_derivatives_file_paths(model_dir_path, contrasts_name)


def create_dataset_description_file(function_name: str, input_dir_path_list: List[str], output_dir_path: str):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path) for input_dir_path in input_dir_path_list]
    dataset_description = utils.get_dataset_description_template('Statistical modeling', function_name,
                                                                 input_dir_name_list)

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
