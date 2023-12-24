from typing import Dict
from fastapi import APIRouter, BackgroundTasks
import uuid

from optinist.api.workflow.workflow import NodeItem, RunItem, Message, ExptInfo
from optinist.api.workflow.workflow_runner import WorkflowRunner
from optinist.api.workflow.workflow_result import WorkflowResult
from optinist.routers.experiment import get_last_experiment

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
    """ Send the info about the latest workflow analysis results for a given project. """

    # Get the latest ExptConfig data from experiment.yaml.
    last_expt_config = get_last_experiment(project_id)

    # Get the experiment info from ExptConfig data.
    experiment_info = WorkflowResult(project_id, last_expt_config.unique_id).get_experiment_info(last_expt_config)

    return {last_expt_config.unique_id: experiment_info}
