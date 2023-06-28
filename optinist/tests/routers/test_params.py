import pytest
from fastapi.testclient import TestClient

from optinist.routers.params import router

client = TestClient(router)


def test_params():
    response = client.get("/params/suite2p_file_convert")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)

    assert isinstance(data["nplanes"], int)
    assert data["nplanes"] == 1

    assert isinstance(data["force_sktiff"], bool)
    assert data["force_sktiff"] == False


def test_snakemake_params():
    response = client.get("/snakemake")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)

    assert isinstance(data["cores"], int)
    assert data["cores"] == 2

    assert isinstance(data["use_conda"], bool)
    assert data["use_conda"] == True


def test_nwb_params():
    response = client.get("/nwb")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)

    assert isinstance(data["session_description"], str)
    assert data["session_description"] == "optinist"
