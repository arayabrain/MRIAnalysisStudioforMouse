import logging
from collections import OrderedDict
from typing import List, Optional

from optinist.routers.workproject.mapfile import MapFile

class MapFolder:
    """ファイルマップ中のフォルダを表すデータクラス"""
    def __init__(self, folder_name: str = "", images: Optional[List] = None, sub_folders: Optional[List] = None) -> None:
        self.__folder_name: str = folder_name

        self.__images: List[MapFile] = []
        if images is not None:
            for image in images:
                self.__images.append(MapFile(**image))
        
        self.__sub_folders: List[MapFolder] = []
        if sub_folders is not None:
            for folder in sub_folders:
                self.__sub_folders.append(MapFolder(**folder))

    @property
    def name(self) -> str:
        return self.__folder_name
    
    @property
    def folder_list(self) -> List["MapFolder"]:
        return self.__sub_folders

    @property
    def image_count(self) -> int:
        """サブフォルダも含めた画像数を取得します。"""
        result: int = len(self.__images)

        for folder in self.__sub_folders:
            result += folder.image_count

        return result
    
    def append_image(self, id: int, image_path: str) -> None:
        self.__images.append(MapFile(id, image_path))

    def append_folder(self, folder: "MapFolder") -> None:
        self.__sub_folders.append(folder)


    def create_dict(self) -> OrderedDict:
        dst: OrderedDict = OrderedDict()

        dst['folder_name'] = self.__folder_name

        if len(self.__images) > 0:
            dst['images'] = []
            for image in self.__images:
                dst['images'].append(image.create_dict())

        if len(self.__sub_folders) > 0:
            dst['sub_folders'] = []
            for folder in self.__sub_folders:
                dst['sub_folders'].append(folder.create_dict())

        return dst
    
    def get_image_path(self, image_id: int) -> str:
        """指定された画像のパスを取得します。見つからなければ空文字を返します。"""

        # 直下の画像から一致する画像を検索します。
        for image in self.__images:
            if image.id == image_id:
                return image.path
        
        # サブフォルダーから一致する画像を検索します。
        for folder in self.__sub_folders:
            image_path: str = folder.get_image_path(image_id)
            if image_path != '':
                return image_path
        
        return ''