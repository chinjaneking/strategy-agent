"""
文件工具模块
用于保存分析结果到文件
"""

import os
import re
from datetime import datetime
from typing import Optional, Dict, Any


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename.strip()


def generate_filename(question: str, extension: str = "md") -> str:
    """
    根据问题生成文件名

    Args:
        question: 分析问题
        extension: 文件扩展名

    Returns:
        生成的文件名
    """
    # 提取问题的前20个字符作为文件名主体
    title = question[:20] if len(question) <= 20 else question[:20] + "..."
    title = sanitize_filename(title)

    # 添加时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{timestamp}_{title}.{extension}"


def format_analysis_result(result: Dict[str, Any], question: str) -> str:
    """
    将分析结果格式化为Markdown文档

    Args:
        result: 分析结果字典
        question: 原始问题

    Returns:
        Markdown格式的文档内容
    """
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

    if not result.get("success"):
        return f"""# 分析失败

**时间**: {timestamp}

**问题**: {question}

**错误信息**: {result.get('error', '未知错误')}
"""

    content = f"""# 谋策智能体分析报告

---

**分析时间**: {timestamp}
**分析模型**: {result.get('model', '未知')}
**Token消耗**: {result.get('tokens', {}).get('total', '未知')}
(提示: {result.get('tokens', {}).get('prompt', '未知')}, 输出: {result.get('tokens', {}).get('completion', '未知')})

---

## 决策问题

{question}

---

## 分析结果

{result.get('content', '无内容')}

---

*本报告由谋策智能体 Strategy Agent V2.0 生成*
"""

    return content


def save_analysis_result(
    result: Dict[str, Any],
    question: str,
    save_dir: Optional[str] = None
) -> Optional[str]:
    """
    保存分析结果到文件

    Args:
        result: 分析结果字典
        question: 原始问题
        save_dir: 保存目录，默认使用 analysis_results/

    Returns:
        保存的文件路径，失败返回None
    """
    # 确定保存目录
    if save_dir is None:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(current_dir, "analysis_results")

    # 确保目录存在
    try:
        os.makedirs(save_dir, exist_ok=True)
    except Exception as e:
        print(f"创建目录失败: {e}")
        return None

    # 生成文件名
    filename = generate_filename(question, "md")
    filepath = os.path.join(save_dir, filename)

    # 格式化内容
    content = format_analysis_result(result, question)

    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        print(f"保存文件失败: {e}")
        return None


def list_saved_results(save_dir: Optional[str] = None) -> list:
    """
    列出已保存的分析结果文件

    Args:
        save_dir: 保存目录

    Returns:
        文件信息列表，每项包含文件名、路径、创建时间
    """
    if save_dir is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_dir = os.path.join(current_dir, "analysis_results")

    if not os.path.exists(save_dir):
        return []

    results = []
    try:
        for filename in sorted(os.listdir(save_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(save_dir, filename)
                stat = os.stat(filepath)
                results.append({
                    "filename": filename,
                    "path": filepath,
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": stat.st_size,
                })
    except Exception as e:
        print(f"列出文件失败: {e}")

    return results


def read_saved_result(filepath: str) -> Optional[str]:
    """
    读取已保存的分析结果

    Args:
        filepath: 文件路径

    Returns:
        文件内容，失败返回None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


# ============================================
# 便捷函数
# ============================================

def save_quick(content: str, question: str, save_dir: Optional[str] = None) -> Optional[str]:
    """
    快速保存分析内容的便捷函数

    Args:
        content: 分析内容字符串
        question: 原始问题
        save_dir: 保存目录

    Returns:
        保存的文件路径
    """
    result = {
        "success": True,
        "content": content,
        "model": "unknown",
        "tokens": {"total": 0, "prompt": 0, "completion": 0},
    }
    return save_analysis_result(result, question, save_dir)
