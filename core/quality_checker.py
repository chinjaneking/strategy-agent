"""
输出质量检查器模块 (V2.2)
对 LLM 生成的分析结果进行后处理质量检查
"""

import re
from typing import Dict, Any, List


class QualityChecker:
    """
    分析输出质量检查器

    在 LLM 返回分析结果后，使用规则检查输出是否符合六步分析框架的质量要求。
    """

    # 六步分析标识（允许多种变体）
    STEP_PATTERNS = [
        (r"步骤\s*1|矛盾拆解|矛盾分析", "矛盾拆解"),
        (r"步骤\s*2|谋略匹配", "谋略匹配"),
        (r"步骤\s*3|方案推演|多维度", "方案推演"),
        (r"步骤\s*4|风险.*评估|风险量化", "风险评估"),
        (r"步骤\s*5|落地.*拆分|落地路径", "落地路径"),
        (r"步骤\s*6|复盘提示|复盘", "复盘提示"),
    ]

    # 谋略来源体系关键词
    SOURCE_KEYWORDS = [
        "鬼谷子", "孙子兵法", "毛泽东", "三十六计", "资治通鉴",
        "历史谋略", "兵书", "战国策", "谋略原则",
        "捭阖", "反应", "内楗", "抵巇", "飞箝", "忤合",
        "计篇", "谋攻", "虚实", "九变", "用间",
        "实事求是", "矛盾分析", "群众路线", "游击战", "集中优势", "持久战",
        "围魏救赵", "声东击西", "以逸待劳", "借刀杀人",
    ]

    def check_all(self, content: str) -> Dict[str, Any]:
        """
        执行所有质量检查

        Args:
            content: LLM 生成的分析文本

        Returns:
            检查报告字典
        """
        checks = {
            "core_issue": self.check_core_issue_identified(content),
            "strategy_count": self.check_strategy_count(content),
            "risk_quantified": self.check_risk_quantified(content),
            "actionable_steps": self.check_actionable_steps(content),
            "source_cited": self.check_source_cited(content),
            "markdown_format": self.check_markdown_format(content),
        }

        passed = sum(1 for c in checks.values() if c["passed"])
        total = len(checks)
        score = round(passed / total * 100)

        return {
            "checks": checks,
            "passed": passed,
            "total": total,
            "score": score,
            "grade": self._score_to_grade(score),
        }

    def check_core_issue_identified(self, content: str) -> Dict[str, Any]:
        """检查是否明确指出了核心症结"""
        # 查找矛盾拆解步骤
        has_step1 = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern, _ in self.STEP_PATTERNS[:1]
        )
        # 查找核心症结相关关键词
        core_keywords = ["核心症结", "主要矛盾", "根本问题", "关键矛盾", "本质", "要害"]
        has_core_issue = any(kw in content for kw in core_keywords)

        passed = has_step1 and has_core_issue
        return {
            "passed": passed,
            "name": "核心症结识别",
            "detail": "已识别核心症结" if passed else "未明确指出核心症结或缺少矛盾拆解步骤",
        }

    def check_strategy_count(self, content: str) -> Dict[str, Any]:
        """检查谋略匹配数量是否在3-5个范围内"""
        # 统计引用的谋略来源数量
        cited_sources = set()
        for kw in self.SOURCE_KEYWORDS:
            if kw in content:
                cited_sources.add(kw)

        count = len(cited_sources)
        passed = count >= 3

        return {
            "passed": passed,
            "name": "谋略匹配数量",
            "detail": f"引用了 {count} 个谋略/来源" + ("" if passed else "（建议至少3个）"),
            "count": count,
        }

    def check_risk_quantified(self, content: str) -> Dict[str, Any]:
        """检查风险评估是否量化"""
        risk_levels = ["高", "中", "低"]
        risk_keywords = ["风险等级", "发生概率", "应对措施", "风险点", "规避"]

        has_risk_level = sum(1 for level in risk_levels if f"风险" in content and level in content) >= 2
        has_risk_detail = sum(1 for kw in risk_keywords if kw in content) >= 2

        passed = has_risk_level and has_risk_detail
        return {
            "passed": passed,
            "name": "风险量化评估",
            "detail": "风险已量化评估" if passed else "风险评估不够量化，缺少等级或具体措施",
        }

    def check_actionable_steps(self, content: str) -> Dict[str, Any]:
        """检查落地步骤是否可执行"""
        time_keywords = ["第一周", "第二周", "第一阶段", "第二阶段",
                         "1周", "2周", "1个月", "2个月",
                         "Week", "月内", "天内", "阶段"]
        milestone_keywords = ["里程碑", "交付", "验证", "检查点", "决策点", "产出"]

        has_time = any(kw in content for kw in time_keywords)
        has_milestone = any(kw in content for kw in milestone_keywords)

        # 检查是否有落地步骤的结构
        has_step5 = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern, _ in self.STEP_PATTERNS[4:5]
        )

        passed = has_time and (has_milestone or has_step5)
        return {
            "passed": passed,
            "name": "落地步骤可执行性",
            "detail": "包含时间节点和里程碑" if passed else "缺少具体时间节点或可验证的里程碑",
        }

    def check_source_cited(self, content: str) -> Dict[str, Any]:
        """检查是否引用了谋略来源"""
        major_sources = ["鬼谷子", "孙子兵法", "毛泽东", "三十六计", "资治通鉴"]
        cited = [s for s in major_sources if s in content]

        passed = len(cited) >= 2

        return {
            "passed": passed,
            "name": "谋略来源引用",
            "detail": f"引用了来源: {', '.join(cited)}" if cited else "未引用任何谋略来源",
        }

    def check_markdown_format(self, content: str) -> Dict[str, Any]:
        """检查是否使用了Markdown格式"""
        has_headers = bool(re.search(r"^#+\s", content, re.MULTILINE))
        has_bold = "**" in content
        has_table = "|" in content and "---" in content
        has_list = bool(re.search(r"^[-*]\s", content, re.MULTILINE))

        format_score = sum([has_headers, has_bold, has_table, has_list])
        passed = format_score >= 3  # 至少3种格式元素

        details = []
        if has_headers: details.append("标题")
        if has_bold: details.append("加粗")
        if has_table: details.append("表格")
        if has_list: details.append("列表")

        return {
            "passed": passed,
            "name": "Markdown格式",
            "detail": f"使用了: {', '.join(details)}" if details else "未使用Markdown格式",
        }

    @staticmethod
    def _score_to_grade(score: int) -> str:
        """将分数转换为等级"""
        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"

    def format_report(self, report: Dict[str, Any]) -> str:
        """
        格式化质量检查报告为可读字符串

        Args:
            report: check_all() 的返回结果

        Returns:
            格式化的报告字符串
        """
        lines = [
            f"📊 输出质量评分: {report['score']}分 ({report['grade']}级)",
            f"   通过: {report['passed']}/{report['total']}",
            "",
        ]

        for key, check in report["checks"].items():
            status = "✅" if check["passed"] else "❌"
            lines.append(f"   {status} {check['name']}: {check['detail']}")

        return "\n".join(lines)
