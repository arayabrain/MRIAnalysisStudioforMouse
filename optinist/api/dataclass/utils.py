import copy
import numpy as np
import pathlib


def create_images_list(data):
    if len(data.shape) == 2:
        save_data = copy.deepcopy(data)
    elif len(data.shape) == 3:
        save_data = copy.deepcopy(data[:10])
    else:
        assert False, 'data is error'

    if len(data.shape) == 2:
        data = data[np.newaxis, :, :]
        save_data = save_data[np.newaxis, :, :]

    images = []
    for _img in save_data:
        images.append(_img.tolist())

    return images


def check_path_format(paths):
    """
    Convert the path to follow the POSIX format, and remove redundant tokens.

    [arguments]
    paths: A string of path or a list of paths.
    """

    if isinstance(paths, list):
        output_paths = []
        for path in paths:
            output_paths.append(str(pathlib.Path(path).resolve()).replace('\\', '/'))
        return output_paths
    elif isinstance(paths, str):
        return str(pathlib.Path(paths).resolve()).replace('\\', '/')
    else:
        return None
