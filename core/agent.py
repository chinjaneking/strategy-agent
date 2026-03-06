"""
智能体核心模块 (V2.2)
实现谋策智能体的主要功能
支持多轮对话上下文记忆
集成质量检查、日志系统、统一错误处理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Dict, Any, List
from openai import OpenAI
from config.agent_config import get_config, AGENT_INFO
from core.knowledge_base import get_system_prompt
from core.analysis_templates import build_analysis_prompt
from utils.file_utils import format_file_context
from core.dynamic_knowledge import DynamicKnowledgeBase
from core.quality_checker import QualityChecker
from utils.logger import get_logger
from utils.error_handler import handle_api_error, StrategyAgentException


class StrategyAgent:
    """
    谋策智能体核心类

    基于中国传统谋略与毛泽东思想提供决策分析
    支持多轮对话上下文记忆
    """

    # 默认上下文窗口限制
    DEFAULT_MAX_CONTEXT_TOKENS = 8000
    # 保留的系统消息和最近对话的token预留
    TOKEN_RESERVE = 4000

    def __init__(self, provider: Optional[str] = None, max_context_tokens: int = None):
        """
        初始化智能体

        Args:
            provider: 模型提供商，可选 glm4/kimi/minimax，默认使用环境变量配置
            max_context_tokens: 最大上下文token数，默认8000
        """
        self.provider = provider
        self.config = get_config(provider)
        self.client = None
        self._init_client()

        # 对话历史存储
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_tokens = max_context_tokens or self.DEFAULT_MAX_CONTEXT_TOKENS
        
        # 独立智慧库
        self.knowledge_base = DynamicKnowledgeBase()

        # V2.2 新增：质量检查器和日志
        self.quality_checker = QualityChecker()
        self.logger = get_logger()
        self.enable_quality_check = True

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

    def _build_messages(self, question: str, scene_type: Optional[str] = None,
                       use_history: bool = True) -> List[Dict[str, str]]:
        """
        构建完整的消息列表（包含上下文历史）

        Args:
            question: 当前用户问题
            scene_type: 场景类型
            use_history: 是否使用对话历史

        Returns:
            消息列表
        """
        system_prompt = get_system_prompt()
        user_prompt = build_analysis_prompt(question, scene_type or "通用决策")

        # 动态获取历史复盘智慧，增强当前推演能力
        dynamic_wisdom = self.knowledge_base.get_relevant_wisdom(question)
        if dynamic_wisdom:
            user_prompt = f"{dynamic_wisdom}\n\n当前面临的新决策问题：\n{user_prompt}"

        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话（如果启用）
        if use_history and self.conversation_history:
            messages.extend(self.conversation_history)

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_prompt})

        return messages

    def _manage_context_window(self):
        """
        管理上下文窗口，防止超出token限制
        策略：保留最近的对话，移除较早的
        """
        # 简单的启发式策略：限制历史消息对数（每对约500-1000 tokens）
        max_history_pairs = 6  # 最多保留6轮对话（12条消息）

        # 计算当前历史消息数（排除系统消息的后续消息）
        history_count = len(self.conversation_history)

        if history_count > max_history_pairs * 2:
            # 移除最早的消息对，保留最近的
            excess = history_count - max_history_pairs * 2
            self.conversation_history = self.conversation_history[excess:]

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []

    def get_history_summary(self) -> Dict[str, Any]:
        """
        获取对话历史摘要

        Returns:
            包含轮数、token估算等信息的字典
        """
        message_count = len(self.conversation_history)
        turn_count = message_count // 2  # 每轮包含用户+助手两条消息

        # 粗略估算token数（中文约1.5字符/token）
        total_chars = sum(len(m.get("content", "")) for m in self.conversation_history)
        estimated_tokens = int(total_chars / 1.5)

        return {
            "turn_count": turn_count,
            "message_count": message_count,
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.max_context_tokens,
        }

    def analyze(self, question: str, scene_type: Optional[str] = None,
                use_history: bool = True, save_to_history: bool = True,
                file_context: Optional[str] = None) -> Dict[str, Any]:
        """
        执行谋略分析

        Args:
            question: 用户决策问题
            scene_type: 场景类型（通用决策/创业决策/职场决策/投资决策/婚恋决策/教育决策）
            use_history: 是否使用对话历史作为上下文
            save_to_history: 是否将本次对话保存到历史
            file_context: 文件上下文内容（如上传的文件）

        Returns:
            分析结果字典，包含：
            - success: 是否成功
            - content: 分析内容（成功时）
            - error: 错误信息（失败时）
            - model: 使用的模型
            - tokens: token消耗信息
            - history_summary: 对话历史摘要（save_to_history为True时）
        """
        if not question or not question.strip():
            return {
                "success": False,
                "error": "问题不能为空",
                "content": None,
                "model": None,
                "tokens": None,
                "history_summary": None,
            }

        # 合并文件上下文到问题
        if file_context:
            question = f"{file_context}\n\n用户问题：{question}"

        # 构建消息列表
        messages = self._build_messages(question, scene_type, use_history)

        try:
            # 调用API
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=self.config["temperature"],
            )

            # 提取结果
            content = response.choices[0].message.content
            usage = response.usage

            # 保存到对话历史（如果启用）
            if save_to_history:
                user_prompt = build_analysis_prompt(question, scene_type or "通用决策")
                self.conversation_history.append({"role": "user", "content": user_prompt})
                self.conversation_history.append({"role": "assistant", "content": content})
                self._manage_context_window()

            tokens_info = {
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
                "total": usage.total_tokens,
            }

            # V2.2: 质量检查
            quality_report = None
            if self.enable_quality_check:
                quality_report = self.quality_checker.check_all(content)
                self.logger.log_quality_check(
                    quality_report["score"], quality_report["grade"],
                    quality_report["passed"], quality_report["total"]
                )

            # V2.2: 日志记录
            self.logger.log_analysis(
                question=question[:100],
                scene_type=scene_type or "通用决策",
                tokens=tokens_info,
            )

            result = {
                "success": True,
                "content": content,
                "error": None,
                "model": self.config["model"],
                "tokens": tokens_info,
                "history_summary": self.get_history_summary() if save_to_history else None,
                "quality_report": quality_report,
            }

            return result

        except StrategyAgentException as e:
            self.logger.log_error(str(e), context="analyze")
            return {
                "success": False,
                "error": e.message,
                "content": None,
                "model": self.config["model"],
                "tokens": None,
                "history_summary": None,
                "quality_report": None,
            }
        except Exception as e:
            agent_error = handle_api_error(e)
            self.logger.log_error(str(e), context="analyze")
            return {
                "success": False,
                "error": agent_error.message,
                "content": None,
                "model": self.config["model"],
                "tokens": None,
                "history_summary": None,
                "quality_report": None,
            }

    def quick_analyze(self, question: str, scene_type: Optional[str] = None,
                     use_history: bool = True) -> str:
        """
        快速分析，直接返回结果字符串

        Args:
            question: 用户决策问题
            scene_type: 场景类型
            use_history: 是否使用对话历史

        Returns:
            分析结果字符串或错误信息
        """
        result = self.analyze(question, scene_type, use_history=use_history)
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
        
    def learn_from_feedback(self, original_question: str, action_taken: str, final_result: str) -> Dict[str, Any]:
        """
        基于真实复盘结果进行动态学习，提炼经验储存于独立智慧库
        
        Args:
            original_question: 原核心决策问题
            action_taken: 实际采取的行动策略
            final_result: 现实世界中的反馈与最终结果（成功/失败及原因）
            
        Returns:
            Dict: 包含学习状态及提炼智慧的结果
        """
        feedback_prompt = f"""
