import MySQLdb as mysql
import os

from fastapi import HTTPException, status
from typing import Optional

from optinist.routers.workproject.projectfilemap import ProjectFileMap


# Studio コンテナ上にマウントされた WorkDB フォルダのパス
WORKDB_ROOT_PATH: str = '/app/workdb'


def get_project_path(project_id: int) -> str:
    work_db: WorkDbManager = WorkDbManager()
    if not work_db.open():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[{"loc": ["get_workdb_image_file"], "msg": "could not open database", "type": "database error"}]
            )

    path: Optional[str] = work_db.get_project_path(project_id)
    work_db.close()

    if (path is None):
        # プロジェクト未登録エラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[{"loc": ["get_workdb_image_file"], "msg": "could not find work project", "type": "database error"}]
            )

    # ファイルシステム上に対応するプロジェクトがあるか確認します。
    project_path: str = os.path.join(WORKDB_ROOT_PATH, path[1:])
    # if not no_check_folder and not os.path.exists(project_path):
    #     # : プロジェクト未登録エラー
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=[{"loc": ["get_workdb_image_file"], "msg": "could not find work project", "type": "file system error"}]
    #         )

    return project_path


def get_work_project_image_path(project_id: int, image_id: int, function_name: Optional[str] = None) -> str:
    """
    Work プロジェクト内のファイルパスを作成します。返されたパスのファイルがあることは保証しません。

    Parameters
    ----------
    project_id: int                 操作対象となる Work プロジェクトの ID
    image_id: int                   パス取得対象となる画像の ID
    function_name: Optional[str]    derivatives 内に格納されている関数フォルダ名。
                                    指定しなかった場合、alignment のパスの取得を試行します。
                                    alignment に対応する画像ファイルがなければ、derivatives 外のファイルのパスを返します。

    Returns
    -------
    """

    # プロジェクトパスと WorkDB クラスへの参照を取得します。
    # NOTE: エラー時は内部で FastAPI を対象とした例外が発生します。
    project_path = get_project_path(project_id)

    # FileMap を読み込みます。
    file_map: ProjectFileMap = ProjectFileMap()
    file_map.load(project_path)

    # 指定画像のプロジェクト内パスを取得します。
    image_path: str = file_map.get_image_path(image_id)

    # function が指定されていない場合、derivatives/alignment のファイルをチェックし、存在すればそのパスを返します。
    # 存在しない場合は、derivatives 外のファイルのパスを返します (こちらはファイルの有無はチェックしません)。
    if function_name is None:
        alignment_path: str = os.path.join(project_path, 'derivatives', 'alignment', image_path)
        if os.path.exists(alignment_path):
            return alignment_path
        else:
            return os.path.join(project_path, image_path)

    # function が指定されている場合、derivatives/{function_name} のファイルパスを作成し返します。
    # ファイルの有無はチェックしません。
    else:
        return os.path.join(project_path, 'derivatives', function_name, image_path)


class WorkDbManager:
    """DB とのアクセスを担うクラスです。"""

    # 定数宣言
    HOST = 'vbm_db'
    USER = 'root'
    PASSWD = 'vbmbids'
    DB_NAME = 'vbm_db'

    LAST_ID_SQL: str = 'SELECT LAST_INSERT_ID()'
    DATE_FORMAT: str = '%Y-%m-%dT%H:%M:%S'

    def __init__(self):
        """コンストラクタ"""

        # メンバ変数を初期化します。
        self.__connection: Optional[mysql.connection] = None
        self.__cursor: Optional[mysql.cursors.Cursor] = None

    def open(self) -> bool:
        """
        DB との接続を開きます。

        Returns
        -------
        開けたなら True。失敗時は False。
        """

        if self.__connection is not None:
            return True
        
        self.__connection = mysql.connect(
            user=self.USER,
            passwd=self.PASSWD,
            host=self.HOST,
            db=self.DB_NAME,
            charset='utf8',
            use_unicode=True)
        
        if self.__connection is None:
            return False

        self.__cursor = self.__connection.cursor()
        return True

    def close(self) -> None:
        """DB との接続を終了します。"""

        if self.__cursor is not None:
            self.__cursor.close()
            self.__cursor = None
        
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None

    def get_project_path(self, id: int) -> Optional[str]:
        """
        プロジェクトの保存パスを取得します。

        Parameters
        ----------
        id: int     プロジェクト ID

        Returns
        -------
        プロジェクトの保存パス (WorkDB 内)
        """

        self.__cursor.execute(
            "SELECT project_path FROM t_work_project WHERE id = %(id)s",
            { 'id': id }
        )

        rows = self.__cursor.fetchall()

        if len(rows) > 0:
            return rows[0][0]
        else:
            return None
