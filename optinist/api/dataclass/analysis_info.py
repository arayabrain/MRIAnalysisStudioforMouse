from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from optinist.api.dataclass.base import BaseData
from optinist.api.utils.check_path_format import check_path_format


class NodeAnalysisType(Enum):
    """ Represent a node analysis type. """

    UNDEFINED = 'undefined'
    ALIGNMENT = 'alignment'
    SEGMENT1 = 'segment1'
    MASKING = 'masking'
    SEGMENT2 = 'segment2'
    DARTEL = 'dartel'
    NORMALIZATION = 'normalization'
    SMOOTHING = 'smoothing'
    TOTAL_BRAIN_VOLUME = 'total_brain_volume'
    STATS_MODELING = 'stats_modeling'
    STATS_ANALYSIS = 'stats_analysis'
    STATS_VISUALIZATION = 'stats_visualization'


class AnalysisStatus(Enum):
    """ Represent an analysis status for a workflow input file. """

    UNKNOWN = 'unknown'
    WAIT = 'waiting'
    PROCESSING = 'processing'
    PROCESSED = 'success'
    ERROR = 'failure'
    PREVIOUS_ERROR = 'failure'
    SKIPPED = 'skipped'


class AnalysisInfo(BaseData):
    """ Store the analysis info for a single node.
    The object will be used to update experiment.yaml and transmit the info to the next node.
    """

    def __init__(self, wf_input_file_path_list: List[str], group_info: Dict[str, List[str]] = None,
                 node_analysis_type: NodeAnalysisType = NodeAnalysisType.UNDEFINED, file_name='analysis_info'):
        super().__init__(file_name)
        """
        Parameters
            ----------
            wf_input_file_path_list : list[str]
                The full path of the workflow input files.
                The path format must follow the POSIX type.
            group_info : dict[<workflow input file path>, list[str]]
                The groups to which each workflow input file belongs.
                A group can have a hierarchical structure such as ['group A', 'subgroup B'].
        """

        # Workflow input file paths.
        self.__wf_input_file_path_list: List[str] = check_path_format(wf_input_file_path_list)

        # Clean up the workflow input file path of group_info.
        cleaned_group_info = {}
        for wf_input_path in group_info.keys():
            cleaned_wf_input_path = check_path_format(wf_input_path)
            if cleaned_wf_input_path in self.__wf_input_file_path_list:
                cleaned_group_info[cleaned_wf_input_path] = group_info[wf_input_path]

        # UnitAnalysisInfo stores the node analysis info of a single workflow input file.
        self.__unit_analysis_info_dict: Dict[str, UnitAnalysisInfo] = {}
        for wf_input_path in self.__wf_input_file_path_list:
            group = cleaned_group_info[wf_input_path] if wf_input_path in cleaned_group_info.keys() else None
            self.__unit_analysis_info_dict[wf_input_path] = UnitAnalysisInfo(wf_input_path, group)

        self.__node_analysis_type = node_analysis_type

    @property
    def workflow_input_file_path_list(self):
        return self.__wf_input_file_path_list

    @property
    def node_analysis_type(self):
        return self.__node_analysis_type

    def create_new_analysis_info(self, node_analysis_type: NodeAnalysisType = NodeAnalysisType.UNDEFINED):
        """ Create a new AnalysisInfo object with the same workflow input files, groups, and properties. """

        group_info = {}
        for wf_input_path in self.__wf_input_file_path_list:
            group_info[wf_input_path] = self.__unit_analysis_info_dict[wf_input_path].group
        analysis_info = AnalysisInfo(self.__wf_input_file_path_list, group_info, node_analysis_type)

        # Copy the properties.
        for wf_input_path in self.__wf_input_file_path_list:
            for key, value in self.__unit_analysis_info_dict[wf_input_path].properties.items():
                analysis_info.set_property(wf_input_path, key, value)

        return analysis_info

    def get_grouped_workflow_input_file_paths(self) -> Dict[Tuple, List[str]]:
        """ Return the path lists of the workflow input files categorized by groups.

        Returns
        ----------
            wf_input_path_list_out : dict[tuple, list[str]]
                A dict key tuple represents a group with a hierarchical structure such as ('group A', 'subgroup B').
        """

        wf_input_path_list_out = {}
        for wf_input_path in self.__wf_input_file_path_list:
            # Convert to tuple because list cannot be used as a key of a dict.
            group_tuple = tuple(self.__unit_analysis_info_dict[wf_input_path].group)

            if group_tuple not in wf_input_path_list_out.keys():
                wf_input_path_list_out[group_tuple] = [wf_input_path]
            else:
                wf_input_path_list_out[group_tuple].append(wf_input_path)

        return wf_input_path_list_out

    def get_analysis_start_time(self, wf_input_path):
        wf_input_path = check_path_format(wf_input_path)
        return self.__unit_analysis_info_dict[wf_input_path].analysis_start_time

    def get_analysis_end_time(self, wf_input_path):
        wf_input_path = check_path_format(wf_input_path)
        return self.__unit_analysis_info_dict[wf_input_path].analysis_end_time

    def get_output_file_paths(self, wf_input_path: str) -> List[str]:
        wf_input_path = check_path_format(wf_input_path)
        return self.__unit_analysis_info_dict[wf_input_path].output_file_path_list

    def get_analysis_status(self, wf_input_path: Optional[str] = None) -> AnalysisStatus:
        """ Get an analysis status for the specified workflow input file or the node. """

        # Return an error status if all the processing showed errors in the node analysis.
        if wf_input_path is None:
            for wf_input_path in self.__wf_input_file_path_list:
                if self.__unit_analysis_info_dict[wf_input_path].analysis_status != AnalysisStatus.ERROR:
                    return AnalysisStatus.PROCESSED
            return AnalysisStatus.ERROR
        # For an individual analysis.
        else:
            wf_input_path = check_path_format(wf_input_path)
            return self.__unit_analysis_info_dict[wf_input_path].analysis_status

    def get_analysis_status_message(self, wf_input_path: Optional[str] = None) -> str:
        """ Get an analysis status message of the specified workflow input file or the node. """

        # Return an error message ('error') if all the processing showed errors in the node analysis,
        # otherwise return 'success'.
        if wf_input_path is None:
            analysis_status = self.get_analysis_status()
            return 'error' if analysis_status == AnalysisStatus.ERROR else 'success'
        # Return a message of the specified workflow input file.
        else:
            analysis_status = self.get_analysis_status(wf_input_path)
            return analysis_status.value

    def get_property(self, wf_input_path: str, key: str):
        wf_input_path = check_path_format(wf_input_path)
        return self.__unit_analysis_info_dict[wf_input_path].properties[key]

    def get_message(self, wf_input_path: str) -> str:
        """ Get some message such as an error message. """
        wf_input_path = check_path_format(wf_input_path)
        return self.__unit_analysis_info_dict[wf_input_path].message

    def set_analysis_start_time(self, wf_input_path):
        wf_input_path = check_path_format(wf_input_path)
        self.__unit_analysis_info_dict[wf_input_path].set_analysis_start_time()

    def set_analysis_end_time(self, wf_input_path):
        wf_input_path = check_path_format(wf_input_path)
        self.__unit_analysis_info_dict[wf_input_path].set_analysis_end_time()

    def set_output_file_paths(self, wf_input_path: str, output_file_path_list: Union[List[str], str]):
        """
        Parameters
            ----------
            output_file_path_list : list[str] or str
                A list of output file paths or a str of an output file path.
        """

        # If output_file_path_list is str, convert it to list.
        if isinstance(output_file_path_list, str):
            output_file_path_list = [output_file_path_list]

        wf_input_path = check_path_format(wf_input_path)
        self.__unit_analysis_info_dict[wf_input_path].output_file_path_list = check_path_format(output_file_path_list)

    def set_analysis_status(self, wf_input_path: str, analysis_status: AnalysisStatus):
        wf_input_path = check_path_format(wf_input_path)
        self.__unit_analysis_info_dict[wf_input_path].analysis_status = analysis_status

    def set_property(self, wf_input_path: str, key: str, value):
        wf_input_path = check_path_format(wf_input_path)
        self.__unit_analysis_info_dict[wf_input_path].properties[key] = value

    def set_message(self, wf_input_path: str, message: str):
        wf_input_path = check_path_format(wf_input_path)
        self.__unit_analysis_info_dict[wf_input_path].message = message


