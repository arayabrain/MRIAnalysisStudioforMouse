from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    OPTINIST_DIR: str = Field(default='/tmp/optinist', env="OPTINIST_DIR")

    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24 * 1, env="REFRESH_TOKEN_EXPIRE_MINUTES"
    )

    SECRET_KEY: str = Field(default='123456', env="SECRET_KEY")

    USE_FIREBASE_TOKEN: bool = Field(default=True, env="USE_FIREBASE_TOKEN")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
