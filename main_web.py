#!/usr/bin/env python3
"""
Web界面入口
基于Streamlit的谋策智能体可视化界面
"""

import streamlit as st
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import StrategyAgent, AGENT_INFO
from core.analysis_templates import get_all_scene_types, SCENE_SELECTION_GUIDE
from utils.file_utils import save_analysis_result, read_uploaded_file, format_file_context


# ============================================
# 页面配置
# ============================================

st.set_page_config(
    page_title="谋策智能体 Strategy Agent V2.0",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================
# 会话状态初始化
# ============================================

def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agent" not in st.session_state:
        try:
            st.session_state.agent = StrategyAgent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.agent = None
            st.session_state.agent_ready = False
            st.session_state.agent_error = str(e)

    if "current_scene" not in st.session_state:
        st.session_state.current_scene = "通用决策"


# ============================================
# UI组件
# ============================================

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("🎯 谋策智能体")
        st.subheader("Strategy Agent V2.0")

        st.markdown("---")

        # 场景选择
        st.markdown("### 📋 场景选择")

        scenes = get_all_scene_types()
        scene = st.radio(
            "选择决策场景:",
            options=scenes,
            index=scenes.index(st.session_state.current_scene),
            help="不同场景使用不同的分析框架",
        )
        st.session_state.current_scene = scene

        # 场景说明
        scene_descriptions = {
            "通用决策": "适用于各类通用决策场景，提供通用分析框架",
            "创业决策": "针对创业者，侧重市场验证、融资策略、增长路径",
            "职场决策": "针对职场人士，侧重职业发展与人际博弈",
            "投资决策": "针对投资理财，侧重风险收益与资金配置",
            "婚恋决策": "针对恋爱婚姻，侧重双方匹配与长期关系",
            "教育决策": "针对学业规划，侧重投资回报与职业发展",
        }
        st.info(scene_descriptions.get(scene, ""))

        st.markdown("---")

        # 模型信息
        st.markdown("### 🤖 模型信息")
        if st.session_state.agent_ready:
            info = st.session_state.agent.get_agent_info()
            st.success(f"✓ {info['current_model']}")
        else:
            st.error("✗ 模型未就绪")
            st.text(st.session_state.get("agent_error", "未知错误"))

        st.markdown("---")

        # 关于
        with st.expander("ℹ️ 关于谋策智能体"):
            st.markdown("""
            **谋策智能体**融合三大智慧体系：

            📜 **鬼谷子**
            - 捭阖、反应、内楗
            - 抵巇、飞箝、忤合

            ⚔️ **孙子兵法**
            - 计篇、谋攻、虚实
            - 九变、用间

            🚩 **毛泽东思想**
            - 实事求是、矛盾分析
            - 群众路线、持久战

            ---
            基于六步分析框架提供决策建议
            """)

        # 清除对话按钮
        if st.button("🗑️ 清除对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_header():
    """渲染页面头部"""
    st.title("🎯 谋策智能体")
    st.caption("基于中国传统谋略与毛泽东思想的高级决策分析AI")

    # 模型状态提示
    if not st.session_state.agent_ready:
        st.error("""
        ⚠️ **智能体初始化失败**

        请检查以下配置：
        1. 在项目根目录创建 `.env` 文件
        2. 添加 API Key 配置，例如：
           ```
           GLM4_API_KEY=your_api_key_here
           GLM4_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
           ```
        3. 安装依赖: `pip install -r requirements.txt`
        """)
        return False

    return True


def render_chat():
    """渲染聊天界面"""
    st.markdown("### 💬 决策咨询")

    # 显示历史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # 显示保存按钮（仅针对助手消息）
            if message["role"] == "assistant" and "question" in message:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("💾 保存", key=f"save_{message.get('id', 0)}"):
                        result = {
                            "success": True,
                            "content": message["content"],
                            "model": message.get("model", "unknown"),
                            "tokens": message.get("tokens", {"total": 0}),
                        }
                        filepath = save_analysis_result(result, message["question"])
                        if filepath:
                            st.success(f"已保存: {os.path.basename(filepath)}")
                        else:
                            st.error("保存失败")


def render_file_uploader():
    """渲染文件上传组件"""
    st.markdown("### 📎 文件上传")

    uploaded_file = st.file_uploader(
        "上传文件进行分析（支持 .txt, .md, .pdf, .docx）",
        type=['txt', 'md', 'pdf', 'docx'],
        help="上传相关文档辅助决策分析，最大10MB",
    )

    if uploaded_file:
        file_info = read_uploaded_file(uploaded_file)

        if file_info["success"]:
            st.success(f"✓ 已加载: {file_info['filename']} ({file_info['size']} bytes)")
            st.session_state.uploaded_file_info = file_info
        else:
            st.error(f"✗ {file_info['error']}")
            st.session_state.uploaded_file_info = None
    else:
        st.session_state.uploaded_file_info = None


def handle_user_input():
    """处理用户输入"""
    if not st.session_state.agent_ready:
        return

    # 文件上传区域
    with st.expander("📎 文件上传（可选）"):
        uploaded_file = st.file_uploader(
            "上传相关文档辅助分析（.txt, .md, .pdf, .docx, .csv）",
            type=['txt', 'md', 'pdf', 'docx', 'csv'],
            key="file_uploader",
        )

        file_context = None
        if uploaded_file:
            with st.spinner("正在读取文件..."):
                file_info = read_uploaded_file(uploaded_file)

            if file_info["success"]:
                st.success(f"✓ 已加载: {file_info['filename']} ({file_info['size']:,} bytes)")
                file_context = format_file_context(file_info, max_length=8000)
            else:
                st.error(f"✗ 读取失败: {file_info['error']}")

    # 聊天输入
    prompt = st.chat_input("请描述你面临的决策问题...")

    if prompt:
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 执行分析
        with st.chat_message("assistant"):
            with st.spinner("正在运用鬼谷子、孙子兵法、毛泽东思想进行深度分析..."):
                result = st.session_state.agent.analyze(
                    prompt,
                    st.session_state.current_scene,
                    file_context=file_context
                )

            if result["success"]:
                # 显示分析结果
                st.markdown(result["content"])

                # 显示元信息
                with st.expander("📊 分析详情"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**模型**: {result['model']}")
                    with col2:
                        tokens = result['tokens']
                        st.markdown(f"**Token**: 提示 {tokens['prompt']} / 输出 {tokens['completion']} / 总计 {tokens['total']}")
                    with col3:
                        if result.get("history_summary"):
                            summary = result["history_summary"]
                            st.markdown(f"**对话**: {summary['turn_count']}轮")

                # 添加到历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["content"],
                    "question": prompt,
                    "model": result["model"],
                    "tokens": result["tokens"],
                    "id": len(st.session_state.messages),
                })

                # 保存按钮
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("💾 保存分析结果", key=f"save_result_{len(st.session_state.messages)}"):
                        filepath = save_analysis_result(result, prompt)
                        if filepath:
                            st.success(f"✓ 已保存: {os.path.basename(filepath)}")
                        else:
                            st.error("✗ 保存失败")
            else:
                error_msg = f"**分析失败**: {result['error']}"
                st.error(error_msg)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "question": prompt,
                    "model": result.get("model", "unknown"),
                    "tokens": {},
                    "id": len(st.session_state.messages),
                })


