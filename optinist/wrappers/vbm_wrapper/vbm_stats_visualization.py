import json
import os
import sys
import traceback

from nilearn import plotting
from nipype import Node, Workflow
from nipype.interfaces.io import SelectFiles, DataSink
import nipype.interfaces.spm as spm
from nipype.interfaces.spm.model import Threshold

from optinist.api.dataclass.dataclass import *
from optinist.api.utils.filepath_creater import join_filepath
import optinist.wrappers.vbm_wrapper.vbm.utils as utils
from optinist.wrappers.vbm_wrapper.vbm_exception import VbmException


def vbm_stats_thresholding(project_id: int, analysis_id: str, p_value: float) -> List[str]:
    """ Threshold the statistical analysis results performed by the vbm_stats_analysis node.

    Parameters
        ----------
        project_id : int
        analysis_id : str
        p_value : float
            Applied to the following two parameters of the Nipype Threshold.
                height_threshold: Value for initial thresholding (defining clusters).
                extent_fdr_p_threshold: P threshold on FDR corrected cluster size probabilities.

    Returns
        ----------
        thresholded_file_path_list : List[str]
            A path list of the thresholded image files for each contrast pair.
    """

    function_name = sys._getframe().f_code.co_name
    print(f'{function_name} started.')

    # Set the input derivatives directories.
    project_path = utils.get_project_path(project_id)
    stats_dir_path = utils.get_derivatives_dir_path(project_path, analysis_id, NodeAnalysisType.STATS_ANALYSIS)

    if not os.path.isdir(stats_dir_path):
        raise VbmException(f'[Error] No statistical analysis results found.')

    # Create the output derivatives directory if it does not exist.
    visualization_dir_path = utils.create_derivatives_directory(project_path, analysis_id,
                                                                NodeAnalysisType.STATS_VISUALIZATION)

    # Set SPM12 standalone with MATLAB runtime.
    vbm_config = utils.load_config()
    matlab_command = utils.create_matlab_command(vbm_config['spm_script'], vbm_config['matlab_runtime'])
    spm.SPMCommand.set_mlab_paths(matlab_cmd=matlab_command, use_mcr=True)

    # Get the paths of the previously generated output directories in order to clean up
    # unused ones at the end of analysis.
    unused_output_dir_path_list = utils.get_subdir_path_list(visualization_dir_path)

    # Process statistical thresholding by Nipype-SPM12.
    thresholded_file_path_list = process_stats_thresholding(stats_dir_path, visualization_dir_path, p_value,
                                                            vbm_config['stats_visualization']['extent_threshold'],
                                                            unused_output_dir_path_list)

    # Delete output directories that were not included in this analysis.
    utils.delete_directories(unused_output_dir_path_list)

    # Save some analysis info in dataset_description.json.
    create_dataset_description_file(function_name, stats_dir_path, visualization_dir_path, vbm_config)

    print(f'{function_name} finished.')

    # Return the paths of the output image files.
    return thresholded_file_path_list


