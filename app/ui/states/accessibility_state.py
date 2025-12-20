import reflex as rx
from typing import Optional
import asyncio
import random


class ViolationDisplay(rx.Base):
    rule_id: str
    description: str
    element: str
    wcag_criterion: str
    help_url: str
    impact: str
    count: int


class WCAGBreakdown(rx.Base):
    level_a: int
    level_aa: int
    level_aaa: int


class AuditStats(rx.Base):
    overall_score: int
    total_violations: int
    pages_audited: int
    compliance_percentage: float


class AccessibilityState(rx.State):
    is_loading: bool = False
    audit_stats: Optional[AuditStats] = None
    wcag_breakdown: Optional[WCAGBreakdown] = None
    violations: list[ViolationDisplay] = []
    filter_impact: str = "All"

    @rx.var
    def filtered_violations(self) -> list[ViolationDisplay]:
        if self.filter_impact == "All":
            return self.violations
        return [
            v for v in self.violations if v.impact.lower() == self.filter_impact.lower()
        ]

    @rx.var
    def has_data(self) -> bool:
        return self.audit_stats is not None

    @rx.event
    def set_filter_impact(self, impact: str):
        self.filter_impact = impact

    @rx.event(background=True)
    async def run_audit(self):
        async with self:
            self.is_loading = True
        await asyncio.sleep(2.0)
        stats = AuditStats(
            overall_score=random.randint(75, 98),
            total_violations=0,
            pages_audited=random.randint(5, 15),
            compliance_percentage=0.0,
        )
        breakdown = WCAGBreakdown(level_a=0, level_aa=0, level_aaa=0)
        mock_violations_data = [
            {
                "rule_id": "image-alt",
                "description": "Images must have alternate text",
                "element": "<img src='logo.png'>",
                "wcag_criterion": "1.1.1 (A)",
                "impact": "critical",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/image-alt",
            },
            {
                "rule_id": "color-contrast",
                "description": "Elements must have sufficient color contrast",
                "element": "<button class='btn-gray'>",
                "wcag_criterion": "1.4.3 (AA)",
                "impact": "serious",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/color-contrast",
            },
            {
                "rule_id": "label",
                "description": "Form elements must have labels",
                "element": "<input type='text'>",
                "wcag_criterion": "1.3.1 (A)",
                "impact": "critical",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/label",
            },
            {
                "rule_id": "link-name",
                "description": "Links must have discernible text",
                "element": "<a href='#'></a>",
                "wcag_criterion": "2.4.4 (A)",
                "impact": "serious",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/link-name",
            },
            {
                "rule_id": "heading-order",
                "description": "Heading levels should only increase by one",
                "element": "<h5>Title</h5>",
                "wcag_criterion": "1.3.1 (A)",
                "impact": "moderate",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/heading-order",
            },
            {
                "rule_id": "landmark-one-main",
                "description": "Document should have one main landmark",
                "element": "<body>",
                "wcag_criterion": "1.3.1 (A)",
                "impact": "moderate",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/landmark-one-main",
            },
            {
                "rule_id": "region",
                "description": "All page content should be contained by landmarks",
                "element": "<div>",
                "wcag_criterion": "2.4.1 (A)",
                "impact": "minor",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/region",
            },
            {
                "rule_id": "tabindex",
                "description": "Elements should not have tabindex greater than zero",
                "element": "<div tabindex='1'>",
                "wcag_criterion": "2.4.3 (A)",
                "impact": "minor",
                "help_url": "https://dequeuniversity.com/rules/axe/4.4/tabindex",
            },
        ]
        selected_violations = random.sample(
            mock_violations_data, k=random.randint(3, len(mock_violations_data))
        )
        new_violations = []
        total_v = 0
        level_a = 0
        level_aa = 0
        level_aaa = 0
        for v in selected_violations:
            count = random.randint(1, 10)
            total_v += count
            if "(A)" in v["wcag_criterion"]:
                level_a += count
            elif "(AA)" in v["wcag_criterion"]:
                level_aa += count
            elif "(AAA)" in v["wcag_criterion"]:
                level_aaa += count
            new_violations.append(
                ViolationDisplay(
                    rule_id=v["rule_id"],
                    description=v["description"],
                    element=v["element"],
                    wcag_criterion=v["wcag_criterion"],
                    help_url=v["help_url"],
                    impact=v["impact"],
                    count=count,
                )
            )
        stats.total_violations = total_v
        stats.compliance_percentage = round(max(0, 100 - total_v * 1.5), 1)
        breakdown.level_a = level_a
        breakdown.level_aa = level_aa
        breakdown.level_aaa = level_aaa
        async with self:
            self.audit_stats = stats
            self.wcag_breakdown = breakdown
            self.violations = new_violations
            self.is_loading = False