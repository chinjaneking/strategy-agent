"""
谋策智能体配置文件
加载环境变量并定义智能体配置
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def _get_env_dir() -> Path:
    override_dir = os.getenv("STRATEGY_AGENT_ENV_DIR")
    if override_dir:
        return Path(override_dir)
    return Path(__file__).resolve().parent.parent


def _load_environment():
    env_dir = _get_env_dir()
    load_dotenv(env_dir / ".env")
    load_dotenv(env_dir / ".env.local", override=True)


def _build_agent_config() -> dict:
    return {
        "glm4": {
            "api_key": os.getenv("GLM4_API_KEY"),
            "base_url": os.getenv("GLM4_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"),
            "model": os.getenv("GLM4_MODEL", "glm-4"),
            "temperature": 0.2,
            "timeout": 120,
        },
        "kimi": {
            "api_key": os.getenv("KIMI_API_KEY"),
            "base_url": os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1"),
            "model": os.getenv("KIMI_MODEL", "moonshot-v1-8k"),
            "temperature": 0.2,
            "timeout": 120,
        },
        "minimax": {
            "api_key": os.getenv("MINIMAX_API_KEY"),
            "base_url": os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
            "model": os.getenv("MINIMAX_MODEL", "abab6.5-chat"),
            "temperature": 0.2,
            "timeout": 120,
        },
    }


def _refresh_runtime_config():
    global DEFAULT_PROVIDER, AGENT_CONFIG
    _load_environment()
    DEFAULT_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "glm4")
    AGENT_CONFIG = _build_agent_config()


_refresh_runtime_config()

# 智能体信息
AGENT_INFO = {
    "name": "谋策智能体 Strategy Agent V2.2",
    "description": "基于中国传统谋略（鬼谷子、孙子兵法）与毛泽东思想的高级决策分析AI智能体",
    "version": "2.2.0",
    "author": "谋策团队",
}


def get_config(provider: str = None) -> dict:
    """
    获取指定提供商的配置

    Args:
        provider: 模型提供商，可选 glm4/kimi/minimax，默认使用环境变量配置

    Returns:
        配置字典
    """
    _refresh_runtime_config()
    provider = provider or DEFAULT_PROVIDER
    if provider not in AGENT_CONFIG:
        raise ValueError(f"不支持的模型提供商: {provider}，可选: {list(AGENT_CONFIG.keys())}")

    config = AGENT_CONFIG[provider].copy()

    # 检查 API Key
    if not config.get("api_key") or config["api_key"] == f"your_{provider}_api_key_here":
        raise ValueError(f"请设置 {provider.upper()}_API_KEY 环境变量或在 .env 文件中配置")

    return config


def get_available_providers() -> list:
    """获取所有可用的模型提供商列表"""
    _refresh_runtime_config()
    return list(AGENT_CONFIG.keys())