def process_stats_thresholding(stats_dir_path: str, visualization_dir_path: str, p_value: float,
                               extent_threshold: int, unused_output_dir_path_list: List[str]) -> List[str]:
    """ Process statistical analysis by Nipype-SPM12.

    Parameters
        ----------
        stats_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_stats_analysis node.
        visualization_dir_path : str
            Path of the directory storing the image files of the statistical analysis results.
        p_value : float
            Applied to the following two parameters of the Nipype Threshold.
                height_threshold: Value for initial thresholding (defining clusters).
                extent_fdr_p_threshold: P threshold on FDR corrected cluster size probabilities.
        extent_threshold : int
            Minimum cluster size in voxels.
        unused_output_dir_path_list : list[str]
            Paths of the previously generated output directories, but not included in the analysis.

    Returns
        ----------
        thresholded_file_path_list : List[str]
            A path list of the thresholded image files for each contrast pair.
    """

    # Get contrast pair names from the input directory name.
    stats_subdir_path_list = utils.get_subdir_path_list(stats_dir_path)
    contrasts_name_list = [os.path.basename(dir_path) for dir_path in stats_subdir_path_list]

    # Process by each valid contrast pair.
    thresholded_file_path_list = []
    for contrasts_name in contrasts_name_list:
        try:
            # Check if the input data exist.
            result = utils.check_derivatives_existence(stats_dir_path, contrasts_name)
            if not result['exist']:
                raise VbmException(f'[Error ({contrasts_name})] Input data not found in '
                                   f'{os.path.basename(result["missing_dir_path"])}.')

            # Delete the old output data if they exist.
            if utils.check_derivatives_existence(visualization_dir_path, contrasts_name)['exist']:
                utils.delete_derivatives_data(visualization_dir_path, contrasts_name)

            # Perform statistical thresholding by Nipype-SPM12.
            output_dir_path = utils.create_directory([visualization_dir_path, contrasts_name])
            output_file_path_list = perform_statistical_thresholding(contrasts_name, stats_dir_path,
                                                                     visualization_dir_path, p_value, extent_threshold)
            thresholded_file_path_list.append(output_file_path_list[0])

            # Remove this output directory from the unmanaged list.
            utils.remove_from_unused_list(output_dir_path, unused_output_dir_path_list)
        except:
            error_message = traceback.format_exc()
            print(f'[Error ({contrasts_name})] {error_message}')

    return thresholded_file_path_list


def perform_statistical_thresholding(contrasts_name: str, stats_dir_path: str, visualization_dir_path: str,
                                     p_value: float, extent_threshold: int = 0) -> List[str]:
    """ Perform statistical thresholding by Nipype-SPM12.
    See https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.spm.model.html#threshold
    for the details of the Nipype-SPM12 Thresholding.

    Parameters
        ----------
        contrasts_name : str
            Contrast pair name such as <Between-factor A><Within-factor X>-<Between-factor B><Within-factor X>.
        stats_dir_path : str
            Path of the directory storing the analysis results performed by the vbm_stats_analysis node.
        visualization_dir_path : str
            Path of the directory storing the image files of the statistical analysis results.
        p_value : float
            Applied to the following two parameters of the Nipype Threshold.
                height_threshold: Value for initial thresholding (defining clusters).
                extent_fdr_p_threshold: P threshold on FDR corrected cluster size probabilities.
        extent_threshold : int
            Minimum cluster size in voxels.

    Returns
        ----------
        output_file_path_list : list[str]
            Paths of the output files generated in the analysis.
    """

    # Set a SelectFiles node.
    templates = {
        'spm_mat': '{subject_id}/SPM.mat',
        'spmT_images': '{subject_id}/spmT_0001.nii'
    }
    select_files_node = Node(SelectFiles(templates), name='select_files')
    select_files_node.inputs.base_directory = stats_dir_path
    select_files_node.inputs.subject_id = contrasts_name

    # Set a thresholding node.
    thresholding_node = Node(Threshold(contrast_index=1,
                                       use_topo_fdr=True,
                                       use_fwe_correction=False,
                                       extent_threshold=extent_threshold,
                                       height_threshold=p_value,
                                       height_threshold_type='p-value',
                                       extent_fdr_p_threshold=p_value),
                             name='thresholding')

    # Set a DataSink node.
    sink_node = Node(DataSink(), name='data_sink')
    sink_node.inputs.base_directory = visualization_dir_path

    # Create a workflow.
    wf = Workflow(name='vbm_stats_visualization')
    wf.connect([(select_files_node, thresholding_node,
                 [('spm_mat_file', 'spm_mat_file'),
                  ('spmT_images', 'stat_image')
                  ])])
    wf.connect([(thresholding_node, sink_node,
                 [('thresholded_map', contrasts_name + '.@threshold')])])

    # Run the workflow.
    wf.run()

    # Return the paths of the output files saved in the analysis.
    return utils.get_derivatives_file_paths(visualization_dir_path, contrasts_name)


