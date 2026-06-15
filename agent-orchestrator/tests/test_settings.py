"""测试 Settings 强制环境变量注入"""
import pytest
import os
from unittest.mock import patch


# 使用完整的模块路径来导入，避免相对导入问题
def test_settings_requires_db_password():
    """没有 DB_PASSWORD 时应抛出 ValueError"""
    with patch.dict(os.environ, {}, clear=True):
        from app.config.settings import Settings
        with pytest.raises(ValueError, match="缺少必需的环境变量"):
            Settings()


def test_settings_requires_redis_url():
    """没有 REDIS_URL 时应抛出 ValueError"""
    with patch.dict(os.environ, {}, clear=True):
        from app.config.settings import Settings
        with pytest.raises(ValueError, match="缺少必需的环境变量"):
            Settings()


def test_settings_requires_jwt_secret():
    """没有 JWT_SECRET 时应抛出 ValueError"""
    with patch.dict(os.environ, {}, clear=True):
        from app.config.settings import Settings
        with pytest.raises(ValueError, match="缺少必需的环境变量"):
            Settings()


def test_settings_accepts_all_required_env_vars():
    """提供所有必需环境变量时应成功创建 Settings"""
    env = {
        "DB_PASSWORD": "test_password_123",
        "REDIS_URL": "redis://:test@localhost:6379/1",
        "JWT_SECRET": "test_jwt_secret_at_least_32_chars_long!!",
        "SERVICE_ACCOUNT_PASSWORD": "test_sa_password",
    }
    with patch.dict(os.environ, env, clear=True):
        from app.config.settings import Settings
        s = Settings()
        assert s.db.password == "test_password_123"
        assert s.redis.url == "redis://:test@localhost:6379/1"
        assert len(s.services.jwt_secret) >= 32
