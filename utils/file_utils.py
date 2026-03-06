"""
文件工具模块
用于保存分析结果到文件，以及读取上传的文件
"""

import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, Union
from io import BytesIO

# 文件上传支持的最大大小（MB）
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# 支持的文件类型
SUPPORTED_EXTENSIONS = {
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.csv': 'text/csv',
    '.json': 'application/json',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc': 'application/msword',
}


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


# ============================================
# 文件读取功能（用于上传）
# ============================================

def get_file_extension(filename: str) -> str:
    """获取文件扩展名（小写）"""
    return os.path.splitext(filename)[1].lower()


def is_supported_file(filename: str) -> bool:
    """检查文件类型是否支持"""
    ext = get_file_extension(filename)
    return ext in SUPPORTED_EXTENSIONS


def read_text_file(file_content: Union[bytes, str], encoding: str = 'utf-8') -> str:
    """
    读取文本文件内容

    Args:
        file_content: 文件内容（bytes或str）
        encoding: 编码格式

    Returns:
        文件文本内容
    """
    if isinstance(file_content, bytes):
        # 尝试使用指定编码，失败则尝试其他编码
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    return file_content.decode(enc)
                except UnicodeDecodeError:
                    continue
            return file_content.decode('utf-8', errors='ignore')
    return file_content


def read_uploaded_file(uploaded_file) -> Dict[str, Any]:
    """
    读取上传的文件内容

    Args:
        uploaded_file: Streamlit 上传的文件对象

    Returns:
        包含文件名、类型、大小、内容的字典
    """
    if uploaded_file is None:
        return {"success": False, "error": "未上传文件", "content": None}

    filename = uploaded_file.name
    file_size = uploaded_file.size

    # 检查文件大小
    if file_size > MAX_FILE_SIZE_BYTES:
        return {
            "success": False,
            "error": f"文件大小超过限制（最大{MAX_FILE_SIZE_MB}MB）",
            "content": None,
        }

    # 检查文件类型
    if not is_supported_file(filename):
        ext = get_file_extension(filename)
        supported = ', '.join(SUPPORTED_EXTENSIONS.keys())
        return {
            "success": False,
            "error": f"不支持的文件类型: {ext}。支持: {supported}",
            "content": None,
        }

    try:
        # 读取文件内容
        file_bytes = uploaded_file.getvalue()
        ext = get_file_extension(filename)

        # 根据文件类型处理
        if ext in ['.txt', '.md', '.csv', '.json']:
            content = read_text_file(file_bytes)
        elif ext == '.pdf':
            content = read_pdf_file(file_bytes)
        elif ext in ['.docx', '.doc']:
            content = read_docx_file(file_bytes)
        else:
            content = read_text_file(file_bytes)

        return {
            "success": True,
            "filename": filename,
            "size": file_size,
            "type": ext,
            "content": content,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}",
            "content": None,
        }


def read_pdf_file(file_bytes: bytes) -> str:
    """
    读取 PDF 文件内容

    Args:
        file_bytes: PDF 文件字节

    Returns:
        提取的文本内容
    """
    try:
        # 尝试使用 PyPDF2
        import PyPDF2
        from io import BytesIO

        pdf_file = BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text() or "")

        return "\n\n".join(text_parts)

    except ImportError:
        return "[PDF 解析需要安装 PyPDF2: pip install PyPDF2]"
    except Exception as e:
        return f"[PDF 解析失败: {str(e)}]"


def read_docx_file(file_bytes: bytes) -> str:
    """
    读取 Word 文档内容

    Args:
        file_bytes: Word 文件字节

    Returns:
        提取的文本内容
    """
    try:
        # 尝试使用 python-docx
        import docx
        from io import BytesIO

        doc_file = BytesIO(file_bytes)
        doc = docx.Document(doc_file)

        text_parts = []
        for para in doc.paragraphs:
            text_parts.append(para.text)

        return "\n\n".join(text_parts)

    except ImportError:
        return "[Word 解析需要安装 python-docx: pip install python-docx]"
    except Exception as e:
        return f"[Word 解析失败: {str(e)}]"


def truncate_content(content: str, max_chars: int = 50000) -> str:
    """
    截断过长内容，保留开头和结尾

    Args:
        content: 原始内容
        max_chars: 最大字符数

    Returns:
        截断后的内容
    """
    if len(content) <= max_chars:
        return content

    # 保留开头 60% 和结尾 40%
    head_len = int(max_chars * 0.6)
    tail_len = max_chars - head_len

    head = content[:head_len]
    tail = content[-tail_len:]

    return f"{head}\n\n...[内容已截断，共{len(content)}字符]...\n\n{tail}"


def format_file_context(file_info: Dict[str, Any], max_length: int = 10000) -> str:
    """
    格式化文件内容为分析上下文

    Args:
        file_info: 文件信息字典
        max_length: 最大内容长度

    Returns:
        格式化后的上下文字符串
    """
    if not file_info.get("success"):
        return ""

    content = file_info.get("content", "")
    if len(content) > max_length:
        content = truncate_content(content, max_length)

    filename = file_info.get("filename", "未知文件")
    file_type = file_info.get("type", "未知")

    context = f"""## 参考文件: {filename}
**文件类型**: {file_type}
**文件内容**:
```
{content}
```
---
请结合以上文件内容进行分析。
"""
    return context
