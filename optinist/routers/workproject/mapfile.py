from collections import OrderedDict

class MapFile:
    """ファイルマップ中のファイルを表すデータクラス"""

    def __init__(self, id: str = "", path: str = "") -> None:
        self.__id: str = id
        self.__path: str = path


    def create_dict(self) -> OrderedDict:
        """連想配列に変換します。"""

        dst: OrderedDict = OrderedDict()
        dst['id'] = self.__id
        dst['path'] = self.__path
        return dst
    
    @property
    def id(self) -> int:
        return self.__id
    
    @property
    def path(self) -> str:
        return self.__path