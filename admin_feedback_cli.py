#!/usr/bin/env python3
"""
管理员专属：实战案例复盘与智慧提取工具
用于向独立智慧库（Dynamic Knowledge Base）录入实战反馈，提升智能体能力。
"""

import sys
import os

# 确保能导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import StrategyAgent
from core.dynamic_knowledge import DynamicKnowledgeBase

def main():
    print("=" * 60)
    print("🛡️ 【管理员专属】谋策智能体 - 实战复盘与进化终端")
    print("=" * 60)
    print("利用本工具输入真实商业/职场/生活案例的最终结果。")
    print("大模型将自动复盘提炼智慧，并永久存入独立智慧库，供后续推演调用。")
    print("输入 'quit' 或 'q' 随时退出。\n")
    
    # 尝试初始化 Agent，需要 API Key 等环境配置
    try:
        agent = StrategyAgent()
        knowledge_base = DynamicKnowledgeBase()
    except Exception as e:
        print(f"❌ 智能体初始化失败 (请检查 .env 配置): {e}")
        return

    while True:
        print("\n--- [启动新的复盘分析] ---")
        
        # 1. 原始问题
        original_question = input("\n📝 请输入原决策问题:\n> ").strip()
        if original_question.lower() in ['q', 'quit']:
            break
        if not original_question:
            print("输入不能为空！")
            continue
            
        # 2. 采取的行动
        action_taken = input("\n🏃 请输入你实际采取的动作/方案:\n> ").strip()
        if action_taken.lower() in ['q', 'quit']:
            break
            
        # 3. 真实反馈
        final_result = input("\n📊 请输入该动作带来的真实结果 (成功/失败及细节):\n> ").strip()
        if final_result.lower() in ['q', 'quit']:
            break
            
        print("\n⏳ 正在呼叫谋策智能体进行深度复盘与智慧提炼 (预计 10-20 秒)...")
        
        result = agent.learn_from_feedback(original_question, action_taken, final_result)
        
        if result["success"]:
            print(f"\n✅ 提炼成功！(保存为智慧节点 ID: {result['wisdom_id']})")
            print("==================================================")
            print(f"💡 提炼的实战智慧:\n{result['extracted_wisdom']}")
            print("==================================================")
            print("\n该条智慧已存入本地智慧库。后续遇到类似情境将自动触发提示。")
        else:
            print(f"\n❌ 复盘学习失败: {result['error']}")

        print("\n" + "=" * 60)
        
        # 询问是否查看当前库数量
        wisdoms = knowledge_base.get_all_wisdoms()
        print(f"📚 当前独立智慧库共收录了 {len(wisdoms)} 条实战经验。")

if __name__ == "__main__":
    main()
