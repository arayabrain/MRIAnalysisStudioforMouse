import glob
import json
import os
import pathlib
import re
import shutil
from typing import Dict, List, Optional, Tuple, Union
import yaml

from optinist.api.config.config_reader import ConfigReader
from optinist.api.config.config_writer import ConfigWriter
from optinist.api.dataclass.analysis_info import NodeAnalysisType
from optinist.api.dir_path import DIRPATH
from optinist.api.utils.filepath_creater import join_filepath
import optinist.routers.workdbmanager as db


# This file holds the necessary info about the ongoing workflow analysis.
WORKFLOW_INFO_FILE_NAME = 'workflow_info.yaml'

# This file saves the path and ID of the files registered in the project.
FILEMAP_FILE_NAME = 'filemap.json'

# This file saves the path and ID of the files registered in the project.
DATASET_DESCRIPTION_FILE_NAME = 'dataset_description.json'


def get_project_path(project_id: int) -> str:
    """ Get the project path from Work DB. """
    return db.get_project_path(project_id)


def get_image_file_path(project_id: int, image_file_id: int) -> str:
    """ Get the workflow input file path corresponding to an image file ID from Work DB. """
    return db.get_work_project_image_path(project_id, image_file_id)


def get_project_name(project_id: int):
    dataset_description_file_path = join_filepath([get_project_path(int(project_id)), DATASET_DESCRIPTION_FILE_NAME])
    dataset_description_data = read_json_file(dataset_description_file_path)
    return dataset_description_data['Name']


def save_wf_input_file_id_list(project_id: int, analysis_id: str, image_file_id_list: List[int]):
    """ Save the workflow input file IDs in workflow_info.yaml. """

    # Get the workflow info from workflow_info.yaml.
    workflow_output_path = join_filepath([DIRPATH.OUTPUT_DIR, str(project_id), analysis_id])
    file_path = join_filepath([workflow_output_path, WORKFLOW_INFO_FILE_NAME])
    workflow_info = ConfigReader.read(file_path) if os.path.isfile(file_path) else {}

    # Set the image file IDs as the workflow input file IDs.
    workflow_info['wf_input_file_id_list'] = image_file_id_list

    # Save the workflow info in workflow_info.yaml.
    ConfigWriter.write(
        dirname=workflow_output_path,
        filename=WORKFLOW_INFO_FILE_NAME,
        config=workflow_info
    )


def get_wf_input_file_id_list(project_id: int, analysis_id: str) -> List[int]:
    """ Get the workflow input file IDs from workflow_info.yaml if it exists. """

    # Get the workflow info from workflow_info.yaml.
    file_path = join_filepath([DIRPATH.OUTPUT_DIR, str(project_id), analysis_id, WORKFLOW_INFO_FILE_NAME])
    try:
        workflow_info = ConfigReader.read(file_path)

        return workflow_info['wf_input_file_id_list']
    except:
        return []


def get_subject_name(wf_input_path: str) -> str:
    """ Get the subject name from a workflow input file name based on the BIDS naming convention.

    Parameters
        ----------
        wf_input_path : str
            Workflow input file path.
    """

    file_name = os.path.basename(wf_input_path)
    tokens = file_name.split('_')
    subject_name = tokens[0].split('-')[1]
    return subject_name


def get_file_name_without_extension(file_path: str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]


def get_subdir_path_list(dir_path: str) -> List[str]:
    files = os.listdir(dir_path)
    subdir_list = []
    for file in files:
        path = join_filepath([dir_path, file])
        if os.path.isdir(path):
            subdir_list.append(path)
    return subdir_list


def create_directory(dir_path: Union[str, List[str]]) -> str:
    """ Create directory if it does not exist. """

    if isinstance(dir_path, list):
        dir_path = join_filepath(dir_path)

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    return dir_path


def delete_directories(dir_path_list: Union[str, List[str]]):
    # If dir_path_list is str, convert it to list.
    if isinstance(dir_path_list, str):
        dir_path_list = [dir_path_list]

    for dir_path in dir_path_list:
        shutil.rmtree(dir_path)


def read_json_file(file_path) -> Dict:
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data


