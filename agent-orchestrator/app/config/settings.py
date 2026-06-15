"""Agent Orchestrator 配置管理"""
from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    name: str = Field(default="ecom_order_hub", alias="DB_NAME")
    user: str = Field(default="ecom", alias="DB_USER")
    password: str = Field(default="ecom_secret_123", alias="DB_PASSWORD")

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    model_config = {"env_prefix": "", "extra": "ignore"}


class RedisSettings(BaseSettings):
    url: str = Field(
        default="redis://:redis_secret_123@localhost:6379/1",
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
    jwt_secret: str = Field(default="your_jwt_secret_key_at_least_32_chars_long", alias="JWT_SECRET")
    service_account_user: str = Field(default="agent_service", alias="SERVICE_ACCOUNT_USER")
    service_account_password: str = Field(default="agent_service_secret", alias="SERVICE_ACCOUNT_PASSWORD")
    model_config = {"env_prefix": "", "extra": "ignore"}


class Settings(BaseSettings):
    server_port: int = Field(default=9000, alias="AGENT_PORT")
    debug: bool = Field(default=False, alias="DEBUG")

    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    llm: LLMSettings = LLMSettings()
    services: ServiceSettings = ServiceSettings()

    model_config = {"env_prefix": "", "extra": "ignore"}


settings = Settings()