class UnitAnalysisInfo:
    """ Store the node analysis info of a single workflow input file. """

    def __init__(self, wf_input_file_path: str, group: List[str] = None):

        # Workflow input file path.
        self.__wf_input_file_path: str = wf_input_file_path

        # The group to which the workflow input file belongs.
        # A group can have a hierarchical structure in a list, such as ['group A', 'subgroup B'].
        self.__group: List[str] = group

        self.__analysis_start_time: Optional[str] = None
        self.__analysis_end_time: Optional[str] = None
        self.__DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

        # The paths of the output files generated in the node analysis.
        self.output_file_path_list: List[str] = []

        self.analysis_status: AnalysisStatus = AnalysisStatus.WAIT

        # Any of properties associated with the input data.
        self.properties: Dict = {}

        # Some message such as an error message.
        self.message = ''

    @property
    def wf_input_file_path(self):
        return self.__wf_input_file_path

    @property
    def group(self):
        return self.__group

    @property
    def analysis_start_time(self):
        return self.__analysis_start_time

    @property
    def analysis_end_time(self):
        return self.__analysis_end_time

    def set_analysis_start_time(self):
        self.__analysis_start_time = datetime.now().strftime(self.__DATETIME_FORMAT)

    def set_analysis_end_time(self):
        self.__analysis_end_time = datetime.now().strftime(self.__DATETIME_FORMAT)
