import pytest
from fastapi.testclient import TestClient
from optinist.routers.model import Algo

from optinist.wrappers import wrapper_dict
from optinist.routers.algolist import NestDictGetter, router

client = TestClient(router)


def test_run():
    response = client.get("/algolist")
    output = response.json()

    assert response.status_code == 200
    assert isinstance(output, dict)
    assert "suite2p" in output
    assert "children" in output["suite2p"]
    assert "suite2p_file_convert" in output["suite2p"]["children"]

    assert "args" in output["suite2p"]["children"]["suite2p_file_convert"]
    assert "path" in output["suite2p"]["children"]["suite2p_file_convert"]
    assert "vbm" in output


def test_NestDictGetter():
    output = NestDictGetter.get_nest_dict(wrapper_dict, "")

    assert isinstance(output, dict)
    assert "suite2p" in output
    assert "children" in output["suite2p"]
    assert "suite2p_file_convert" in output["suite2p"]["children"]

    assert isinstance(output["suite2p"]["children"]["suite2p_file_convert"], Algo)
