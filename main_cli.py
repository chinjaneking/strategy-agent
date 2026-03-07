#!/usr/bin/env python3
"""
命令行界面入口
提供交互式命令行界面使用谋策智能体
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import StrategyAgent
from core.analysis_templates import get_all_scene_types, SCENE_SELECTION_GUIDE
from utils.file_utils import save_analysis_result, list_saved_results


def print_banner():
    """打印欢迎横幅"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███╗   ███╗ ██████╗ ██╗   ██╗     ██████╗███████╗        ║
║   ████╗ ████║██╔═══██╗██║   ██║    ██╔════╝██╔════╝        ║
║   ██╔████╔██║██║   ██║██║   ██║    ██║     █████╗          ║
║   ██║╚██╔╝██║██║   ██║██║   ██║    ██║     ██╔══╝          ║
║   ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝    ╚██████╗██║             ║
║   ╚═╝     ╚═╝ ╚═════╝  ╚═════╝      ╚═════╝╚═╝             ║
║                                                               ║
║        Strategy Agent V2.0 - 谋策智能体                      ║
║        基于中国传统谋略与毛泽东思想的决策分析                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_menu():
    """打印主菜单"""
    print("\n【主菜单】")
    print("-" * 50)
    print("1. 开始决策分析")
    print("2. 查看历史记录")
    print("3. 关于谋策智能体")
    print("0. 退出程序")
    print("-" * 50)


def select_scene() -> str:
    """选择场景类型"""
    scenes = get_all_scene_types()

    print("\n【场景选择】")
    print(SCENE_SELECTION_GUIDE)

    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene}")
    print("0. 返回主菜单")

    while True:
        try:
            choice = input("\n请选择场景编号: ").strip()
            if choice == "0":
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(scenes):
                return scenes[idx]
            else:
                print("无效选择，请重新输入")
        except ValueError:
            print("请输入数字")


def input_question() -> str:
    """输入决策问题"""
    print("\n【输入决策问题】")
    print("提示: 请清晰描述你面临的决策情境，越详细越好")
    print("示例: '面临竞品价格战，我方资金有限该如何反击？'")
    print("输入 'cancel' 取消")
    print("-" * 50)

    lines = []
    while True:
        try:
            line = input("> ")
            if line.strip().lower() == "cancel":
                return None
            if line.strip() == "" and lines:
                break
            lines.append(line)
        except EOFError:
            break

    question = "\n".join(lines).strip()
    return question if question else None


def perform_analysis(agent: StrategyAgent, question: str, scene_type: str):
    """执行分析并显示结果"""
    print("\n" + "=" * 50)
    print("正在分析中，请稍候...")
    print("=" * 50)

    result = agent.analyze(question, scene_type)

    if result["success"]:
        print("\n✓ 分析完成！")
        print(f"模型: {result['model']}")
        print(f"Token消耗: {result['tokens']['total']}")
        print("\n" + "=" * 50)
        print("【分析结果】")
        print("=" * 50)
        print(result["content"])
        print("=" * 50)

        # 询问是否保存
        save_choice = input("\n是否保存分析结果？(y/n): ").strip().lower()
        if save_choice in ("y", "yes"):
            filepath = save_analysis_result(result, question)
            if filepath:
                print(f"✓ 已保存到: {filepath}")
            else:
                print("✗ 保存失败")

        return True
    else:
        print(f"\n✗ 分析失败: {result['error']}")
        return False


def show_history():
    """显示历史记录"""
    print("\n【历史分析记录】")
    print("-" * 50)

    results = list_saved_results()

    if not results:
        print("暂无历史记录")
        return

    for i, item in enumerate(results, 1):
        print(f"{i}. {item['filename']}")
        print(f"   创建时间: {item['created']}")
        print(f"   文件大小: {item['size']} 字节")
        print()

    print("输入编号查看详情，或按 Enter 返回")
    choice = input("> ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            from utils.file_utils import read_saved_result
            content = read_saved_result(results[idx]["path"])
            if content:
                print("\n" + "=" * 50)
                print(content)
                print("=" * 50)
            else:
                print("读取失败")


def show_about(agent: StrategyAgent):
    """显示关于信息"""
    info = agent.get_agent_info()

    print("\n【关于谋策智能体】")
    print("=" * 50)
    print(f"名称: {info['name']}")
    print(f"版本: {info['version']}")
    print(f"作者: {info['author']}")
    print(f"\n{info['description']}")
    print(f"\n当前配置模型: {info['current_model']}")
    print("=" * 50)

    print("\n【核心智慧体系】")
    print("-" * 50)
    print("• 鬼谷子: 捭阖、反应、内楗、抵巇、飞箝、忤合")
    print("• 孙子兵法: 计篇、谋攻、虚实、九变、用间")
    print("• 毛泽东思想: 实事求是、矛盾分析、群众路线、游击战术、持久战")
    print("-" * 50)


def main():
    """主函数"""
    print_banner()

    # 初始化智能体
    try:
        print("正在初始化智能体...")
        agent = StrategyAgent()
        info = agent.get_agent_info()
        print(f"✓ 智能体初始化成功")
        print(f"  当前模型: {info['current_model']}")
    except Exception as e:
        print(f"✗ 初始化失败: {str(e)}")
        print("\n请检查:")
        print("1. 是否已创建 .env.local（推荐）或 .env，并配置 API Key")
        print("2. 是否已安装依赖: pip install -r requirements.txt")
        input("\n按 Enter 退出...")
        return

    # 主循环
    while True:
        print_menu()
        choice = input("请选择: ").strip()

        if choice == "0":
            print("\n感谢使用谋策智能体，再见！")
            break

        elif choice == "1":
            # 开始决策分析
            scene_type = select_scene()
            if scene_type is None:
                continue

            question = input_question()
            if question is None:
                continue

            perform_analysis(agent, question, scene_type)
            input("\n按 Enter 继续...")

        elif choice == "2":
            # 查看历史记录
            show_history()
            input("\n按 Enter 继续...")

        elif choice == "3":
            # 关于
            show_about(agent)
            input("\n按 Enter 继续...")

        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        sys.exit(1)
