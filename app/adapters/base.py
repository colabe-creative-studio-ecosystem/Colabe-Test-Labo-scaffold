from abc import ABC, abstractmethod
from typing import TypedDict
from app.orchestrator.models import StepContext, StepResult


class Capabilities(TypedDict):
    """Defines the capabilities discovered by an adapter."""

    can_static: bool
    can_unit: bool
    can_integration: bool
    can_e2e: bool
    can_perf: bool
    can_a11y: bool
    can_security: bool
    can_coverage: bool
    can_sbom: bool


class Adapter(ABC):
    """Abstract base class for all language/stack adapters."""

    id: str
    name: str
    languages: list[str]

    @abstractmethod
    def discover(self, ctx: StepContext) -> StepResult:
        """Discover project capabilities and structure."""
        pass

    @abstractmethod
    def static(self, ctx: StepContext) -> StepResult:
        """Run static analysis tools (linting, type checking)."""
        pass

    @abstractmethod
    def unit(self, ctx: StepContext) -> StepResult:
        """Run unit tests."""
        pass

    @abstractmethod
    def integration(self, ctx: StepContext) -> StepResult:
        """Run integration tests."""
        pass

    @abstractmethod
    def e2e(self, ctx: StepContext) -> StepResult:
        """Run end-to-end tests."""
        pass

    @abstractmethod
    def perf(self, ctx: StepContext) -> StepResult:
        """Run performance tests."""
        pass

    @abstractmethod
    def a11y(self, ctx: StepContext) -> StepResult:
        """Run accessibility tests."""
        pass

    @abstractmethod
    def security(self, ctx: StepContext) -> StepResult:
        """Run security scanning tools."""
        pass

    @abstractmethod
    def coverage(self, ctx: StepContext) -> StepResult:
        """Generate and process code coverage reports."""
        pass

    @abstractmethod
    def sbom(self, ctx: StepContext) -> StepResult:
        """Generate a Software Bill of Materials (SBOM)."""
        pass

    @abstractmethod
    def summarize(self, ctx: StepContext) -> StepResult:
        """Summarize the entire run."""
        pass