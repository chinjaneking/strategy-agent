"""
动态智慧库模块 (Dynamic Knowledge Base)
用于持久化存储从真实案例复盘中提取的决策经验

支持独立知识库：如果安装了 strategy-knowledge-base 包，则使用独立智慧库
"""
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# 尝试导入独立知识库
try:
    from strategy_knowledge import WisdomManager
    _USE_EXTERNAL_WISDOM = True
except ImportError:
    # 尝试从相对路径导入
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    knowledge_base_path = os.path.join(parent_dir, 'strategy-knowledge-base')
    if os.path.exists(knowledge_base_path):
        sys.path.insert(0, knowledge_base_path)
        try:
            from strategy_knowledge import WisdomManager
            _USE_EXTERNAL_WISDOM = True
        except ImportError:
            _USE_EXTERNAL_WISDOM = False
    else:
        _USE_EXTERNAL_WISDOM = False


class DynamicKnowledgeBase:
    def __init__(self, data_dir: str = None):
        # 如果使用独立知识库，则使用 WisdomManager
        self._use_external = _USE_EXTERNAL_WISDOM
        if self._use_external:
            self._wm = WisdomManager(data_dir)
            return

        # 否则使用本地存储
        if data_dir is None:
            # 默认保存在项目根目录的 data 文件夹下
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.file_path = os.path.join(self.data_dir, "wisdom_library.json")
        self._init_file()
        
    def _init_file(self):
        """初始化智慧库文件"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"wisdoms": []}, f, ensure_ascii=False, indent=4)
                
    def _load_data(self) -> Dict[str, Any]:
        """加载智慧库数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取智慧库失败: {e}")
            return {"wisdoms": []}
            
    def _save_data(self, data: Dict[str, Any]):
        """保存数据到智慧库"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"写入智慧库失败: {e}")

    def add_wisdom(self, original_question: str, action_taken: str, final_result: str, extracted_wisdom: str, tags: List[str] = None):
        """
        添加一条新的实战智慧
        """
        if self._use_external:
            return self._wm.add_wisdom(
                original_question=original_question,
                action_taken=action_taken,
                final_result=final_result,
                extracted_wisdom=extracted_wisdom,
                tags=tags
            )

        data = self._load_data()

        new_entry = {
            "id": len(data["wisdoms"]) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_question": original_question,
            "action_taken": action_taken,
            "final_result": final_result,
            "extracted_wisdom": extracted_wisdom,
            "tags": tags or []
        }

        data["wisdoms"].append(new_entry)
        self._save_data(data)
        return str(new_entry["id"])

    def get_all_wisdoms(self) -> List[Dict[str, Any]]:
        """获取所有智慧条目"""
        if self._use_external:
            return self._wm.get_all_wisdoms()
        return self._load_data().get("wisdoms", [])

    def get_relevant_wisdom(self, question: str, limit: int = 3) -> str:
        """
        基于简单的获取逻辑提取相关智慧（未来可升级为向量匹配）
        """
        if self._use_external:
            return self._wm.get_relevant_wisdom(question, limit)

        wisdoms = self.get_all_wisdoms()
        if not wisdoms:
            return ""

        # 简单实现：总是返回最新提炼的几条智慧，以增强大模型的近期经验
        relevant_wisdoms = sorted(wisdoms, key=lambda x: x["id"], reverse=True)[:limit]

        if not relevant_wisdoms:
            return ""

        formatted_wisdom = "\n【来自独立智慧库的历史实战经验启示（请务必参考以下教训优化你的分析）】\n"
        for w in relevant_wisdoms:
            formatted_wisdom += f"- {w['extracted_wisdom']}\n"

        return formatted_wisdom
