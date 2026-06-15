"""Agent Orchestrator 配置管理"""
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    name: str = Field(default="ecom_order_hub", alias="DB_NAME")
    user: str = Field(default="ecom", alias="DB_USER")
    password: str = Field(default="", alias="DB_PASSWORD")

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    model_config = {"env_prefix": "", "extra": "ignore"}


class RedisSettings(BaseSettings):
    url: str = Field(
        default="",
        alias="REDIS_URL",
    )
    model_config = {"env_prefix": "", "extra": "ignore"}


class LLMSettings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    model_config = {"env_prefix": "", "extra": "ignore"}


class ServiceSettings(BaseSettings):
    go_server_url: str = Field(default="http://localhost:8080", alias="GO_SERVER_URL")
    python_worker_url: str = Field(default="http://localhost:8000", alias="PYTHON_WORKER_URL")
    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    service_account_user: str = Field(default="", alias="SERVICE_ACCOUNT_USER")
    service_account_password: str = Field(default="", alias="SERVICE_ACCOUNT_PASSWORD")
    model_config = {"env_prefix": "", "extra": "ignore"}


class Settings(BaseSettings):
    server_port: int = Field(default=9000, alias="AGENT_PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:80,http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    llm: LLMSettings = LLMSettings()
    services: ServiceSettings = ServiceSettings()

    model_config = {"env_prefix": "", "extra": "ignore"}

    @model_validator(mode="after")
    def check_required_secrets(self) -> "Settings":
        """验证必需的敏感配置 (Pydantic v2 正确方式)"""
        required_secrets = {
            "db.password": self.db.password,
            "redis.url": self.redis.url,
            "services.jwt_secret": self.services.jwt_secret,
            "services.service_account_password": self.services.service_account_password,
        }
        missing = [k for k, v in required_secrets.items() if not v.strip()]
        if missing:
            raise ValueError(
                f"缺少必需的环境变量: {', '.join(missing)}. "
                "请通过环境变量或 .env 文件设置。"
            )
        return self


settings = Settings()
