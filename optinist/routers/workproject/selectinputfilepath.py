from datetime import datetime
from glob import glob
import os
from typing import Optional
import yaml

from optinist.routers.workdbmanager import WorkDbManager
from optinist.routers.workproject.projectfilemap import ProjectFileMap

# workd projects root folder path
# WORKDB_ROOT_PATH: str = '/var/vbm/workdb'
WORKDB_ROOT_PATH: str = '/app/workdb'
# Optinist output folder path.
# ★OptiNiSt の出力フォルダーのパスは定数で指定します。
OPTINIST_OUTPUT_DIR_PATH: str = ''

def select_input_file_path(project_id: int, image_id: int) -> str:

    last_experiment_info = get_last_experiment_info(project_id)

    # Get work projet path.
    project_path = get_work_project_path(project_id)

    # Load and parse filemap.json.
    file_map: ProjectFileMap = ProjectFileMap()
    file_map.load(project_path)

    # Get image path in the work project.
    image_path: str = file_map.get_image_path(image_id)

    # Derivatives do not exist, return original image path.
    if last_experiment_info is None:
        return os.path.join(project_path, image_path)

    # Derivatives exist, return image path in last derivative folder.
    alignment_dir_path = os.path.join(project_path, 'derivatives', last_experiment_info['unique_id'], 'alignment')
    image_file_name = os.path.basename(image_path)
    image_file_name_without_extension = os.path.splitext(image_file_name)[0]
    aligned_file_path = os.path.join(alignment_dir_path, image_file_name_without_extension, image_file_name)

    return aligned_file_path if os.path.isfile(aligned_file_path) else os.path.join(project_path, image_path)


def get_last_experiment_info(project_id: int) -> dict:
    experiment_file_paths = glob(os.path.join(OPTINIST_OUTPUT_DIR_PATH, str(project_id), '*', 'experiment.yaml'))

    # Find the latest experiment info basd on the start time.
    last_experiment_info = None
    for experiment_file in experiment_file_paths:
        experiment_info = read_yaml(experiment_file)
        if not last_experiment_info:
            last_experiment_info = experiment_info
        elif datetime.strptime(experiment_info.started_at, "%Y-%m-%d %H:%M:%S") > \
                datetime.strptime(last_experiment_info.started_at, "%Y-%m-%d %H:%M:%S"):
            last_experiment_info = experiment_info

    return last_experiment_info


def read_yaml(file_path):
    data = {}
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = yaml.safe_load(f)
    return data


def get_work_project_path(project_id: int, no_check_folder: bool = False) -> str:
    """
    指定プロジェクトのファイルシステム上のパスを取得します。併せて、DB 操作クラスも用意します。

    Parameters
    ----------
    project_id: int         対象となる Work プロジェクトの ID
    no_check_folder: bool   True の場合、プロジェクトフォルダの有無はチェックしません。

    Returns
    -------
    Work プロジェクトフォルダのパス
    """

    work_db: WorkDbManager = WorkDbManager()
    if not work_db.open():
        raise Exception('Database open error.')
    
    path: Optional[str] = work_db.get_project_path(project_id)
    if (path is None):
        # プロジェクト未登録エラー
        raise Exception('Project not found.')

    # ファイルシステム上に対応するプロジェクトがあるか確認します。
    project_path: str = os.path.join(WORKDB_ROOT_PATH, path[1:])
    if not no_check_folder and not os.path.exists(project_path):
        # : プロジェクト未登録エラー
        raise IOError('Project files not found.')

    work_db.close()
    return project_path
