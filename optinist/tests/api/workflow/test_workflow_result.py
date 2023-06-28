import os
import shutil

from optinist.api.dir_path import DIRPATH
from optinist.api.workflow.workflow import Message
from optinist.api.workflow.workflow_result import NodeResult, WorkflowResult

project_id = "test_project"
unique_id = "result_test"
node_id_list = ["func1", "func2"]

workflow_dirpath = f"{DIRPATH.OUTPUT_DIR}/{project_id}/{unique_id}"
pickle_path = f"{DIRPATH.OUTPUT_DIR}/{project_id}/{unique_id}/func1/func1.pkl"

shutil.copytree(
    f"{DIRPATH.OPTINIST_DIR}/output_test/{project_id}/{unique_id}",
    workflow_dirpath,
    dirs_exist_ok=True,
)


def test_WorkflowResult_get():
    output = WorkflowResult(project_id=project_id, unique_id=unique_id).get(
        node_id_list
    )
    assert isinstance(output, dict)
    assert len(output) == 1


def test_NodeResult_get():
    assert os.path.exists(pickle_path)
    output = NodeResult(
        workflow_dirpath=workflow_dirpath,
        node_id="func1",
        pickle_filepath=pickle_path,
    ).get()

    assert isinstance(output, Message)
