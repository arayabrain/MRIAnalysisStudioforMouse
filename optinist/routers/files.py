import os
from glob import glob
from typing import List
from fastapi import APIRouter

from optinist.api.dir_path import DIRPATH
from optinist.api.utils.filepath_creater import join_filepath
from optinist.routers.model import TreeNode

router = APIRouter()


class DirTreeGetter:

    @classmethod
    def get_tree(cls, file_types: List[str], dirname: str = None) -> List[TreeNode]:
        nodes: List[TreeNode] = []

        if dirname is None:
            absolute_dirpath = DIRPATH.INPUT_DIR
        else:
            absolute_dirpath = join_filepath([DIRPATH.INPUT_DIR, dirname])

        for node_name in os.listdir(absolute_dirpath):

            if dirname is None:
                relative_path = node_name
            else:
                relative_path = join_filepath([dirname, node_name])

            search_dirpath = join_filepath([absolute_dirpath, node_name])

            if os.path.isfile(search_dirpath) and node_name.endswith(tuple(file_types)):
                nodes.append(TreeNode(
                    path=relative_path,
                    name=node_name,
                    isdir=False,
                    nodes=[],
                ))
            elif os.path.isdir(search_dirpath) and len(cls.accept_files(search_dirpath, file_types)) > 0:
                nodes.append(TreeNode(
                    path=node_name,
                    name=node_name,
                    isdir=True,
                    nodes=cls.get_tree(file_types, relative_path)
                ))

        return nodes

    @classmethod
    def accept_files(cls, path: str, file_types: List[str]):
        files_list = []
        for file_type in file_types:
            files_list.extend(glob(
                join_filepath([path, "**", f"*{file_type}"]),
                recursive=True
            ))

        return files_list
