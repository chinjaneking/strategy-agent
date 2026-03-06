"""
谋策智能体错误处理模块 (V2.2)
统一的错误分类和友好提示
"""

from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """错误码枚举"""
    API_ERROR = "API_ERROR"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"
    INVALID_INPUT = "INVALID_INPUT"
    AUTH_ERROR = "AUTH_ERROR"
    MODEL_ERROR = "MODEL_ERROR"
    KNOWLEDGE_BASE_ERROR = "KB_ERROR"
    FILE_ERROR = "FILE_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"
    UNKNOWN = "UNKNOWN"


class StrategyAgentException(Exception):
    """谋策智能体自定义异常"""

    def __init__(self, code: ErrorCode, message: str, detail: str = ""):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error_code": self.code.value,
            "message": self.message,
            "detail": self.detail,
        }


# 友好的错误提示映射
ERROR_MESSAGES = {
    ErrorCode.API_ERROR: "AI 模型服务暂时不可用，请稍后重试。",
    ErrorCode.TIMEOUT: "请求超时，可能是问题过于复杂或网络不佳，请缩短问题后重试。",
    ErrorCode.RATE_LIMIT: "请求过于频繁，请等待片刻后再试。",
    ErrorCode.INVALID_INPUT: "输入格式有误，请检查您的问题描述。",
    ErrorCode.AUTH_ERROR: "API 密钥配置有误，请检查 .env 文件中的 API Key 设置。",
    ErrorCode.MODEL_ERROR: "AI 模型返回了异常结果，请换个方式描述问题后重试。",
    ErrorCode.KNOWLEDGE_BASE_ERROR: "知识库加载失败，请检查知识库文件是否完整。",
    ErrorCode.FILE_ERROR: "文件处理失败，请检查文件格式和大小。",
    ErrorCode.CONFIG_ERROR: "配置加载失败，请检查配置文件。",
    ErrorCode.UNKNOWN: "发生了未知错误，请联系技术支持。",
}


def get_friendly_message(code: ErrorCode) -> str:
    """获取用户友好的错误提示"""
    return ERROR_MESSAGES.get(code, ERROR_MESSAGES[ErrorCode.UNKNOWN])


def handle_api_error(error: Exception) -> StrategyAgentException:
    """
    将 API 异常转化为统一的 StrategyAgentException

    Args:
        error: 原始异常

    Returns:
        标准化的 StrategyAgentException
    """
    error_str = str(error).lower()

    if "timeout" in error_str or "timed out" in error_str:
        code = ErrorCode.TIMEOUT
    elif "rate" in error_str and "limit" in error_str:
        code = ErrorCode.RATE_LIMIT
    elif "auth" in error_str or "api_key" in error_str or "unauthorized" in error_str:
        code = ErrorCode.AUTH_ERROR
    elif "model" in error_str or "not found" in error_str:
        code = ErrorCode.MODEL_ERROR
    else:
        code = ErrorCode.API_ERROR

    return StrategyAgentException(
        code=code,
        message=get_friendly_message(code),
        detail=str(error),
    )
