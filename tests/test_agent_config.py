"""
Environment loading regression tests.
"""

from pathlib import Path

from config import agent_config


def clear_provider_env(monkeypatch):
    keys = [
        "DEFAULT_MODEL_PROVIDER",
        "GLM4_API_KEY",
        "GLM4_BASE_URL",
        "GLM4_MODEL",
        "KIMI_API_KEY",
        "KIMI_BASE_URL",
        "KIMI_MODEL",
        "MINIMAX_API_KEY",
        "MINIMAX_BASE_URL",
        "MINIMAX_MODEL",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)


def write_env(path: Path, content: str):
    path.write_text(content.strip() + "\n", encoding="utf-8")


def test_env_local_overrides_env(monkeypatch, tmp_path):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("STRATEGY_AGENT_ENV_DIR", str(tmp_path))

    write_env(
        tmp_path / ".env",
        """
        GLM4_API_KEY=env-key
        GLM4_MODEL=env-model
        DEFAULT_MODEL_PROVIDER=glm4
        """,
    )
    write_env(
        tmp_path / ".env.local",
        """
        GLM4_API_KEY=env-local-key
        GLM4_MODEL=env-local-model
        DEFAULT_MODEL_PROVIDER=glm4
        """,
    )

    agent_config._load_environment()
    config = agent_config.get_config()

    assert config["api_key"] == "env-local-key"
    assert config["model"] == "env-local-model"


def test_env_local_only_is_loaded(monkeypatch, tmp_path):
    clear_provider_env(monkeypatch)
    monkeypatch.setenv("STRATEGY_AGENT_ENV_DIR", str(tmp_path))

    write_env(
        tmp_path / ".env.local",
        """
        GLM4_API_KEY=only-local-key
        GLM4_MODEL=only-local-model
        DEFAULT_MODEL_PROVIDER=glm4
        """,
    )

    agent_config._load_environment()
    config = agent_config.get_config()

    assert config["api_key"] == "only-local-key"
    assert config["model"] == "only-local-model"