def render_quick_start():
    """渲染快速开始区域"""
    if len(st.session_state.messages) == 0:
        st.markdown("### 🚀 快速开始")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **💼 职场示例**
            > 面临两个offer选择，一个是稳定的大厂，一个是高风险的创业公司，该如何决策？
            """)
            if st.button("使用此示例", key="example1"):
                st.session_state.example_input = "面临两个offer选择，一个是稳定的大厂，一个是高风险的创业公司，该如何决策？"
                st.rerun()

        with col2:
            st.markdown("""
            **🏢 创业示例**
            > 竞品突然发起价格战，我方资金有限，该如何应对？
            """)
            if st.button("使用此示例", key="example2"):
                st.session_state.example_input = "竞品突然发起价格战，我方资金有限，该如何应对？"
                st.rerun()

        with col3:
            st.markdown("""
            **📈 投资示例**
            > 手上有50万现金，当前股市低迷，是否适合入场？
            """)
            if st.button("使用此示例", key="example3"):
                st.session_state.example_input = "手上有50万现金，当前股市低迷，是否适合入场？"
                st.rerun()

        # 如果有示例输入，填充到聊天框（通过session_state传递到handle_user_input）
        if "example_input" in st.session_state:
            prompt = st.session_state.example_input
            del st.session_state.example_input

            # 直接处理示例输入
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
            })
            st.rerun()


# ============================================
# 主函数
# ============================================

def main():
    """主函数"""
    # 初始化会话状态
    init_session_state()

    # 渲染侧边栏
    render_sidebar()

    # 渲染主内容
    if render_header():
        render_quick_start()
        render_chat()
        handle_user_input()


if __name__ == "__main__":
    main()
