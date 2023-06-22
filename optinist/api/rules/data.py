# flake8: noqa
# Exclude from lint for the following reason
# This file is executed by snakemake and cause the following lint errors
# - E402: sys.path.append is required to import optinist modules
# - F821: do not import snakemake
import sys

from const import OPTINIST_DIRPATH

sys.path.append(OPTINIST_DIRPATH)

from optinist.api.pickle.pickle_writer import PickleWriter
from optinist.api.rules.file_writer import FileWriter
from optinist.api.snakemake.snakemake_reader import RuleConfigReader
from optinist.routers.model import FILETYPE


def process_dummy_image(rule_config, params: dict = None):
    """
    Since mri studio uses an image type node for the data input node,
      here we specify one dummy image path as a fixed path for debugging purposes.
    """
    print('params:', params)

    # Specify the path to any existing dummy images.
    return ['sample_data/mouse2p_2_donotouse.tiff']


if __name__ == "__main__":
    last_output = snakemake.config["last_output"]

    rule_config = RuleConfigReader.read(snakemake.params.name)
    if rule_config.type in [FILETYPE.IMAGE]:
        rule_config.input = snakemake.input
    elif rule_config.type in [FILETYPE.CSV, FILETYPE.BEHAVIOR, FILETYPE.HDF5]:
        rule_config.input = snakemake.input[0]

    rule_config.output = snakemake.output[0]


    info = process_dummy_image(rule_config, snakemake.params.name['params'])

    rule_config.input = info

    if rule_config.type in [FILETYPE.CSV, FILETYPE.BEHAVIOR]:
        outputfile = FileWriter.csv(rule_config, rule_config.type)
        PickleWriter.write(rule_config.output, outputfile)
    elif rule_config.type == FILETYPE.IMAGE:
        outputfile = FileWriter.image(rule_config)
        PickleWriter.write(rule_config.output, outputfile)
    elif rule_config.type == FILETYPE.HDF5:
        outputfile = FileWriter.hdf5(rule_config)
        PickleWriter.write(rule_config.output, outputfile)
