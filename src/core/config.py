from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    class Config:
        env_file = ".env"


class AppSettings(CommonSettings):
    APP_NAME: str
    APP_VERSION: str


class MySQLConfigs(CommonSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str

    @property
    def MYSQL_CONNECTION(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )


class SQLServerConfigs(CommonSettings):
    SQLSERVER_USER: str
    SQLSERVER_PASSWORD: str
    SQLSERVER_HOST: str
    SQLSERVER_PORT: int
    SQLSERVER_DATABASE: str

    @property
    def SQLSERVER_CONNECTION(self) -> str:
        return (
            f"mssql+pymssql://{self.SQLSERVER_USER}:{self.SQLSERVER_PASSWORD}"
            f"@{self.SQLSERVER_HOST}:{self.SQLSERVER_PORT}/{self.SQLSERVER_DATABASE}"
        )


# Khởi tạo config
app_conf = AppSettings()
mysql_conf = MySQLConfigs()
sqlserver_conf = SQLServerConfigs()
