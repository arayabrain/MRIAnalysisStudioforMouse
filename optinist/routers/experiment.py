from typing import Dict, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

import shutil
from glob import glob

from optinist.api.dir_path import DIRPATH
from optinist.api.utils.filepath_creater import join_filepath
from optinist.api.experiment.experiment_reader import ExptConfigReader
from optinist.api.experiment.experiment import ExptConfig, ExptImportData
from optinist.routers.model import DeleteItem

router = APIRouter()


@router.get(
    "/experiments/{project_id}",
    response_model=Dict[str, ExptConfig],
    tags=['experiments']
)
async def get_experiments(project_id: str):
    exp_config = {}
    config_paths = glob(
        join_filepath([DIRPATH.OUTPUT_DIR, project_id, "*", DIRPATH.EXPERIMENT_YML])
    )
    for path in config_paths:
        try:
            config = ExptConfigReader.read(path)
            config.nodeDict = []
            config.edgeDict = []
            exp_config[config.unique_id] = config
        except Exception:
            pass

    return exp_config


@router.get("/experiments/import/{unique_id}", response_model=ExptImportData, tags=['experiments'])
async def import_experiment(unique_id: str):
    config = ExptConfigReader.read(join_filepath([
        DIRPATH.OUTPUT_DIR,
        unique_id,
        DIRPATH.EXPERIMENT_YML
    ]))
    return {
        "nodeDict": config.nodeDict,
        "edgeDict": config.edgeDict,
    }


@router.get(
    "/experiments/fetch/{project_id}", response_model=ExptConfig, tags=["experiments"]
)
async def fetch_last_experiment(project_id: str):
    last_expt_config: Optional[ExptConfig] = None
    config_paths = glob(
        join_filepath([DIRPATH.OUTPUT_DIR, project_id, "*", DIRPATH.EXPERIMENT_YML])
    )
    for path in config_paths:
        config = ExptConfigReader.read(path)
        if not last_expt_config:
            last_expt_config = config
        elif datetime.strptime(
            config.started_at, "%Y-%m-%d %H:%M:%S"
        ) > datetime.strptime(last_expt_config.started_at, "%Y-%m-%d %H:%M:%S"):
            last_expt_config = config
    if last_expt_config:
        return last_expt_config
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/experiments/{unique_id}", response_model=bool, tags=['experiments'])
async def delete_experiment(unique_id: str):
    try:
        shutil.rmtree(join_filepath([DIRPATH.OUTPUT_DIR, unique_id]))
        return True
    except Exception:
        return False


@router.post("/experiments/delete", response_model=bool, tags=['experiments'])
async def delete_experiment_list(deleteItem: DeleteItem):
    try:
        [
            shutil.rmtree(join_filepath([DIRPATH.OUTPUT_DIR, uid]))
            for uid in deleteItem.uidList
        ]
        return True
    except Exception as e:
        return False


@router.get("/experiments/download/nwb/{unique_id}", tags=['experiments'])
async def download_nwb_experiment(unique_id: str):
    nwb_path_list = glob(join_filepath([
        DIRPATH.OUTPUT_DIR,
        unique_id,
        "*.nwb"
    ]))
    if len(nwb_path_list) > 0:
        return FileResponse(nwb_path_list[0])
    else:
        return False


@router.get("/experiments/download/nwb/{unique_id}/{function_id}", tags=['experiments'])
async def download_nwb_experiment(unique_id: str, function_id: str):
    nwb_path_list = glob(join_filepath([
        DIRPATH.OUTPUT_DIR,
        unique_id,
        function_id,
        "*.nwb"
    ]))
    if len(nwb_path_list) > 0:
        return FileResponse(nwb_path_list[0])
    else:
        return False


@router.get("/experiments/download/config/{unique_id}", tags=['experiments'])
async def download_config_experiment(unique_id: str):
    config_filepath = join_filepath([
        DIRPATH.OUTPUT_DIR,
        unique_id,
        DIRPATH.SNAKEMAKE_CONFIG_YML
    ])
    return FileResponse(config_filepath)
