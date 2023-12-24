import os
import traceback
import gc
import copy
from dataclasses import asdict
from datetime import datetime

from optinist.api.config.config_reader import ConfigReader
from optinist.api.config.config_writer import ConfigWriter
from optinist.api.dir_path import DIRPATH
from optinist.api.experiment.experiment_reader import ExptConfigReader
from optinist.wrappers import wrapper_dict
from optinist.api.snakemake.smk import Rule
from optinist.api.pickle.pickle_reader import PickleReader
from optinist.api.pickle.pickle_writer import PickleWriter
from optinist.api.utils.filepath_creater import join_filepath
from optinist.api.nwb.nwb_creater import merge_nwbfile, save_nwb
from optinist.api.dataclass.dataclass import AnalysisInfo
from optinist.api.experiment.experiment import ExptFunction
from optinist.api.workflow.workflow import OutputPath, SubjectAnalysisInfo


class Runner:
    @classmethod
    def run(cls, __rule: Rule, last_output):
        try:
            input_info = cls.read_input_info(__rule.input)

            cls.change_dict_key_exist(input_info, __rule)

            nwbfile = input_info['nwbfile']

            # input_info
            for key in list(input_info):
                if key not in __rule.return_arg.values():
                    input_info.pop(key)

            cls.set_func_start_timestamp(os.path.dirname(__rule.output))

            # Get the project ID, analysis ID, and node ID from the pickle file path adding them to the params.
            tokens = __rule.output.split('/')
            __rule.params['project_id'] = int(tokens[-4])
            __rule.params['analysis_id'] = tokens[-3]
            __rule.params['node_id'] = tokens[-2]

            # output_info
            output_info = cls.execute_function(
                __rule.path,
                __rule.params,
                input_info
            )

            # Update experiment.yaml and workflow_info.yaml based on the output AnalysisInfo object.
            if 'analysis_info_out' in output_info.keys():
                cls.update_experiment_file(os.path.dirname(__rule.output), output_info['analysis_info_out'])
                cls.update_workflow_info_file(os.path.dirname(__rule.output), output_info['analysis_info_out'])

            # nwbfileの設定
            output_info['nwbfile'] = cls.save_func_nwb(
                f"{__rule.output.split('.')[0]}.nwb",
                __rule.type,
                nwbfile,
                output_info,
            )

            # 各関数での結果を保存
            PickleWriter.write(__rule.output, output_info)

            # NWB全体保存
            if __rule.output in last_output:
                # 全体の結果を保存する
                path = join_filepath(os.path.dirname(os.path.dirname(__rule.output)))
                path = join_filepath([path, f"whole_{__rule.type}.nwb"])
                cls.save_all_nwb(path, output_info['nwbfile'])

            del input_info, output_info
            gc.collect()

        except Exception as e:
            print(e)
            PickleWriter.write(
                __rule.output,
                list(traceback.TracebackException.from_exception(e).format())[-2:],
            )

    @classmethod
    def update_experiment_file(cls, node_output_dir_path: str, analysis_info: AnalysisInfo):
        """ Update the node analysis info in experiment.yaml based on an AnalysisInfo object. """

        # Get the ExptConfig data from experiment.yaml.
        workflow_output_path = os.path.dirname(node_output_dir_path)
        node_id = os.path.basename(node_output_dir_path)
        expt_file_path = join_filepath([workflow_output_path, DIRPATH.EXPERIMENT_YML])
        expt_config = ExptConfigReader.read(expt_file_path)

        # Set the info about the output files and subjects from the AnalysisInfo object.
        output_path_dict = {}
        subject_dict = {}
        for wf_input_path in analysis_info.workflow_input_file_path_list:
            # Set output file paths to OutputPath.
            output_file_paths = analysis_info.get_output_file_paths(wf_input_path)
            for output_file_path in output_file_paths:
                file_name = os.path.splitext(os.path.basename(output_file_path))[0]
                output_path_dict[file_name] = OutputPath(
                    path=output_file_path,
                    type='images',
                    max_index=1
                )

            # Set subjects info to SubjectAnalysisInfo.
            # Each subject field takes a list form in case of multiple workflow input files for a single subject.
            subject = analysis_info.get_property(wf_input_path, 'subject_name')
            if subject in subject_dict.keys():
                subject_dict[subject].success.append(analysis_info.get_analysis_status_message(wf_input_path))
                subject_dict[subject].output_path.append(output_file_paths)
                subject_dict[subject].message.append(analysis_info.get_message(wf_input_path))
            else:
                subject_dict[subject] = SubjectAnalysisInfo(
                    success=[analysis_info.get_analysis_status_message(wf_input_path)],
                    output_path=[output_file_paths],
                    message=[analysis_info.get_message(wf_input_path)]
                )

        # Update the ExptFunction data of a given node in the ExptConfig data.
        expt_config.function[node_id] = ExptFunction(
            unique_id=expt_config.function[node_id].unique_id,
            name=expt_config.function[node_id].name,
            success=expt_config.success,
            hasNWB=expt_config.function[node_id].hasNWB,
            message=analysis_info.get_analysis_status_message(),
            outputPaths=output_path_dict,
            started_at=expt_config.started_at,
            finished_at=expt_config.finished_at,
            subjects=subject_dict
        )

        # Overwrite experiment.yaml with the new ExptConfig data.
        ConfigWriter.write(
            dirname=workflow_output_path,
            filename=DIRPATH.EXPERIMENT_YML,
            config=asdict(expt_config)
        )

    @classmethod
    def update_workflow_info_file(cls, node_output_dir_path: str, analysis_info: AnalysisInfo):
        """ Update the node analysis info in workflow_info.yaml based on an AnalysisInfo object.
        The info saved in workflow_info.yaml will be referred in the same node analysis next time.
        """

        WORKFLOW_INFO_FILE_NAME = 'workflow_info.yaml'

        # Get the workflow info from workflow_info.yaml.
        workflow_output_path = os.path.dirname(node_output_dir_path)
        node_id = os.path.basename(node_output_dir_path)
        file_path = join_filepath([workflow_output_path, WORKFLOW_INFO_FILE_NAME])
        workflow_info = ConfigReader.read(file_path) if os.path.isfile(file_path) else {}

        # Set the new node analysis info extracted from the AnalysisInfo object.
        if 'node_analysis' not in workflow_info.keys():
            workflow_info['node_analysis'] = {}
        node_info = {}
        for wf_input_path in analysis_info.workflow_input_file_path_list:
            node_info[wf_input_path] = {
                'output_file_paths': analysis_info.get_output_file_paths(wf_input_path),
                'success': analysis_info.get_analysis_status_message(wf_input_path),
                'message': analysis_info.get_message(wf_input_path)
            }
        workflow_info['node_analysis'][node_id] = node_info

        # Save the workflow info in workflow_info.yaml.
        ConfigWriter.write(
            dirname=workflow_output_path,
            filename=WORKFLOW_INFO_FILE_NAME,
            config=workflow_info
        )

    @classmethod
    def set_func_start_timestamp(cls, output_dirpath):
        workflow_dirpath = os.path.dirname(output_dirpath)
        node_id = os.path.basename(output_dirpath)
        expt_config = ExptConfigReader.read(
            join_filepath([workflow_dirpath, DIRPATH.EXPERIMENT_YML])
        )
        expt_config.function[node_id].started_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        ConfigWriter.write(
            dirname=workflow_dirpath,
            filename=DIRPATH.EXPERIMENT_YML,
            config=asdict(expt_config),
        )

    @classmethod
    def save_func_nwb(cls, save_path, name, nwbfile, output_info):
        if "nwbfile" in output_info:
            nwbfile[name] = output_info["nwbfile"]
            save_nwb(
                save_path,
                nwbfile["input"],
                output_info["nwbfile"],
            )
        return nwbfile

    @classmethod
    def save_all_nwb(cls, save_path, all_nwbfile):
        input_nwbfile = all_nwbfile["input"]
        all_nwbfile.pop("input")
        nwbfile = {}
        for x in all_nwbfile.values():
            nwbfile = merge_nwbfile(nwbfile, x)
        save_nwb(save_path, input_nwbfile, nwbfile)

    @classmethod
    def execute_function(cls, path, params, input_info):
        wrapper = cls.dict2leaf(wrapper_dict, path.split('/'))
        func = copy.deepcopy(wrapper["function"])
        output_info = func(params=params, **input_info)
        del func
        gc.collect()

        return output_info

    @classmethod
    def change_dict_key_exist(cls, input_info, rule_config: Rule):
        for return_name, arg_name in rule_config.return_arg.items():
            if return_name in input_info:
                input_info[arg_name] = input_info.pop(return_name)

    @classmethod
    def read_input_info(cls, input_files):
        input_info = {}
        for filepath in input_files:
            load_data = PickleReader.read(filepath)
            input_info = dict(list(load_data.items()) + list(input_info.items()))
        return input_info

    @classmethod
    def dict2leaf(cls, root_dict: dict, path_list):
        path = path_list.pop(0)
        if len(path_list) > 0:
            return cls.dict2leaf(root_dict[path], path_list)
        else:
            return root_dict[path]