def get_derivatives_dir_path(project_path: str, analysis_id: str, node_name: Union[NodeAnalysisType, str] = None,
                             subdir_path: Optional[str] = None) -> str:
    """ Get a derivatives directory path below the root derivatives directory for a given analysis ID.

    Returns
        ----------
        derivatives_dir_path : str
            <project path>/derivatives/<analysis ID>/<node name (optional)>/<subdir (optional)>
    """

    # If node_name is NodeAnalysisType enum, convert it to the corresponding str.
    if isinstance(node_name, NodeAnalysisType):
        node_name = node_name.value

    path_list = [project_path, 'derivatives', analysis_id]
    if node_name is not None:
        path_list.append(node_name)
        if subdir_path is not None:
            path_list.append(subdir_path)

    return join_filepath(path_list)


def create_derivatives_directory(project_path: str, analysis_id: str, node_name: Union[NodeAnalysisType, str] = None,
                                 subdir_path: Optional[str] = None) -> str:
    """ Create a derivatives directory below the root derivatives directory for a given analysis ID.

    Returns
        ----------
        derivatives_dir_path : str
            <project path>/derivatives/<analysis ID>/<node name (optional)>/<subdir (optional)>
    """

    derivatives_dir_path = get_derivatives_dir_path(project_path, analysis_id, node_name, subdir_path)

    # Create directory if it does not exist.
    if not os.path.isdir(derivatives_dir_path):
        os.makedirs(derivatives_dir_path)

    return derivatives_dir_path


def check_derivatives_existence(node_derivatives_dir_path_list: Union[str, List[str]], subdir_path: str) -> Dict:
    """ Check if the directory exists with some files in it.

    Returns
        ----------
        result : dict
            'exist' : bool
                True if the directory exists with some files in it.
            'missing_dir_path' : str
                Directory path if the directory cannot be found or has no files, otherwise return an empty string.
    """

    # If node_derivatives_dir_path_list is str, convert it to list.
    if isinstance(node_derivatives_dir_path_list, str):
        node_derivatives_dir_path_list = [node_derivatives_dir_path_list]

    result = {'exist': True, 'missing_dir_path': ''}

    for node_derivatives_dir_path in node_derivatives_dir_path_list:
        # Make the target directory path (<node derivatives dir path>/<subdir path>)
        dir_path = join_filepath([node_derivatives_dir_path, subdir_path])
        if os.path.isdir(dir_path):
            file_list = os.listdir(dir_path)
            if len(file_list) == 0:
                result['exist'] = False
                result['missing_dir_path'] = dir_path
                return result
        else:
            result['exist'] = False
            result['missing_dir_path'] = dir_path
            return result

    return result


def get_derivatives_file_paths(node_derivatives_dir_path: str, subdir_path: Optional[str] = None,
                               file_name_pattern: str = '*') -> List[str]:
    """ Return the paths of the files saved in a given derivatives directory.
    Specify the path as <node derivatives dir path>/<subdir path (optional)>/<file name pattern (optional)>.
    <file name pattern> can be f-string.
    """

    path_list = [node_derivatives_dir_path]
    if subdir_path is not None:
        path_list.append(subdir_path)
    search_path = glob.escape(join_filepath(path_list))
    search_path = join_filepath([search_path, file_name_pattern])
    return [path for path in glob.glob(search_path) if os.path.isfile(path)]


def delete_derivatives_data(node_derivatives_dir_path: str, subdir_path: str):
    """ Delete files and directories in a given derivatives directory (<node derivatives dir path>/<subdir path>). """
    shutil.rmtree(join_filepath([node_derivatives_dir_path, subdir_path]))


def load_config() -> Dict:
    """ Load the configurations of the VBM analysis from vbm_config.json.
    vbm_config.json is assumed to be saved in "/wrappers/vbm_wrapper/vbm".

    Returns
        ----------
        config : dict
            config[<node name>][<config name>] (ex., config['segment1']['tpm_path'])
    """

    PATH_TO_CONFIG_FILE = 'wrappers/vbm_wrapper/vbm/vbm_config.yaml'

    config_file_path = join_filepath([DIRPATH.ROOT_DIR, PATH_TO_CONFIG_FILE])
    config = {}
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as file:
            config = yaml.safe_load(file)

    return config


