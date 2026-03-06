"""
质量检查器单元测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.quality_checker import QualityChecker


@pytest.fixture
def checker():
    return QualityChecker()


# 一个高质量的模拟 LLM 输出（包含六步分析、表格、来源引用等）
GOOD_OUTPUT = """
### 步骤1：矛盾拆解 🔍

| 维度 | 分析内容 |
|------|----------|
| **主要矛盾** | 资金有限与竞品价格战的冲突 |
| **次要矛盾** | 团队士气与市场信心的矛盾 |
| **矛盾主要方面** | 竞品拥有资金优势，主导了价格战节奏 |
| **核心症结** | 本质问题不是价格，而是如何在资源劣势下建立差异化壁垒 |

### 步骤2：谋略匹配 🎯

| 序号 | 谋略名称 | 来源体系 | 选择理由 | 应用方向 |
|------|----------|----------|----------|----------|
| 1 | 避实击虚 | 孙子兵法·虚实篇 | 不应在价格正面交锋 | 转向竞品薄弱的细分市场 |
| 2 | 集中优势兵力 | 毛泽东思想 | 资源有限需聚焦 | 聚焦一个核心场景做到极致 |
| 3 | 围魏救赵 | 三十六计 | 迫使竞品分散注意力 | 在竞品忽视的渠道发力 |
| 4 | 持久战 | 毛泽东思想 | 短期无法正面对抗 | 以时间换空间，等待竞品犯错 |

### 步骤3：多维度方案推演 📋

**🛡️ 保守型方案**：收缩防御
- 核心策略：放弃低毛利产品线，聚焦高壁垒细分市场
- 适用条件：资金不足以支撑6个月以上的价格战
- 预期收益：保住核心客户群，毛利率提升5%
- 所需资源：现有团队即可

**⚔️ 进攻型方案**：侧翼突击
- 核心策略：在竞品未覆盖的渠道快速获客
- 适用条件：有差异化的产品特性或渠道优势
- 预期收益：新增30%客户来源
- 所需资源：追加营销预算20万

**🔄 灵活型方案**：以退为进
- 核心策略：表面跟进降价，实际通过增值服务提高客单价
- 适用条件：客户对服务质量敏感
- 预期收益：维持收入的同时建立服务壁垒
- 所需资源：增加1名客户成功经理

### 步骤4：风险量化评估 ⚠️

| 方案 | 风险等级 | 主要风险点 | 发生概率 | 应对措施 |
|------|----------|-----------|----------|----------|
| 保守型 | 低 | 市场份额进一步下滑 | 中 | 设定最低份额红线 |
| 进攻型 | 高 | 资金消耗过快 | 高 | 设定月度预算上限 |
| 灵活型 | 中 | 客户感知不一致 | 中 | 统一销售话术 |

### 步骤5：落地路径拆分 📅

| 阶段 | 时间节点 | 关键动作 | 里程碑/交付物 | 决策点 |
|------|----------|----------|---------------|--------|
| 第1阶段 | 第1周 | 客户分层分析 | 客户分层报告 | 识别核心客户群 |
| 第2阶段 | 第2-3周 | 差异化产品打磨 | 新版本上线 | 用户满意度>80% |
| 第3阶段 | 第1个月 | 新渠道试点 | 新渠道获客数据 | ROI>1.5即扩大 |

### 步骤6：复盘提示 🔄

| 维度 | 具体内容 |
|------|----------|
| **核心验证指标** | 客户留存率≥90%、新渠道获客成本<50元 |
| **调整信号** | 连续2周留存率<85%时切换方案 |
| **复盘时间点** | 每周五进行周复盘，每月底进行月度评审 |
| **复盘检查清单** | ☐ 核心客户是否流失 ☐ 竞品价格是否继续下探 ☐ 新渠道ROI是否达标 |
"""

# 一个低质量的模拟输出（缺少结构、来源、量化等）
BAD_OUTPUT = """
面对竞品价格战，建议你做好以下几点：

1. 保持冷静，不要盲目降价
2. 提升产品质量
3. 加强客户服务
4. 寻找新的市场机会

总之，要认真分析、深入研究、扎实推进，确保取得实效。
"""


class TestQualityChecker:
    """质量检查器测试"""

    def test_good_output_passes_all(self, checker):
        """高质量输出应通过大多数检查"""
        report = checker.check_all(GOOD_OUTPUT)
        assert report["score"] >= 80
        assert report["passed"] >= 5

    def test_bad_output_fails_most(self, checker):
        """低质量输出应无法通过大多数检查"""
        report = checker.check_all(BAD_OUTPUT)
        assert report["score"] <= 50
        assert report["passed"] <= 3

    def test_core_issue_identified_pass(self, checker):
        """包含核心症结的文本应通过"""
        result = checker.check_core_issue_identified(GOOD_OUTPUT)
        assert result["passed"] is True

    def test_core_issue_identified_fail(self, checker):
        """缺少核心症结的文本应失败"""
        result = checker.check_core_issue_identified(BAD_OUTPUT)
        assert result["passed"] is False

    def test_strategy_count_pass(self, checker):
        """引用足够谋略的文本应通过"""
        result = checker.check_strategy_count(GOOD_OUTPUT)
        assert result["passed"] is True
        assert result["count"] >= 3

    def test_strategy_count_fail(self, checker):
        """未引用谋略的文本应失败"""
        result = checker.check_strategy_count(BAD_OUTPUT)
        assert result["passed"] is False

    def test_risk_quantified_pass(self, checker):
        """量化风险的文本应通过"""
        result = checker.check_risk_quantified(GOOD_OUTPUT)
        assert result["passed"] is True

    def test_risk_quantified_fail(self, checker):
        """未量化风险的文本应失败"""
        result = checker.check_risk_quantified(BAD_OUTPUT)
        assert result["passed"] is False

    def test_actionable_steps_pass(self, checker):
        """有时间线的文本应通过"""
        result = checker.check_actionable_steps(GOOD_OUTPUT)
        assert result["passed"] is True

    def test_actionable_steps_fail(self, checker):
        """无时间线的文本应失败"""
        result = checker.check_actionable_steps(BAD_OUTPUT)
        assert result["passed"] is False

    def test_source_cited_pass(self, checker):
        """引用来源的文本应通过"""
        result = checker.check_source_cited(GOOD_OUTPUT)
        assert result["passed"] is True

    def test_source_cited_fail(self, checker):
        """未引用来源的文本应失败"""
        result = checker.check_source_cited(BAD_OUTPUT)
        assert result["passed"] is False

    def test_markdown_format_pass(self, checker):
        """使用Markdown格式的文本应通过"""
        result = checker.check_markdown_format(GOOD_OUTPUT)
        assert result["passed"] is True

    def test_markdown_format_fail(self, checker):
        """未使用Markdown的文本应失败"""
        result = checker.check_markdown_format(BAD_OUTPUT)
        assert result["passed"] is False

    def test_format_report(self, checker):
        """报告格式化应正常工作"""
        report = checker.check_all(GOOD_OUTPUT)
        formatted = checker.format_report(report)
        assert "输出质量评分" in formatted
        assert "通过" in formatted

    def test_score_to_grade(self, checker):
        """分数等级转换"""
        assert checker._score_to_grade(100) == "A"
        assert checker._score_to_grade(90) == "A"
        assert checker._score_to_grade(75) == "B"
        assert checker._score_to_grade(60) == "C"
        assert checker._score_to_grade(50) == "D"
