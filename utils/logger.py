"""
谋策智能体日志系统 (V2.2)
统一的日志记录模块
"""

import os
import logging
from datetime import datetime


class StrategyLogger:
    """
    智能体日志管理器

    提供统一的日志记录接口，输出到文件和控制台。
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_dir: str = None, log_level: str = "INFO"):
        if self._initialized:
            return

        # 设置日志目录
        if log_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(base_dir, "logs")

        os.makedirs(log_dir, exist_ok=True)

        # 日志文件路径
        log_file = os.path.join(log_dir, "strategy_agent.log")

        # 配置 logger
        self.logger = logging.getLogger("strategy_agent")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # 避免重复添加 handler
        if not self.logger.handlers:
            # 文件 handler
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # 控制台 handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter("%(levelname)s: %(message)s")
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        self._initialized = True

    def log_analysis(self, question: str, scene_type: str, tokens: dict = None):
        """记录分析请求"""
        token_info = ""
        if tokens:
            token_info = f" | tokens={{prompt:{tokens.get('prompt', '?')}, completion:{tokens.get('completion', '?')}, total:{tokens.get('total', '?')}}}"
        self.logger.info(f"[分析] 场景={scene_type} | 问题={question[:80]}...{token_info}")

    def log_error(self, error: str, context: str = ""):
        """记录错误"""
        ctx = f" | 上下文={context}" if context else ""
        self.logger.error(f"[错误] {error}{ctx}")

    def log_wisdom_added(self, wisdom_id: str, category: str = ""):
        """记录智慧新增"""
        cat = f" | 分类={category}" if category else ""
        self.logger.info(f"[智慧库] 新增智慧 ID={wisdom_id}{cat}")

    def log_quality_check(self, score: int, grade: str, passed: int, total: int):
        """记录质量检查结果"""
        self.logger.info(f"[质检] 评分={score}分({grade}级) 通过={passed}/{total}")

    def info(self, message: str):
        """通用 info 日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """通用 warning 日志"""
        self.logger.warning(message)

    def debug(self, message: str):
        """通用 debug 日志"""
        self.logger.debug(message)


# 全局日志实例
def get_logger(log_level: str = "INFO") -> StrategyLogger:
    """获取全局日志实例"""
    return StrategyLogger(log_level=log_level)
