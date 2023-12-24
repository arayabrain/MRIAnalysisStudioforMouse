import os
from dataclasses import asdict
from glob import glob

from optinist.api.pickle.pickle_reader import PickleReader
from optinist.api.dataclass.dataclass import *
from optinist.api.workflow.workflow import Message, OutputPath, OutputType, ExptInfo, SubjectInfo, NodeInfo, SubjectAnalysisInfo
from optinist.api.config.config_writer import ConfigWriter
from optinist.api.experiment.experiment_reader import ExptConfigReader
from optinist.api.experiment.experiment import ExptConfig
from optinist.api.utils.filepath_creater import join_filepath
from optinist.api.dir_path import DIRPATH
from optinist.routers.fileIO.file_reader import Reader
import optinist.routers.workdbmanager as db
import optinist.wrappers.vbm_wrapper.vbm.utils as utils


class WorkflowResult:

    def __init__(self, project_id, unique_id):
        self.project_id = project_id
        self.unique_id = unique_id
        self.workflow_dirpath = join_filepath([
            DIRPATH.OUTPUT_DIR,
            self.project_id,
            self.unique_id,
        ])
        self.expt_filepath = join_filepath([
            self.workflow_dirpath,
            DIRPATH.EXPERIMENT_YML
        ])
        self.error_filepath = join_filepath([
            self.workflow_dirpath,
            "error.log"
        ])

    def get(self, nodeIdList):
        results: Dict[str, Message] = {}
        for node_id in nodeIdList:
            if os.path.exists(self.error_filepath):
                error_message = Reader.read(self.error_filepath)
                if error_message != "":
                    results[node_id] = Message(
                        status="error",
                        message=error_message,
                    )

            glob_pickle_filepath = join_filepath([
                self.workflow_dirpath,
                node_id,
                "*.pkl"
            ])
            for pickle_filepath in glob(glob_pickle_filepath):
                results[node_id] = NodeResult(
                    self.workflow_dirpath,
                    node_id,
                    pickle_filepath,
                ).get()
                self.has_nwb(node_id)

        self.has_nwb()

        return results

    def has_nwb(self, node_id=None):

        if node_id is None:
            nwb_filepath_list = glob(join_filepath([
                self.workflow_dirpath,
                "*.nwb"
            ]))
        else:
            nwb_filepath_list = glob(join_filepath([
                self.workflow_dirpath,
                node_id,
                "*.nwb"
            ]))

        for nwb_filepath in nwb_filepath_list:
            if os.path.exists(nwb_filepath):
                config = ExptConfigReader.read(self.expt_filepath)

                if node_id is None:
                    config.hasNWB = True
                else:
                    config.function[node_id].hasNWB = True

                ConfigWriter.write(
                    dirname=self.workflow_dirpath,
                    filename=DIRPATH.EXPERIMENT_YML,
                    config=asdict(config),
                )

    def get_experiment_info(self, expt_config: ExptConfig) -> ExptInfo:
        """ Extract the experiment info from the ExptConfig data, and store them in ExptInfo. """

        # URL of get_nifti_image() API, which is attached to the head of an output file path.
        GET_NIFTI_IMAGE_API_URL = '/outputs/nifti_image'

        # Get the ExptFunction dict (Dict[<node_id>, ExptFunction]) from the ExptConfig data.
        expt_function_dict = expt_config.function

        results_data = []   # A list of SubjectInfo data, which will be pushed to ExptInfo.results.
        for node_id, subject_info in expt_function_dict.items():
            # Get the SubjectAnalysisInfo dict (Dict[<subject_name>, SubjectAnalysisInfo]) of the node, and.
            # add the SubjectAnalysisInfo data if workflow input files were added in the project after the analysis.
            subject_analysis_info_dict = self._add_new_subject_analysis_info(int(expt_config.project_id),
                                                                             expt_config.unique_id,
                                                                             subject_info.subjects)
            if subject_analysis_info_dict is None:
                continue
            for subject_name, subject_analysis_info in subject_analysis_info_dict.items():
                # Summarize the node analysis info of the subject in NodeInfo.
                output_file_paths = subject_analysis_info.output_path
                node_analysis_info = NodeInfo(
                    unique_id=node_id,
                    name=subject_info.name,
                    # 'success' field must take a single value of the whole node analysis status, 'success' or 'error',
                    # otherwise causes an error in RESULT.
                    # Take 'success' if all the individual analyses have been successful in the node analysis,
                    # otherwise take 'error'.
                    success='success' if all(i == 'success' for i in subject_analysis_info.success) else 'error',
                    message=subject_info.message,
                    # 2D list -> 1D list. Also, append the API URL at the head of the path.
                    outputs=[GET_NIFTI_IMAGE_API_URL + path for row in output_file_paths for path in row]
                )

                # Add the NodeInfo data to the SubjectInfo data of results_data.
                for subject_info_data in results_data:
                    if subject_name == subject_info_data.name:
                        subject_info_data.function[node_id] = node_analysis_info
                        break
                else:
                    results_data.append(
                        SubjectInfo(
                            subject_id=subject_name,
                            name=subject_name,
                            function={node_id: node_analysis_info},
                            nodeDict={},
                            edgeDict={}
                        ))

        return ExptInfo(
            started_at=expt_config.started_at,
            finished_at=expt_config.finished_at,
            unique_id=expt_config.unique_id,
            name=expt_config.name,
            status=expt_config.success,
            results=results_data
        )

    def _add_new_subject_analysis_info(self, project_id: int, analysis_id: str, subject_analysis_info_dict):
        """ Add the SubjectAnalysisInfo data if workflow input files were added in the project after the analysis. """

        # TODO: Implement in the DB program.
        return subject_analysis_info_dict

        # Find newly added IDs.
        db_file_id_list = db.get_file_id_list(project_id)
        wf_file_id_list = utils.get_wf_input_file_id_list(project_id, analysis_id)
        new_ids = list(set(db_file_id_list) - set(wf_file_id_list))

        # Add the SubjectAnalysisInfo data (success='waiting', output_path=[]. message='') for the newly added IDs.
        for id in new_ids:
            wf_input_file_path = utils.get_image_file_path(project_id, id)
            subject_name = utils.get_subject_name(wf_input_file_path)
            if subject_name in subject_analysis_info_dict.keys():
                subject_analysis_info_dict[subject_name].success.append('waiting')
                subject_analysis_info_dict[subject_name].output_path.append([])
                subject_analysis_info_dict[subject_name].message.append('')
            else:
                subject_analysis_info_dict[subject_name] = SubjectAnalysisInfo(success=['waiting'],
                                                                               output_path=[],
                                                                               message=[''])

        return subject_analysis_info_dict


