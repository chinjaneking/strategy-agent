"""
知识库模块单元测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.knowledge_base import (
    get_knowledge_base,
    get_system_prompt,
    get_error_cases,
    get_tactic_detail,
    get_thirtysix_stratagems,
    get_historical_cases,
    search_tactics,
    get_kb_version,
    is_using_external_kb,
    SYSTEM_PROMPT,
)
from core.analysis_templates import (
    get_scene_template,
    get_scene_description,
    get_all_scene_types,
    build_analysis_prompt,
)


class TestKnowledgeBase:
    """知识库功能测试"""

    def test_knowledge_base_not_empty(self):
        """知识库应不为空"""
        kb = get_knowledge_base()
        assert kb is not None
        assert len(kb) >= 5

    def test_knowledge_base_has_required_sources(self):
        """知识库应包含五大体系"""
        kb = get_knowledge_base()
        required = ["三十六计", "鬼谷子", "孙子兵法", "毛泽东思想", "资治通鉴"]
        for source in required:
            assert source in kb, f"缺少知识体系: {source}"

    def test_embedded_prompt_is_v22(self):
        """内嵌系统提示词应为V2.2版本（不依赖外部知识库）"""
        assert "V2.2" in SYSTEM_PROMPT
        assert "六步分析框架" in SYSTEM_PROMPT

    def test_embedded_prompt_has_self_check(self):
        """V2.2内嵌提示词应包含自我校验清单"""
        assert "自我校验" in SYSTEM_PROMPT or "校验清单" in SYSTEM_PROMPT

    def test_embedded_prompt_has_table_format(self):
        """V2.2内嵌提示词应要求Markdown表格输出"""
        assert "Markdown 表格" in SYSTEM_PROMPT or "表格" in SYSTEM_PROMPT

    def test_error_cases_not_empty(self):
        """错误案例库应不为空"""
        cases = get_error_cases()
        assert cases is not None
        assert len(cases) >= 5

    def test_tactic_detail_guiguzi(self):
        """应能获取鬼谷子谋略详情"""
        detail = get_tactic_detail("鬼谷子", "捭阖")
        assert detail is not None
        assert "definition" in detail

    def test_tactic_detail_sunzi(self):
        """应能获取孙子兵法谋略详情"""
        detail = get_tactic_detail("孙子兵法", "计篇")
        assert detail is not None

    def test_thirtysix_stratagems(self):
        """三十六计应包含六套计"""
        stratagems = get_thirtysix_stratagems()
        assert stratagems is not None
        tactics = stratagems.get("core_tactics", {})
        assert len(tactics) >= 6

    def test_historical_cases(self):
        """历史案例应不少于6个"""
        cases = get_historical_cases()
        assert cases is not None
        tactics = cases.get("core_tactics", {})
        assert len(tactics) >= 6

    def test_search_tactics(self):
        """搜索功能应正常工作"""
        results = search_tactics("围魏救赵")
        assert len(results) >= 1
        assert any("围魏救赵" in r["name"] for r in results)

    def test_search_empty_returns_empty(self):
        """搜索不存在的谋略应返回空"""
        results = search_tactics("不存在的谋略xyzabc")
        assert len(results) == 0

    def test_kb_version(self):
        """版本号应可获取"""
        version = get_kb_version()
        assert version is not None
        assert len(version) > 0


class TestAnalysisTemplates:
    """场景模板测试"""

    def test_has_10_scene_types(self):
        """V2.2应有10个场景类型"""
        types = get_all_scene_types()
        assert len(types) >= 10

    def test_original_6_scenes_exist(self):
        """原有6个场景应存在"""
        required = ["通用决策", "创业决策", "职场决策", "投资决策", "婚恋决策", "教育决策"]
        types = get_all_scene_types()
        for scene in required:
            assert scene in types, f"缺少场景: {scene}"

    def test_new_4_scenes_exist(self):
        """V2.2新增4个场景应存在"""
        required = ["互联网创业决策", "制造业经营决策", "职场晋升决策", "投资理财决策"]
        types = get_all_scene_types()
        for scene in required:
            assert scene in types, f"缺少V2.2场景: {scene}"

    def test_template_not_empty(self):
        """每个场景的模板应不为空"""
        for scene_type in get_all_scene_types():
            template = get_scene_template(scene_type)
            assert template is not None, f"{scene_type}模板为空"
            assert len(template) > 50, f"{scene_type}模板过短"

    def test_description_not_empty(self):
        """每个场景应有描述"""
        for scene_type in get_all_scene_types():
            desc = get_scene_description(scene_type)
            assert desc is not None, f"{scene_type}缺少描述"

    def test_build_prompt_default(self):
        """默认构建提示词应正常"""
        prompt = build_analysis_prompt("测试问题")
        assert "测试问题" in prompt
        assert "通用决策" in prompt

    def test_build_prompt_specific_scene(self):
        """指定场景构建提示词应正常"""
        prompt = build_analysis_prompt("互联网创业问题", "互联网创业决策")
        assert "互联网创业问题" in prompt
        assert "PMF" in prompt

    def test_build_prompt_unknown_scene_fallback(self):
        """未知场景应回退到通用"""
        prompt = build_analysis_prompt("测试", "不存在的场景")
        assert "测试" in prompt
        # 应回退到通用模板
        assert "通用决策" in prompt or "分析框架" in prompt
