"""
配置管理和错误处理测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from config.settings import Settings, get_settings
from utils.error_handler import (
    ErrorCode,
    StrategyAgentException,
    get_friendly_message,
    handle_api_error,
)
from utils.logger import StrategyLogger, get_logger


class TestSettings:
    """配置管理测试"""

    def test_default_values(self):
        """默认配置值应正确"""
        settings = Settings()
        assert settings.default_model_provider == "glm4"
        assert settings.max_context_tokens == 8000
        assert settings.log_level == "INFO"
        assert settings.enable_quality_check is True
        assert settings.agent_version == "2.2.0"

    def test_get_settings_singleton(self):
        """get_settings应返回一致的实例"""
        s1 = get_settings()
        s2 = get_settings()
        assert s1.agent_version == s2.agent_version


class TestErrorHandler:
    """错误处理测试"""

    def test_all_error_codes_have_messages(self):
        """每个错误码都应有友好提示"""
        for code in ErrorCode:
            msg = get_friendly_message(code)
            assert msg is not None
            assert len(msg) > 0

    def test_strategy_agent_exception(self):
        """自定义异常应正常工作"""
        ex = StrategyAgentException(
            code=ErrorCode.API_ERROR,
            message="测试错误",
            detail="详细信息",
        )
        assert ex.code == ErrorCode.API_ERROR
        assert ex.message == "测试错误"
        assert ex.detail == "详细信息"

    def test_exception_to_dict(self):
        """异常应能转为字典"""
        ex = StrategyAgentException(
            code=ErrorCode.TIMEOUT,
            message="超时",
        )
        d = ex.to_dict()
        assert d["error_code"] == "TIMEOUT"
        assert d["message"] == "超时"

    def test_handle_timeout_error(self):
        """超时异常应被正确分类"""
        error = Exception("Connection timed out after 120s")
        result = handle_api_error(error)
        assert result.code == ErrorCode.TIMEOUT

    def test_handle_rate_limit_error(self):
        """限流异常应被正确分类"""
        error = Exception("Rate limit exceeded")
        result = handle_api_error(error)
        assert result.code == ErrorCode.RATE_LIMIT

    def test_handle_auth_error(self):
        """认证异常应被正确分类"""
        error = Exception("Unauthorized: invalid api_key")
        result = handle_api_error(error)
        assert result.code == ErrorCode.AUTH_ERROR

    def test_handle_generic_error(self):
        """通用异常应归为API_ERROR"""
        error = Exception("Something went wrong")
        result = handle_api_error(error)
        assert result.code == ErrorCode.API_ERROR


class TestLogger:
    """日志系统测试"""

    def test_logger_singleton(self):
        """日志应为单例"""
        # 重置单例以便测试
        StrategyLogger._instance = None
        StrategyLogger._instance = None
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2

    def test_logger_methods_exist(self):
        """日志实例应有所需方法"""
        StrategyLogger._instance = None
        logger = get_logger()
        assert hasattr(logger, "log_analysis")
        assert hasattr(logger, "log_error")
        assert hasattr(logger, "log_wisdom_added")
        assert hasattr(logger, "log_quality_check")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")

    def test_log_analysis_no_error(self):
        """记录分析日志应不出错"""
        StrategyLogger._instance = None
        logger = get_logger()
        # 不应抛出异常
        logger.log_analysis("测试问题", "通用决策", {"prompt": 100, "completion": 200, "total": 300})

    def test_log_error_no_error(self):
        """记录错误日志应不出错"""
        StrategyLogger._instance = None
        logger = get_logger()
        logger.log_error("测试错误", context="test")
