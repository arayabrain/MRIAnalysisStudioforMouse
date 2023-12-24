import pathlib
from typing import List, Union


def check_path_format(path_list: Union[List[str], str]) -> Union[List[str], str]:
    """ Check and modify a path to follow the POSIX format as well as removing redundant tokens.
    A relative path will be changed to the full path.

    Parameters
        ----------
        path_list : list[str] or str
            A list of paths or a str of a path.
    """

    if isinstance(path_list, list):
        path_list_out = []
        for path in path_list:
            path_list_out.append(str(pathlib.Path(path).resolve()).replace('\\', '/'))
        return path_list_out
    elif isinstance(path_list, str):
        return str(pathlib.Path(path_list).resolve()).replace('\\', '/')
    else:
        return None
