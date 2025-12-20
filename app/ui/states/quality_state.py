import reflex as rx
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.models import Coverage, QualityScore
import random
import plotly.graph_objects as go
from typing import Optional


class QualityScoreDisplay(rx.Base):
    static_issues_score: str
    test_pass_rate: str
    coverage_delta: str
    performance_score: str
    accessibility_score: str
    security_score: str
    composite_score: str


class QualityState(rx.State):
    coverage_data: list[Coverage] = []
    quality_score: Optional[QualityScore] = None
    current_run_id: int | None = None

    async def _load_quality_data(self, run_id: int):
        self.current_run_id = run_id
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_logged_in:
            return
        with rx.session() as session:
            self.coverage_data = session.exec(
                sqlmodel.select(Coverage).where(Coverage.run_id == run_id)
            ).all()
            self.quality_score = session.exec(
                sqlmodel.select(QualityScore).where(QualityScore.run_id == run_id)
            ).first()

    @rx.event
    async def load_quality_data(self, run_id: int):
        await self._load_quality_data(run_id)

    @rx.event
    async def generate_quality_report(self, run_id: int):
        with rx.session() as session:
            session.exec(sqlmodel.delete(Coverage).where(Coverage.run_id == run_id))
            session.exec(
                sqlmodel.delete(QualityScore).where(QualityScore.run_id == run_id)
            )
            session.commit()
            files = [
                "app/ui/pages/index.py",
                "app/ui/pages/auth.py",
                "app/core/models.py",
                "app/ui/states/auth_state.py",
                "app/app.py",
                "app/orchestrator/tasks.py",
                "app/ui/pages/security.py",
                "app/ui/states/security_state.py",
            ]
            for file_path in files:
                total_lines = random.randint(50, 200)
                covered_lines = random.randint(int(total_lines * 0.4), total_lines)
                coverage = Coverage(
                    run_id=run_id,
                    file_path=file_path,
                    total_lines=total_lines,
                    covered_lines=covered_lines,
                    coverage_percentage=round(covered_lines / total_lines * 100, 2),
                )
                session.add(coverage)
            qs = QualityScore(
                run_id=run_id,
                static_issues_score=random.uniform(70, 95),
                test_pass_rate=random.uniform(85, 100),
                coverage_delta=random.uniform(-5, 5),
                performance_score=random.uniform(75, 98),
                accessibility_score=random.uniform(80, 99),
                security_score=random.uniform(60, 90),
                composite_score=0,
            )
            qs.composite_score = (
                qs.static_issues_score * 0.2
                + qs.test_pass_rate * 0.3
                + (50 + qs.coverage_delta * 5) * 0.1
                + qs.performance_score * 0.1
                + qs.accessibility_score * 0.1
                + qs.security_score * 0.2
            )
            session.add(qs)
            session.commit()
        await self._load_quality_data(run_id)

    @rx.event
    async def load_initial_data(self):
        await self.load_quality_data(1)

    @rx.var
    def formatted_quality_score(self) -> Optional[QualityScoreDisplay]:
        if not self.quality_score:
            return None
        return QualityScoreDisplay(
            static_issues_score=f"{self.quality_score.static_issues_score:.0f}",
            test_pass_rate=f"{self.quality_score.test_pass_rate:.1f}%",
            coverage_delta=f"{self.quality_score.coverage_delta:+.1f}%",
            performance_score=f"{self.quality_score.performance_score:.1f}",
            accessibility_score=f"{self.quality_score.accessibility_score:.1f}",
            security_score=f"{self.quality_score.security_score:.1f}",
            composite_score=f"{self.quality_score.composite_score:.1f}",
        )

    @rx.var
    def coverage_heatmap_fig(self) -> go.Figure:
        if not self.coverage_data:
            return go.Figure()
        paths = [d.file_path for d in self.coverage_data]
        percentages = [d.coverage_percentage for d in self.coverage_data]
        dir_map = {}
        for path, pct in zip(paths, percentages):
            directory = "/".join(path.split("/")[:-1])
            if directory not in dir_map:
                dir_map[directory] = []
            dir_map[directory].append({"file": path.split("/")[-1], "coverage": pct})
        dirs = list(dir_map.keys())
        max_files = max((len(files) for files in dir_map.values()))
        z = [[None] * max_files for _ in dirs]
        hover_text = [[None] * max_files for _ in dirs]
        filenames = [[""] * max_files for _ in dirs]
        for i, directory in enumerate(dirs):
            for j, file_info in enumerate(dir_map[directory]):
                z[i][j] = file_info["coverage"]
                hover_text[i][j] = (
                    f"{file_info['file']}<br>Coverage: {file_info['coverage']:.1f}%"
                )
                filenames[i][j] = file_info["file"]
        fig = go.Figure(
            data=go.Heatmap(
                z=z,
                y=dirs,
                x=[f"File {i + 1}" for i in range(max_files)],
                colorscale="RdYlGn",
                zmin=0,
                zmax=100,
                hoverongaps=False,
                text=filenames,
                texttemplate="%{text}",
                hovertext=hover_text,
                hoverinfo="text",
            )
        )
        fig.update_layout(
            title="File Coverage Heatmap",
            xaxis_title=None,
            yaxis_title=None,
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            font=dict(color="#E8F0FF", size=10),
        )
        fig.update_xaxes(showticklabels=False, visible=False)
        return fig