"""
谋策智能体配置管理 (V2.2)
基于 Pydantic 的类型安全配置
"""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # 如果没有安装 pydantic-settings，回退到简单实现
    class BaseSettings:
        """简单的配置基类回退"""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self._load_from_env()

        def _load_from_env(self):
            """从环境变量加载配置"""
            from dotenv import load_dotenv
            load_dotenv()
            for attr_name in dir(self):
                if attr_name.startswith("_"):
                    continue
                env_var = attr_name.upper()
                env_value = os.getenv(env_var)
                if env_value is not None:
                    current = getattr(self, attr_name, None)
                    if isinstance(current, bool):
                        setattr(self, attr_name, env_value.lower() in ("true", "1", "yes"))
                    elif isinstance(current, int):
                        setattr(self, attr_name, int(env_value))
                    else:
                        setattr(self, attr_name, env_value)


class Settings(BaseSettings):
    """
    智能体全局配置

    支持从 .env 文件或环境变量加载配置。
    """

    # 模型配置
    default_model_provider: str = "glm4"
    max_context_tokens: int = 8000

    # 日志配置
    log_level: str = "INFO"

    # 质量检查
    enable_quality_check: bool = True

    # 智能体版本
    agent_version: str = "2.2.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置实例（懒加载）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
