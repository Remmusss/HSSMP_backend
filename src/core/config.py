from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
        

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
    SQLSERVER_HOST: str
    SQLSERVER_DATABASE: str

    @property
    def SQLSERVER_CONNECTION(self) -> str:
        return (
            f"mssql+pyodbc://{self.SQLSERVER_HOST}/{self.SQLSERVER_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
        )

class SQLServerUserConfigs(CommonSettings):
    SQLSERVER_HOST: str
    SQLSERVER_USER_DB: str

    @property
    def SQLSERVER_USER_CONNECTION(self) -> str:
        return (
            f"mssql+pyodbc://{self.SQLSERVER_HOST}/{self.SQLSERVER_USER_DB}?driver=ODBC+Driver+17+for+SQL+Server"
        )
        

# Khởi tạo config
app_conf = AppSettings()
mysql_conf = MySQLConfigs()
sqlserver_conf = SQLServerConfigs()
