from enum import Enum
import json
import os
import re
from typing import List, Dict

from optinist.api.dataclass.base import BaseData
from optinist.api.dataclass.utils import check_path_format


""" analysis_info.py
The analysis info of a node in a workflow, which is used by the node to transmit the info to the next.
"""


class AnalysisStatus(Enum):
    """
    The enum to represent the analysis status for a workflow input file in a node.
    """

    UNKNOWN = 0
    WAIT = 1
    PROCESSING = 2
    PROCESSED = 3
    ERROR = 4


class AnalysisInfo(BaseData):
    """
    Store the analysis info in a node.
    """

    def __init__(self, wf_input_file_path_list: List[str], project_path: str, file_name='analysis_info'):
        super().__init__(file_name)
        """
        [arguments]
        wf_input_file_path_list: A list of the workflow input file paths.
        """

        self.__project_path = project_path
        self.__analysis_start_time = None
        self.__analysis_end_time = None

        # A list of the workflow input file paths.
        self.__wf_input_file_path_list: List[str] = check_path_format(wf_input_file_path_list)

        # A dict of the workflow input file path key and UnitAnalysisInfo object value,
        # which collectively stores the analysis info in a node.
        self.__unit_analysis_info_dict: Dict[str, UnitAnalysisInfo] = {}
        for wf_input_path in self.__wf_input_file_path_list:
            self.__unit_analysis_info_dict[wf_input_path] = UnitAnalysisInfo(wf_input_path)

    @property
    def project_path(self):
        return self.__project_path

    @property
    def analysis_start_time(self):
        return self.__analysis_start_time

    @analysis_start_time.setter
    def analysis_start_time(self, val: str):
        self.__analysis_start_time = val

    @property
    def analysis_end_time(self):
        return self.__analysis_end_time

    @analysis_end_time.setter
    def analysis_end_time(self, val: str):
        self.__analysis_end_time = val

    @property
    def workflow_input_file_path_list(self):
        return self.__wf_input_file_path_list

    def __get_metadata(self, wf_input_path: str) -> Dict[str, str]:
        """
        Get the names of subject, session, between-factor, and within-factor associated with the workflow input file.

        [Return]
        metadata: Dict
          'subject': Subject name.
          'session': Session name.
          'factors': Dict
            '<between-factor name>': Dict
              'file_path_list': The paths of the workflow input files belonging to the between-factor.
              'within_factor': Dict
                '<within-factor name>': Dict
                  file_path_list': The paths of the workflow input files belonging to
                  the between-factor and within-factor.
        """

        metadata = {}

        # Get the names of subject and session from the file name.
        file_name = os.path.basename(wf_input_path)
        tokens = file_name.split('_')
        metadata['subject'] = tokens[0].split('-')[1]
        metadata['session'] = tokens[1].split('-')[1]

        # Set the path of filemap.json as <project_root_dir>/filemap.json.
        # project_root_dir = get_project_root_dir(project_id)
        # filemap_path = os.path.join(project_root_dir, 'filemap.json')
        # Dummy
        dir_path = os.path.dirname(__file__)
        filemap_path = os.path.join(dir_path, r'../../../sample_data/cjs/1/filemap.json')

        # Get the between-factor and within-factor from the filemap.json.
        factors_dict = {}
        with open(filemap_path) as file:
            factors_info = json.load(file)

            # Get the between-factor.
            for between_factor in factors_info:
                file_path_list = []
                if 'images' in between_factor.keys():
                    file_path_list = [file['path'] for file in between_factor['images']]
                factors_dict[between_factor['folder_name']] = {'file_path_list': file_path_list, 'within_factor': {}}

                # Get the within-factor in this between-factor if they are specified.
                if 'sub_folders' in between_factor.keys():
                    for within_factor in between_factor['sub_folders']:
                        file_path_list = [file['path'] for file in within_factor['images']]
                        factors_dict[between_factor['folder_name']]['within_factor'][within_factor['folder_name']] = \
                            {'file_path': file_path_list}
        metadata['factors'] = factors_dict

        return metadata

    def get_subject_list(self) -> List[str]:
        subject_list = []
        for wf_input_path in self.__wf_input_file_path_list:
            metadata  = self.__get_metadata(wf_input_path)
            if metadata['subject'] not in subject_list:
                subject_list.append(metadata['subject'])
        return subject_list

    def get_subject(self, wf_input_path: str) -> str:
        metadata  = self.__get_metadata(wf_input_path)
        return metadata['subject']

    def get_factors(self) -> Dict[str, List[str]]:
        """
        Get all the within-factor and between-factor combinations in form of
        dict[<between-factor>, list[<within-factor>].
        """

        factors_dict = {}
        for wf_input_path in self.__wf_input_file_path_list:
            metadata = self.__get_metadata(wf_input_path)
            for between_factor in metadata['factors'].keys():
                factors_dict[between_factor] = []
                for within_factor in metadata['factors'][between_factor]['within_factor'].keys():
                    factors_dict[between_factor].append(within_factor)
        return factors_dict

    def get_output_file_paths(self, wf_input_path: str) -> List[str]:
        """
        Get the paths of the output files for a single workflow input file path.

        [Return]
        file_path_list: List[<output file path>]
        """

        return self.__unit_analysis_info_dict[wf_input_path].output_file_path_list

    def search_output_file_paths(self, wf_input_path_list: List[str] = None, subject_list: List[str] = None,
                                 regex_pattern: str = '') -> Dict[str, List[str]]:
        """
        Get the paths of the output files that were saved in the previous node.
        You can extract the paths by specifying the workflow input file paths and subjects
        as well as by means of a regular expression.

        [Return]
        file_path_dict: dict[<workflow input file path>, list[<output file path>]]
        """

        file_path_dict = {}
        for wf_input_path in wf_input_path_list:
            if not wf_input_path_list or (wf_input_path_list and wf_input_path in self.__wf_input_file_path_list):
                metadata = self.__get_metadata(wf_input_path)
                if not subject_list or (subject_list and metadata['subject'] in subject_list):
                    file_path_dict[wf_input_path] = []
                    if regex_pattern:
                        for output_file_path in self.__unit_analysis_info_dict[wf_input_path].output_file_path_list:
                            result = re.search(regex_pattern, output_file_path)
                            if result:
                                file_path_dict[wf_input_path].append(output_file_path)
                    else:
                        file_path_dict[wf_input_path] = self.__unit_analysis_info_dict[wf_input_path].output_file_path_list

        return file_path_dict

    def get_unit_analysis_status(self, wf_input_path: str) -> str:
        # Get a status message of the analysis for a single workflow input file path.
        analysis_status = self.__unit_analysis_info_dict[wf_input_path].analysis_status
        if analysis_status == AnalysisStatus.WAIT:
            return 'waiting'
        elif analysis_status == AnalysisStatus.PROCESSING:
            return 'processing'
        elif analysis_status == AnalysisStatus.PROCESSED:
            return 'success'
        elif analysis_status == AnalysisStatus.ERROR:
            return 'failure'
        else:
            return 'unknown'

    def get_node_analysis_status(self) -> str:
        # Get a status message of the whole node analysis.
        message_dict = {}
        for wf_input_path in self.__wf_input_file_path_list:
            message = self.get_unit_analysis_status(wf_input_path)
            if message not in message_dict.keys():
                message_dict[message] = 1
            else:
                message_dict[message] += 1

        status_message = ''
        for key, val in message_dict.items():
            status_message += f'{key}: {str(val)} '

        return status_message

    def get_message(self, wf_input_path: str) -> str:
        # Get the message such as an error message.
        return self.__unit_analysis_info_dict[wf_input_path].message

    def set_output_file_paths(self, wf_input_file_path: str, output_file_path_list: List[str]):
        """
        [arguments]
        output_file_path_list: A list of workflow input file paths or a str of a workflow input file path.
        """

        # Convert to the list if the output_file_path_list argument is a str.
        if isinstance(output_file_path_list, str):
            output_file_path_list = [output_file_path_list]

        self.__unit_analysis_info_dict[wf_input_file_path].output_file_path_list = check_path_format(output_file_path_list)

    def set_analysis_status(self, wf_input_path: str, analysis_status: AnalysisStatus):
        self.__unit_analysis_info_dict[wf_input_path].analysis_status = analysis_status

    def set_message(self, wf_input_path: str, message: str):
        self.__unit_analysis_info_dict[wf_input_path].message = message


class UnitAnalysisInfo():
    """
    Store the analysis info in a node for a single workflow input file.
    """

    def __init__(self, wf_input_file_path: str):

        # The path of the workflow input file.
        self.__wf_input_file_path: str = wf_input_file_path

        # The paths of the output files that save the results of the analysis associated
        # with the workflow input file in the node.
        self.__output_file_path_list: List[str] = []

        # An analysis status for the workflow input file in the node.
        self.__analysis_status: AnalysisStatus = AnalysisStatus.WAIT

        # Some message such as an error message.
        self.__message = ''

    @property
    def input_file_path(self):
        return self.__wf_input_file_path

    @property
    def output_file_path_list(self):
        return self.__output_file_path_list

    @output_file_path_list.setter
    def output_file_path_list(self, val: str):
        self.__output_file_path_list = val

    @property
    def analysis_status(self):
        return self.__analysis_status

    @analysis_status.setter
    def analysis_status(self, val: AnalysisStatus):
        self.__analysis_status = val

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, val: str):
        self.__message = val
