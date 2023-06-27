import shutil
import pytest
from fastapi.testclient import TestClient
import os

from optinist.routers.experiment import router
from optinist.api.utils.filepath_creater import join_filepath
from optinist.api.dir_path import DIRPATH

client = TestClient(router)

project_id = "test_project"
unique_id = "0123"

output_test_dir = f"{DIRPATH.OPTINIST_DIR}/output_test"

shutil.copytree(
    f"{output_test_dir}/{project_id}/{unique_id}",
    f"{DIRPATH.OUTPUT_DIR}/{project_id}/{unique_id}",
    dirs_exist_ok=True,
)


def test_get():
    response = client.get(f"/experiments/{project_id}")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert isinstance(data[next(iter(data))], dict)


def test_delete():
    dirname = "delete_dir"
    dirpath = join_filepath([DIRPATH.OUTPUT_DIR, dirname])
    os.makedirs(dirpath, exist_ok=True)
    assert os.path.exists(dirpath)
    response = client.delete(f"/experiments/{dirname}")
    assert response.status_code == 200
    assert not os.path.exists(dirpath)


def test_delete_list():
    uidList = ["delete_dir1", "delete_dir2"]
    for name in uidList:
        dirpath = join_filepath([DIRPATH.OUTPUT_DIR, name])
        os.makedirs(dirpath, exist_ok=True)
        assert os.path.exists(dirpath)

    response = client.post("/experiments/delete", json={"uidList": uidList})
    assert response.status_code == 200

    for name in uidList:
        dirpath = join_filepath([DIRPATH.OUTPUT_DIR, name])
        assert not os.path.exists(dirpath)
