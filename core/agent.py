"""
智能体核心模块
实现谋策智能体的主要功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Any
from openai import OpenAI
from config.agent_config import get_config, AGENT_INFO
from core.knowledge_base import get_system_prompt
from core.analysis_templates import build_analysis_prompt


class StrategyAgent:
    """
    谋策智能体核心类

    基于中国传统谋略与毛泽东思想提供决策分析
    """

    def __init__(self, provider: Optional[str] = None):
        """
        初始化智能体

        Args:
            provider: 模型提供商，可选 glm4/kimi/minimax，默认使用环境变量配置
        """
        self.provider = provider
        self.config = get_config(provider)
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化OpenAI兼容客户端"""
        try:
            self.client = OpenAI(
                api_key=self.config["api_key"],
                base_url=self.config["base_url"],
                timeout=self.config["timeout"],
            )
        except Exception as e:
            raise RuntimeError(f"初始化API客户端失败: {str(e)}")

    def analyze(self, question: str, scene_type: Optional[str] = None) -> Dict[str, Any]:
        """
        执行谋略分析

        Args:
            question: 用户决策问题
            scene_type: 场景类型（通用决策/创业决策/职场决策/投资决策）

        Returns:
            分析结果字典，包含：
            - success: 是否成功
            - content: 分析内容（成功时）
            - error: 错误信息（失败时）
            - model: 使用的模型
            - tokens: token消耗信息
        """
        if not question or not question.strip():
            return {
                "success": False,
                "error": "问题不能为空",
                "content": None,
                "model": None,
                "tokens": None,
            }

        # 构建完整提示词
        system_prompt = get_system_prompt()
        user_prompt = build_analysis_prompt(question, scene_type or "通用决策")

        try:
            # 调用API
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config["temperature"],
            )

            # 提取结果
            content = response.choices[0].message.content
            usage = response.usage

            return {
                "success": True,
                "content": content,
                "error": None,
                "model": self.config["model"],
                "tokens": {
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "total": usage.total_tokens,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"API调用失败: {str(e)}",
                "content": None,
                "model": self.config["model"],
                "tokens": None,
            }

    def quick_analyze(self, question: str, scene_type: Optional[str] = None) -> str:
        """
        快速分析，直接返回结果字符串

        Args:
            question: 用户决策问题
            scene_type: 场景类型

        Returns:
            分析结果字符串或错误信息
        """
        result = self.analyze(question, scene_type)
        if result["success"]:
            return result["content"]
        else:
            return f"分析失败: {result['error']}"

    def get_agent_info(self) -> Dict[str, str]:
        """获取智能体信息"""
        return {
            **AGENT_INFO,
            "current_provider": self.provider or "default",
            "current_model": self.config["model"],
        }


# ============================================
# 便捷函数
# ============================================

def create_agent(provider: Optional[str] = None) -> StrategyAgent:
    """
    创建智能体实例的便捷函数

    Args:
        provider: 模型提供商

    Returns:
        StrategyAgent实例
    """
    return StrategyAgent(provider)


def quick_analyze(question: str, scene_type: Optional[str] = None, provider: Optional[str] = None) -> str:
    """
    快速分析的便捷函数

    Args:
        question: 用户决策问题
        scene_type: 场景类型
        provider: 模型提供商

    Returns:
        分析结果字符串
    """
    agent = create_agent(provider)
    return agent.quick_analyze(question, scene_type)


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    # 简单测试
    print("=" * 60)
    print("谋策智能体测试")
    print("=" * 60)

    try:
        agent = create_agent()
        info = agent.get_agent_info()
        print(f"\n智能体: {info['name']}")
        print(f"版本: {info['version']}")
        print(f"当前模型: {info['current_model']}")
        print(f"\n{info['description']}\n")

        # 测试问题
        test_question = "面临竞品价格战，我方资金有限该如何反击？"
        print(f"\n测试问题: {test_question}")
        print("-" * 60)

        result = agent.analyze(test_question)
        if result["success"]:
            print("分析成功！")
            print(f"模型: {result['model']}")
            print(f"Token消耗: {result['tokens']['total']} (提示: {result['tokens']['prompt']}, 输出: {result['tokens']['completion']})")
            print("\n分析结果预览:")
            print(result["content"][:500] + "...")
        else:
            print(f"分析失败: {result['error']}")

    except Exception as e:
        print(f"初始化失败: {str(e)}")
        print("\n请确保:")
        print("1. 已创建 .env 文件并配置 API Key")
        print("2. 已安装依赖: pip install -r requirements.txt")
