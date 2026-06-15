from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 数据库
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "ecom"
    db_password: str = ""
    db_name: str = "ecom_order_hub"

    # Redis
    redis_url: str = ""

    # Go 服务地址
    go_server_url: str = "http://localhost:8080"

    # 淘宝
    taobao_app_key: str = ""
    taobao_app_secret: str = ""
    taobao_callback_url: str = ""

    # 京东
    jd_app_key: str = ""
    jd_app_secret: str = ""
    jd_callback_url: str = ""

    # 拼多多
    pdd_client_id: str = ""
    pdd_client_secret: str = ""
    pdd_callback_url: str = ""

    # 通知
    dingtalk_webhook: Optional[str] = None
    wecom_webhook: Optional[str] = None

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"

    def __init__(self, /, **kwargs) -> None:
        super().__init__(**kwargs)
        required_secrets = {
            "DB_PASSWORD": self.db_password,
            "REDIS_URL": self.redis_url,
        }
        missing = [k for k, v in required_secrets.items() if not v.strip()]
        if missing:
            raise ValueError(
                f"缺少必需的环境变量: {', '.join(missing)}. "
                "请通过环境变量或 .env 文件设置。"
            )


settings = Settings()
