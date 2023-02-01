from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()


class Settings(BaseSettings):
    """configuration for apps"""

    MYSQL_ROOT_PASSWORD: str
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    DATABASE_URL: str = None
    PREFIX_DATABASE_URI: str = None
    ECHO_SQL: bool = None

    # pylint: disable=no-self-argument
    @validator('DATABASE_URL', pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """generate database url.

        Args:
            v (Optional[str]): value of DATABASE_URL variable
            values (Dict[str, Any]): values of all variables

        Returns:
            Any: new DATABASE_URL value
        """
        if isinstance(v, str):
            return v
        return f'mysql+aiomysql://{values.get("MYSQL_USER")}:{values.get("MYSQL_PASSWORD")}@{values.get("MYSQL_SERVER")}/{values.get("MYSQL_DATABASE")}?charset=utf8mb4'

    # pylint: disable=no-self-argument
    @validator('PREFIX_DATABASE_URI', pre=True)
    def assemble_testing_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        """generated database testing url.

        Args:
            v (Optional[str]): value of PREFIX_DATABASE_URI
            values (Dict[str, Any]): values of all variables

        Returns:
            Any: new PREFIX_DATABASE_URI value
        """
        if isinstance(v, str):
            return v
        return f'mysql+aiomysql://{values.get("MYSQL_USER")}:{values.get("MYSQL_PASSWORD")}@{values.get("MYSQL_SERVER")}'

    class Config:
        case_sensitive = True


settings = Settings()