def create_stats_analysis_plot(stats_image_file_path: str, display_mode: str, threshold: Optional[Union[float, str]],
                                cut_coords: Tuple[Union[float, int]], vbm_config: Dict, plot_title: str,
                                output_dir_path: str) -> str:
    """ Create and save a statistical analysis plot from the images thresholded by vbm_stats_thresholding() function.
    Plots are created by the Nilearn's plotting function.
    See https://nilearn.github.io/dev/modules/generated/nilearn.plotting.plot_stat_map.html for details.

    Parameters
        ----------
        stats_image_file_path : str
            Path of a thresholded image file created by vbm_stats_thresholding() function.
        display_mode : str
            One of the following direction of the cuts.
                'x': Sagittal
                'y': Coronal
                'z': Axial
                'ortho': Three cuts are performed in orthogonal directions
                'tiled': Three cuts are performed and arranged in a 2x2 grid
                'mosaic': Three cuts are performed along multiple rows and columns
        threshold : float, None, or 'auto'
            Applied to the threshold parameter of Nilearn's plot_stat_map() function.
            float: It is used to threshold the image.
                values below the threshold (in absolute value) are plotted as transparent.
            None: The image is not thresholded.
            'auto': The threshold is determined magically by analysis of the image. Default is 1e-6.
        cut_coords : tuple[float or int]
            Coordinates of the point where the cut is performed in the averaged brain image.
        vbm_config : dict
            Configurations of the VBM analysis loaded from vbm_config.json in the form of
            config['stats_visualization'][<config name>] (ex., config['stats_visualization']['bg_image_file_path']).
        plot_title : str
        output_dir_path : str
    """

    EXTENSION = 'png'

    # Set the direction name.
    if display_mode == 'x':
        direction = 'sagittal'
    elif  display_mode == 'y':
        direction = 'coronal'
    elif  display_mode == 'z':
        direction = 'horizontal'
    else:
        direction = display_mode

    # Set the file path saving in the same directory as that of the input image file.
    # File name is <input file name>_<direction name>.png
    plot_file_path = join_filepath([
        output_dir_path,
        utils.get_file_name_without_extension(stats_image_file_path) + '_' + direction + '.' + EXTENSION])

    # Create a plot.
    display = plotting.plot_stat_map(stats_image_file_path,
                                     bg_img=vbm_config['stats_visualization']['bg_image_file_path'],
                                     cut_coords=cut_coords,
                                     display_mode=display_mode,
                                     title=plot_title,
                                     threshold=threshold,
                                     cmap=vbm_config['stats_visualization']['cmap'],
                                     symmetric_cbar=True,
                                     dim=vbm_config['stats_visualization']['dim'],
                                     vmax=vbm_config['stats_visualization']['vmax'])

    # Get the matplotlib handle, and add some vertical margins to fit the plot title.
    fig = display.frame_axes.figure
    fig_size = fig.get_size_inches()
    fig.set_size_inches(fig_size[0], fig_size[1] + 0.5)

    display.savefig(plot_file_path)

    return plot_file_path


def create_dataset_description_file(function_name: str, input_dir_path: str, output_dir_path: str, p_value: float,
                               extent_threshold: int):
    """ Save some analysis info in dataset_description.json. """

    # Create a dataset description dict.
    input_dir_name_list = [os.path.basename(input_dir_path)]
    dataset_description = utils.get_dataset_description_template('Statistical visualization', function_name,
                                                                 input_dir_name_list)
    dataset_description['Parameters']['p_value'] = p_value
    dataset_description['Parameters']['extent_threshold'] = extent_threshold

    # Save it in a JSON file.
    json_file_path = join_filepath([output_dir_path, 'dataset_description.json'])
    with open(json_file_path, mode='wt', encoding='utf-8') as file:
        json.dump(dataset_description, file, indent=2, ensure_ascii=False)
