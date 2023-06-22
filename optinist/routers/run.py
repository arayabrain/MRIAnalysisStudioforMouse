from typing import Dict
from fastapi import APIRouter, BackgroundTasks
import uuid

from optinist.api.workflow.workflow import NodeItem, RunItem, Message, ExptInfo
from optinist.api.workflow.workflow_runner import WorkflowRunner
from optinist.api.workflow.workflow_result import WorkflowResult

router = APIRouter()


@router.post("/run/{project_id}", response_model=str, tags=['run'])
async def run(project_id: str, runItem: RunItem, background_tasks: BackgroundTasks):
    unique_id = str(uuid.uuid4())[:8]
    WorkflowRunner(project_id, unique_id, runItem).run_workflow(background_tasks)
    print("run snakemake")
    return unique_id


@router.post("/run/{project_id}/{uid}", response_model=str, tags=['run'])
async def run_id(
    project_id: str,
    uid: str,
    runItem: RunItem,
    background_tasks: BackgroundTasks
):
    WorkflowRunner(project_id, uid, runItem).run_workflow(background_tasks)
    print("run snakemake")
    print("forcerun list: ", runItem.forceRunList)
    return uid


@router.post(
    "/run/result/{project_id}/{uid}", response_model=Dict[str, Message], tags=['run']
)
async def run_result(project_id: str, uid: str, nodeDict: NodeItem):
    return WorkflowResult(project_id, uid).get(nodeDict.pendingNodeIdList)


@router.get('/run_result/{project_id}', response_model=Dict[str, ExptInfo], tags=['run_result'])
async def get_experiment_info(project_id: str):
    """
    Send the experiment info about all the workflow analyses associated with a given project.
    """

    # TODO: Get the all analysis IDs from <OUTPUT>/<project ID>, and iterate get_experiment_info() with those IDs.
    # Dummy
    analysis_id_list = ['3a55fa37']

    experiment_info_list = {}
    for analysis_id in analysis_id_list:
        experiment_info_list[analysis_id] = WorkflowResult(project_id, analysis_id).get_experiment_info()

    return experiment_info_list
