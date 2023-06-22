import os
from dataclasses import asdict
from datetime import datetime
from glob import glob

from optinist.api.pickle.pickle_reader import PickleReader
from optinist.api.dataclass.dataclass import *
from optinist.api.workflow.workflow import Message, OutputPath, OutputType, ExptInfo, SubjectInfo, NodeInfo
from optinist.api.config.config_writer import ConfigWriter
from optinist.api.experiment.experiment_reader import ExptConfigReader
from optinist.api.utils.filepath_creater import join_filepath
from optinist.api.dir_path import DIRPATH
from optinist.routers.fileIO.file_reader import Reader


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

    def get_experiment_info(self):
        """
        Get the experiment info about the workflow analysis.
        """

        GET_NIFTI_IMAGE_API = '/outputs/nifti_image/'

        # TODO: Set the experiment.yaml path.
        expt_file_path = os.path.join(DIRPATH.OUTPUT_DIR, str(self.project_id), self.unique_id, DIRPATH.EXPERIMENT_YML)
        # Dummy
        expt_file_path = os.path.join(DIRPATH.ROOT_DIR, r'../sample_data/cjs/output/1/3a55fa37/experiment2.yaml')

        # Get the experiment config data (ExptConfig) and the function data ({<node_id>, ExptFunction}).
        expt_config = ExptConfigReader.read(expt_file_path)
        function_data = expt_config.function

        results_data = []   # List[SubjectInfo] appended to ExptInfo.results.
        for node_id in function_data.keys():
            # Get the subjects data ({<subject_name>, {<success>, <output_path>, <message>}}).
            subjects_data = function_data[node_id].subjects
            if subjects_data is None:
                continue
            for subject_name in subjects_data.keys():
                # Summarize the analysis info for the node.
                node_analysis_info = NodeInfo(
                    unique_id=node_id,
                    name=function_data[node_id].name,
                    success=', '.join(subjects_data[subject_name].success), # 2D -> 1D
                    message=function_data[node_id].message,
                    outputs=[os.path.join(GET_NIFTI_IMAGE_API, x) for row in subjects_data[subject_name].output_path for x in row] # 2D -> 1D
                )

                # Add to the corresponding subject data in results_data.
                for subject_data in results_data:
                    if subject_name == subject_data.name:
                        subject_data.function[node_id] = node_analysis_info
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

        return  ExptInfo(
            started_at=expt_config.started_at,
            finished_at=expt_config.finished_at,
            unique_id=expt_config.unique_id,
            name=expt_config.name,
            status=expt_config.success,
            results=results_data
        )


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