class NodeResult:

    def __init__(self, workflow_dirpath, node_id, pickle_filepath):
        self.workflow_dirpath = workflow_dirpath
        self.node_id = node_id
        self.node_dirpath = join_filepath([
            self.workflow_dirpath,
            self.node_id
        ])
        self.expt_filepath = join_filepath([
            self.workflow_dirpath,
            DIRPATH.EXPERIMENT_YML
        ])

        pickle_filepath = pickle_filepath.replace("\\", "/")
        self.algo_name = os.path.splitext(os.path.basename(pickle_filepath))[0]
        self.info = PickleReader.read(pickle_filepath)

    def get(self):
        expt_config = ExptConfigReader.read(self.expt_filepath)
        if isinstance(self.info, (list, str)):
            expt_config.function[self.node_id].success = "error"
            message = self.error()
        else:
            expt_config.function[self.node_id].success = "success"
            message = self.success()
            expt_config.function[self.node_id].outputPaths = message.outputPaths
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expt_config.function[self.node_id].finished_at = now
        expt_config.function[self.node_id].message = message.message

        statuses = list(map(lambda x: x.success, expt_config.function.values()))
        if "running" not in statuses:
            expt_config.finished_at = now
            if "error" in statuses:
                expt_config.success = "error"
            else:
                expt_config.success = "success"

        ConfigWriter.write(
            dirname=self.workflow_dirpath,
            filename=DIRPATH.EXPERIMENT_YML,
            config=asdict(expt_config),
        )

        return message

    def success(self):
        return Message(
            status="success",
            message=f"{self.algo_name} success",
            outputPaths=self.outputPaths()
        )

    def error(self):
        return Message(
            status="error",
            message=self.info if isinstance(self.info, str) else "\n".join(self.info),
        )

    def outputPaths(self):
        outputPaths: Dict[str, OutputPath] = {}
        for k, v in self.info.items():  # k: output object name, v: output object
            if isinstance(v, BaseData):
                v.save_json(self.node_dirpath)

            if isinstance(v, ImageData):
                outputPaths[k] = OutputPath(
                    path=v.json_path,
                    type=OutputType.IMAGE,
                    max_index=len(v.data) if v.data.ndim == 3 else 1
                )
            elif isinstance(v, TimeSeriesData):
                outputPaths[k] = OutputPath(
                    path=v.json_path,
                    type=OutputType.TIMESERIES,
                    max_index=len(v.data)
                )
            elif isinstance(v, HeatMapData):
                outputPaths[k] = OutputPath(
                    path=v.json_path,
                    type=OutputType.HEATMAP,
                )
            elif isinstance(v, RoiData):
                outputPaths[k] = OutputPath(
                    path=v.json_path,
                    type=OutputType.ROI,
                )
            elif isinstance(v, ScatterData):
                outputPaths[k] = [OutputPath(
                    path=v.json_path,
                    type=OutputType.SCATTER
                )]
            elif isinstance(v, BarData):
                outputPaths[k] = OutputPath(
                    path=v.json_path,
                    type=OutputType.BAR,
                )
            elif isinstance(v, HTMLData):
                outputPaths[k] = OutputPath(
                    path=v.json_path,
                    type=OutputType.HTML,
                )
            else:
                pass

        return outputPaths