def create_matlab_command(spm_standalone_path, matlab_runtime_path) -> str:
    """ Make a Nipype command to set the SPM and MATLAB runtime.

    Parameters
        ----------
        spm_standalone_path : str
            Path to run_spm12.sh (Linux).
        matlab_runtime_path : str
            Path to the MATLAB runtime root directory (ex., /usr/local/MATLAB/MATLAB_Runtime/R2022b/).
    """

    return "{0} {1} script".format(spm_standalone_path, matlab_runtime_path)


def __search_factors(factors_info, relative_wf_input_path, previous_factor: Optional[str], project_path, factors_dict):
    """ Search for the between-factor and within-factor names for a given workflow input file.
    Those factor names will be stored in factors_dict if they are found.
    This function is called by get_factors().

    Parameters
        ----------
        factors_info : dict
            Info about factors and workflow input files.
            Data structure follows that of filemap.json.
        relative_wf_input_path : str
            Relative path of the workflow input file.
        previous_factor : str or None
            Tha factor name one layer above.
        factors_dict : dict[<absolute workflow input file path>, list[<between-factor name>, <within-factor name (optional)>]]
            Store factor names if they are found.
    """

    if relative_wf_input_path in factors_dict.keys():
        return

    for factor_dict in factors_info:
        for image in factor_dict['images']:
            if image['path'] == relative_wf_input_path:
                # Revert to the absolute path.
                wf_input_path = join_filepath([project_path, relative_wf_input_path])
                if previous_factor is None:
                    factors_dict[wf_input_path] = [factor_dict['folder_name']]
                else:
                    factors_dict[wf_input_path] = [previous_factor, factor_dict['folder_name']]
                return

        if 'sub_folders' in factor_dict.keys():
            previous_factor = factor_dict['folder_name']
            __search_factors(factor_dict['sub_folders'], relative_wf_input_path, previous_factor, project_path, factors_dict)
            previous_factor = None


def get_factors(wf_input_path_list: List[str], project_path: str) -> Dict[str, List[str]]:
    """ Get the between-factor and within-factor names for the workflow input files from filemap.json.

    Returns
        ----------
        factors_dict : dict[<absolute workflow input file path>, list[<between-factor name>, <within-factor name (optional)>]]
    """

    # Get the filemap.json path.
    # This file is assumed to be saved in the project directory.
    filemap_path = join_filepath([project_path, FILEMAP_FILE_NAME])

    # Get the between-factor and within-factor names recursively for each workflow input file from filemap.json.
    factors_dict = {}
    with open(filemap_path) as file:
        factors_info = json.load(file)
        for wf_input_path in wf_input_path_list:
            # Change the project path to the relative because paths in filemap.json are relative to the project directory.
            relative_wf_input_path = str(pathlib.Path(wf_input_path).relative_to(project_path))
            previous_factor = None
            __search_factors(factors_info, relative_wf_input_path, previous_factor, project_path, factors_dict)

    return factors_dict


def get_previous_node_analysis_info(params: Dict) -> Dict:
    """ Get the previous node analysis info from workflow_info.yaml if it exists.

    Returns
        ----------
        node_analysis_info : dict
            Key: Workflow input file path
            Value : dict
                output_file_paths (list[str])): Paths of the output files generated in the node analysis.
                success (str): Analysis status message ('success' or 'error').
                message (str): Any additional message.
    """

    # Get the workflow info from workflow_info.yaml.
    file_path = join_filepath([DIRPATH.OUTPUT_DIR, str(params['project_id']), params['analysis_id'],
                               WORKFLOW_INFO_FILE_NAME])
    try:
        workflow_info = ConfigReader.read(file_path)

        # Return the node analysis info.
        return workflow_info['node_analysis'][params['node_id']]
    except:
        return {}


def skip_alignment(wf_input_path: str, skip_analyzed: bool, previous_node_analysis_info: Dict,
                   alignment_params) -> bool:
    """ Check if the alignment processing can be skipped or not for a given workflow input file.

    Parameters
        ----------
        wf_input_path : str
            Path of the workflow NIfTI input file.
        skip_analyzed: bool
            True for checking if the analysis can be skipped for inputs that have been already analyzed before,
            otherwise reanalyze anyway.
        previous_node_analysis_info : dict
            Key: Workflow input file path
            Value : dict
                output_file_paths (list[str])): Paths of the output files generated in the node analysis.
                success (str): Analysis status message ('success' or 'error').
                message (str): Any additional message.
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

    Returns
        ----------
        True: Skip analysis.
        False: Analyze anyway.
    """

    DEFAULT_ALIGNMENT_PARAMS = [0, 0, 0, 0, 0, 0, 1, 1, 1]

    # Check if the node analysis can be skipped or not for a given workflow input file.
    if not skip_node_analysis(wf_input_path, skip_analyzed, previous_node_analysis_info):
        return False

    # Also, do not skip analysis if the alignment parameters have been modified.
    if not (alignment_params == DEFAULT_ALIGNMENT_PARAMS).all():
        return False

    return True