请你作为高级战略复盘专家，对以下真实决策案例进行深度复盘：

【原决策问题】：{original_question}
【实际采取的行动】：{action_taken}
【现实世界反馈结果】：{final_result}

请结合鬼谷子、孙子兵法或毛泽东思想，分析为何会产生这样的结果，并提炼出 1到2 条核心“实战智慧教训”。
要求：
1. 语言高度凝练，直击要害。
2. 以“【实战规则】XXX：因为YYY，以后遇到ZZZ情况，应当WWW。”的结构输出。
3. 必须对未来的类似问题有明确的指导意义，切忌正确的废话。
        """

        messages = [
            {"role": "system", "content": "你是冷酷、理性的战略复盘讲师，只提取最核心的战术规律。"},
            {"role": "user", "content": feedback_prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=0.3, # 复盘总结需要客观稳定
            )
            extracted_wisdom = response.choices[0].message.content.strip()

            # 将提炼的智慧存入独立智慧库
            wisdom_id = self.knowledge_base.add_wisdom(
                original_question=original_question,
                action_taken=action_taken,
                final_result=final_result,
                extracted_wisdom=extracted_wisdom,
                tags=["复盘总结"]
            )

            return {
                "success": True,
                "wisdom_id": wisdom_id,
                "extracted_wisdom": extracted_wisdom
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"复盘学习失败: {str(e)}",
                "extracted_wisdom": ""
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
    快速分析的便捷函数（无上下文记忆）

    Args:
        question: 用户决策问题
        scene_type: 场景类型
        provider: 模型提供商

    Returns:
        分析结果字符串
    """
    agent = create_agent(provider)
    return agent.quick_analyze(question, scene_type, use_history=False)


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
            if result.get("history_summary"):
                summary = result["history_summary"]
                print(f"对话历史: {summary['turn_count']}轮 ({summary['estimated_tokens']} tokens)")
            print("\n分析结果预览:")
            print(result["content"][:500] + "...")
        else:
            print(f"分析失败: {result['error']}")

    except Exception as e:
        print(f"初始化失败: {str(e)}")
        print("\n请确保:")
        print("1. 已创建 .env 文件并配置 API Key")
        print("2. 已安装依赖: pip install -r requirements.txt")
