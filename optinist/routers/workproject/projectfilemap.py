import json
import logging
import os
from collections import OrderedDict
from typing import Dict, List, Optional

from optinist.routers.workproject.mapfolder import MapFolder

class ProjectFileMap:
    """プロジェクトに属するファイルの表示上のフォルダと実フォルダの対応関係を管理するクラスです。"""

    FILE_NAME: str = 'filemap.json'

    def __init__(self) -> None:
        """空のマップを作成します。保存はしません。"""
        self.__folder_list: List[MapFolder] = []

    def append(self, root_folder_name: str, sub_folder_name: str, image_id: int, image_path: str) -> None:
        """
        マップにファイルを１つ追加します。保存はしません。ファイルの追加は別途行います。

        Parameters
        ----------
        root_folder_name: str   上位フォルダ名
        sub_folder_name: str    下位フォルダ名。下位フォルダがない場合は空文字列
        image_id: int           追加する画像の ID
        image_path: str         work プロジェクト内の画像パス
        """

        # 上位レイヤーへの参照を取得します。なければ作成します。
        top_folder: Optional[MapFolder] = self.__get_folder(root_folder_name, self.__folder_list)

        if top_folder is None:
            top_folder = MapFolder(root_folder_name)
            self.__folder_list.append(top_folder)

        # サブレイヤーが指定されていれば、参照を取得します (ない場合は作成します)。
        if sub_folder_name != '':
            sub_folder: Optional[MapFolder] = self.__get_folder(sub_folder_name, top_folder.folder_list)
            if sub_folder is None:
                sub_folder = MapFolder(sub_folder_name)
                top_folder.append_folder(sub_folder)
            # サブレイヤーに画像を登録します。
            sub_folder.append_image(image_id, image_path)
        
        # サブレイヤーが指定されていない場合は、上位レイヤーに画像を登録します。
        else:
            top_folder.append_image(image_id, image_path)


    def __get_folder(self, folder_name: str, folder_list: List[MapFolder]) -> Optional[MapFolder]:
        """指定した名前を持つフォルダーへの参照を取得します。"""
        for i in range(len(folder_list)):
            if folder_list[i].name == folder_name:
                return folder_list[i]
        return None

    def flush(self, project_path: str) -> None:
        """
        マップファイルに書き出しを実行します。

        Parameters
        ----------
        project_path: str   マップファイルを書き出すプロジェクトのパス
        """

        dict_data: List[OrderedDict] = self.convert_to_response()

        with open(os.path.join(project_path, self.FILE_NAME), mode='w') as dst:
            json.dump(dict_data, dst, sort_keys=False, indent=4)
        

    def load(self, project_path: str) -> List[Dict]:
        """
        指定ファイルからデータを読み込みます。
        クラスのインスタンスにも読み込みますが、JSON をパースした連想配列も返します。

        Parameters
        ----------
        project_path: str   読み込み対象のマップファイルを保有するプロジェクトのパス

        Returns
        -------
        JSON ファイルを読み込んだ生の連想配列
        """

        # フォルダリストをリセットします。
        self.__folder_list = []

        # 連想配列としてデータを読み込みます。
        with open(os.path.join(project_path, self.FILE_NAME), mode='r') as src:
            json_data = json.load(src)
        
        for folder_src in json_data:
            folder: MapFolder = MapFolder(**folder_src)
            self.__folder_list.append(folder)

        # クラスとして読み込んだものとは別に、生の辞書データを返します。
        return json_data

    def convert_to_response(self) -> List[OrderedDict]:
        """
        保持データから HttpResponse 用の連想配列を返します。

        Returns
        -------
        メンバ変数に保持されているデータに対応する連想配列
        """

        dst: List[OrderedDict] = []

        for folder in self.__folder_list:
            dst.append(folder.create_dict())

        return dst
    
    @property
    def image_count(self) -> int:
        """画像数を取得します。"""
        result: int = 0

        for folder in self.__folder_list:
            result += folder.image_count

        return result
    
    def get_image_path(self, image_id: int) -> str:
        """
        指定された画像のプロジェクト内パスを取得します。

        Parameters
        ----------
        image_id: int   画像 ID

        Returns
        -------
        指定画像のプロジェクト内のパス。見つからなければ空文字列
        """

        for folder in self.__folder_list:
            image_path: str = folder.get_image_path(image_id)
            if image_path != '':
                return image_path
        
        return ''