def skip_node_analysis(wf_input_path: str, skip_analyzed: bool, previous_node_analysis_info: Dict) -> bool:
    """ Check if the node analysis can be skipped or not for a given workflow input file.

    Parameters
        ----------
        wf_input_path : str
            Path of the workflow NIfTI input file.
        skip_analyzed: bool
            True for checking if the analysis can be skipped for inputs that have been already analyzed before,
            otherwise reanalyze anyway.
        previous_node_analysis_info : dict
            Key: Workflow input file path
            Value : dict
                output_file_paths (list[str])): Paths of the output files generated in the node analysis.
                success (str): Analysis status message ('success' or 'error').
                message (str): Any additional message.

    Returns
        ----------
        True: Skip analysis.
        False: Analyze anyway.
    """

    if not skip_analyzed:
        return False

    # Skip analysis if the workflow input file is included in the previous dataset.
    if wf_input_path in previous_node_analysis_info.keys():
        if previous_node_analysis_info[wf_input_path]['success'] != 'success':
            return False
        for output_file_path in previous_node_analysis_info[wf_input_path]['output_file_paths']:
            if not os.path.isfile(output_file_path):
                return False
        return True
    else:
        return False


def remove_from_unused_list(output_subdir_path: str, unused_output_dir_path_list: List[str]):
    """ Remove the specified output directory from the unused output directory list.

    Parameters
        ----------
        output_subdir_path : str
            Output directory path (<node derivatives dir path>/<workflow input file name)>).
        unused_output_dir_path_list : list[str]
            Paths of the previously generated output directories that are not included in the analysis.
    """

    if output_subdir_path in unused_output_dir_path_list:
        unused_output_dir_path_list.remove(output_subdir_path)


def make_contrast_pair_name(contrast_pair: List[Tuple]) -> str:
    """ Return a contrast pair name such as [Between-factor A][Within-factor X]-[Between-factor B][Within-factor X].

    Parameters
        ----------
        contrast_pair : list[tuple[str]]
            [
                (<contrast1_between-factor>, <contrast1_within-factor (optional)>),
                (<contrast2_between-factor>, <contrast2_within-factor (optional)>)
            ]
    """

    contrast1_name = ''.join(['<' + contrast_name + '>' for contrast_name in contrast_pair[0]])
    contrast2_name = ''.join(['<' + contrast_name + '>' for contrast_name in contrast_pair[1]])
    return contrast1_name + '-' + contrast2_name


def get_contrast_pair_keys(contrast_pair_name: str) -> Optional[Tuple[Tuple, tuple]]:
    """ Get the tuple form of contrast names from a contrast pair name
    such as [Between-factor A][Within-factor X]-[Between-factor B][Within-factor X].

    Returns
        ----------
        contrast_pair_keys : list[tuple[str]]
            [
                (<contrast1_between-factor>, <contrast1_within-factor (optional)>),
                (<contrast2_between-factor>, <contrast2_within-factor (optional)>)
            ]
    """

    pattern = r'<(.*?)>'
    results = re.findall(pattern, contrast_pair_name)

    # No within-factor.
    if len(results) == 2:
        return tuple(results[0]), tuple(results[1])
    # Between-factor and within-factor.
    elif len(results) == 4:
        return tuple(results[0:2]), tuple(results[2:4])
    else:
        return None


def get_dataset_description_template(title: str, function_name: str, input_dir_name_list: List[str]) -> Dict:
    """ Provide a template dict of the dataset description which will be saved in dataset_description.json. """

    return {
        'Name': title,
        'BIDSVersion': 'This dataset does not follow the BIDS format.',
        'GeneratedBy':
            {
                'ProgramName': 'MRI Cloud Analysis-230707',
                'FunctionName': function_name
            },
        'Parameters':
            {
                'InputDir': input_dir_name_list
            }
    }
