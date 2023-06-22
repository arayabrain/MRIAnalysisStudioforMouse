import csv
import json
import os
import shutil

""" utility.py
A collection of utility functions used in the voxel-based morphometry (VBM) analysis.
"""


def get_project_id():
    # DEBUG
    return 'h74ck4cz'


def get_error_message(error):
    """
    Get the error message string from an exception object.
    """

    error_message = ''
    for arg in error.args:
        error_message = error_message + str(arg) + ', '

    return error_message


# Load a config file.
def load_config():
    with open('config.json','r') as f:
        config = json.load(f)

    return config


# Create a command string for using SPM on MATLAB runtime.
def create_matlab_cmd(spm_script_path, matlab_runtime_path):
    return "{0} {1} script".format(spm_script_path, matlab_runtime_path)


# Get the BIDS root path.
def get_bids_root(project_id):
    # @fixme  本来は、松枝さん DB からパスを取得する。
    return '../../../sample_data/20230524-083153/'


# Get a subject ID list.
def get_subject_id_list(bids_root_path):
    subject_id_list = []
    with open(os.path.join(bids_root_path, 'participants.tsv')) as f:
        reader = csv.reader(f, delimiter='\t')
        for line in reader:
            if reader.line_num <= 1:   # Header
                continue
            if line[0]:
                subject_id_list.append(line[0])
         
    return subject_id_list


# Check if any data exist in the BIDS root folder.
def exist_data(bids_root_path, proc_name, subject_id=[]):
    if subject_id:
        target_dir = os.path.join(bids_root_path, 'derivatives', proc_name, subject_id)
    else:
        target_dir = os.path.join(bids_root_path, 'derivatives', proc_name)

    if not os.path.isdir(target_dir):
        return False
    else:
        file_list = os.listdir(target_dir)
        if len(file_list) > 0:
            return True
        else:
            return False


# Remove output files in the derivative folder.
def remove_data(bids_root_path, proc_name, subject_id=[]):
    if subject_id:
        target_dir = os.path.join(bids_root_path, 'derivatives', proc_name, subject_id)
    else:
        target_dir = os.path.join(bids_root_path, 'derivatives', proc_name)

    shutil.rmtree(target_dir)
