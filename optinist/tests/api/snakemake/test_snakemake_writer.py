import os

from optinist.api.dir_path import DIRPATH
from optinist.api.snakemake.snakemake_writer import SmkConfigWriter

project_id = "test_project"
unique_id = "smk_test"
output_fileapth = f"{DIRPATH.OUTPUT_DIR}/{project_id}/{unique_id}/config.yaml"


def test():
    if os.path.exists(output_fileapth):
        os.remove(output_fileapth)

    SmkConfigWriter.write(
        project_id,
        unique_id,
        {"test"},
    )

    assert os.path.exists(output_fileapth)
