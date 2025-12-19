import reflex as rx
from typing import Optional
import asyncio


class AdapterInfo(rx.Base):
    id: str
    name: str
    language: str
    framework: str
    category: str
    icon: str
    description: str
    supported_test_types: list[str]
    status: str
    version: str
    docs_url: str
    cli_command_template: str
    env_vars: list[str]
    ci_platforms: list[str] = ["GitHub Actions", "GitLab CI", "Jenkins"]


class AdapterState(rx.State):
    search_query: str = ""
    selected_language: str = "All"
    selected_status: str = "All"
    selected_category: str = "All"
    selected_adapter: Optional[AdapterInfo] = None
    is_connecting: dict[str, bool] = {}
    adapters: list[AdapterInfo] = [
        AdapterInfo(
            id="py-pytest",
            name="pytest",
            language="Python",
            framework="pytest",
            category="Unit & Integration",
            icon="file-code",
            description="The pytest framework makes it easy to write small tests, yet scales to support complex functional testing.",
            supported_test_types=["unit", "integration", "functional"],
            status="connected",
            version="7.x",
            docs_url="https://docs.pytest.org",
            cli_command_template="pytest {test_path} --junitxml=report.xml",
            env_vars=["PYTHONPATH"],
        ),
        AdapterInfo(
            id="py-unittest",
            name="unittest",
            language="Python",
            framework="unittest",
            category="Unit & Integration",
            icon="file-code",
            description="The Python unit testing framework, sometimes referred to as 'PyUnit'.",
            supported_test_types=["unit"],
            status="disabled",
            version="Stdlib",
            docs_url="https://docs.python.org/3/library/unittest.html",
            cli_command_template="python -m unittest {test_path}",
            env_vars=["PYTHONPATH"],
        ),
        AdapterInfo(
            id="py-behave",
            name="behave",
            language="Python",
            framework="behave",
            category="E2E & UI",
            icon="file-code",
            description="Behavior-driven development (BDD), Python style.",
            supported_test_types=["e2e", "functional"],
            status="pending",
            version="1.2.6",
            docs_url="https://behave.readthedocs.io",
            cli_command_template="behave --junit {test_path}",
            env_vars=["PYTHONPATH"],
        ),
        AdapterInfo(
            id="py-locust",
            name="Locust",
            language="Python",
            framework="Locust",
            category="Performance",
            icon="gauge",
            description="An open source load testing tool.",
            supported_test_types=["performance", "load"],
            status="disabled",
            version="2.x",
            docs_url="https://locust.io",
            cli_command_template="locust -f {test_path} --headless --csv=report",
            env_vars=["LOCUST_HOST"],
        ),
        AdapterInfo(
            id="py-bandit",
            name="Bandit",
            language="Python",
            framework="Bandit",
            category="Security",
            icon="shield",
            description="Security linter for Python code.",
            supported_test_types=["sast", "security"],
            status="connected",
            version="1.7.x",
            docs_url="https://bandit.readthedocs.io",
            cli_command_template="bandit -r {path} -f json -o report.json",
            env_vars=[],
        ),
        AdapterInfo(
            id="js-jest",
            name="Jest",
            language="JavaScript",
            framework="Jest",
            category="Unit & Integration",
            icon="braces",
            description="Jest is a delightful JavaScript Testing Framework with a focus on simplicity.",
            supported_test_types=["unit", "integration"],
            status="connected",
            version="29.x",
            docs_url="https://jestjs.io",
            cli_command_template="npx jest {test_path} --reporter=jest-junit",
            env_vars=["NODE_ENV"],
        ),
        AdapterInfo(
            id="js-vitest",
            name="Vitest",
            language="JavaScript",
            framework="Vitest",
            category="Unit & Integration",
            icon="zap",
            description="A blazing fast unit test framework powered by Vite.",
            supported_test_types=["unit", "integration"],
            status="pending",
            version="1.x",
            docs_url="https://vitest.dev",
            cli_command_template="npx vitest run {test_path} --reporter=junit --outputFile=report.xml",
            env_vars=["NODE_ENV"],
        ),
        AdapterInfo(
            id="js-playwright",
            name="Playwright",
            language="TypeScript",
            framework="Playwright",
            category="E2E & UI",
            icon="monitor",
            description="Playwright enables reliable end-to-end testing for modern web apps.",
            supported_test_types=["e2e", "functional", "ui"],
            status="connected",
            version="1.40.x",
            docs_url="https://playwright.dev",
            cli_command_template="npx playwright test {test_path} --reporter=junit",
            env_vars=["CI", "PLAYWRIGHT_BROWSERS_PATH"],
        ),
        AdapterInfo(
            id="js-cypress",
            name="Cypress",
            language="JavaScript",
            framework="Cypress",
            category="E2E & UI",
            icon="monitor",
            description="Fast, easy and reliable testing for anything that runs in a browser.",
            supported_test_types=["e2e", "functional", "ui"],
            status="disabled",
            version="13.x",
            docs_url="https://www.cypress.io",
            cli_command_template="npx cypress run --spec {test_path} --reporter junit",
            env_vars=["CYPRESS_BASE_URL"],
        ),
        AdapterInfo(
            id="js-k6",
            name="k6",
            language="JavaScript",
            framework="k6",
            category="Performance",
            icon="gauge",
            description="Open-source load testing tool and SaaS for engineering teams.",
            supported_test_types=["performance", "load"],
            status="disabled",
            version="0.46.x",
            docs_url="https://k6.io/docs",
            cli_command_template="k6 run {test_path} --out json=report.json",
            env_vars=["K6_VUS", "K6_DURATION"],
        ),
        AdapterInfo(
            id="js-axe",
            name="axe-core",
            language="JavaScript",
            framework="axe",
            category="Accessibility",
            icon="accessibility",
            description="Accessibility testing engine for websites and other HTML-based user interfaces.",
            supported_test_types=["accessibility"],
            status="disabled",
            version="4.x",
            docs_url="https://www.deque.com/axe/",
            cli_command_template="axe {url} --save report.json",
            env_vars=[],
        ),
        AdapterInfo(
            id="java-junit",
            name="JUnit",
            language="Java",
            framework="JUnit",
            category="Unit & Integration",
            icon="coffee",
            description="JUnit is a simple framework to write repeatable tests.",
            supported_test_types=["unit", "integration"],
            status="disabled",
            version="5.x",
            docs_url="https://junit.org/junit5/",
            cli_command_template="mvn test -Dtest={test_class}",
            env_vars=["JAVA_HOME"],
        ),
        AdapterInfo(
            id="java-testng",
            name="TestNG",
            language="Java",
            framework="TestNG",
            category="Unit & Integration",
            icon="coffee",
            description="TestNG is a testing framework inspired from JUnit and NUnit.",
            supported_test_types=["unit", "integration", "e2e"],
            status="disabled",
            version="7.x",
            docs_url="https://testng.org/doc/",
            cli_command_template="mvn test -DsuiteXmlFile={test_suite}",
            env_vars=["JAVA_HOME"],
        ),
        AdapterInfo(
            id="java-gatling",
            name="Gatling",
            language="Java",
            framework="Gatling",
            category="Performance",
            icon="gauge",
            description="Load test as code, for any web application.",
            supported_test_types=["performance", "load"],
            status="disabled",
            version="3.x",
            docs_url="https://gatling.io/docs/gatling/",
            cli_command_template="mvn gatling:test",
            env_vars=["GATLING_HOME"],
        ),
        AdapterInfo(
            id="go-test",
            name="Go Test",
            language="Go",
            framework="testing",
            category="Unit & Integration",
            icon="box",
            description="Go provides support for automated testing of Go packages.",
            supported_test_types=["unit", "integration"],
            status="connected",
            version="1.21+",
            docs_url="https://pkg.go.dev/testing",
            cli_command_template="go test -v {test_path} | go-junit-report > report.xml",
            env_vars=["GOPATH"],
        ),
        AdapterInfo(
            id="rust-cargo",
            name="Cargo Test",
            language="Rust",
            framework="cargo",
            category="Unit & Integration",
            icon="settings",
            description="Cargo is the Rust package manager, and it is also the test runner.",
            supported_test_types=["unit", "integration"],
            status="disabled",
            version="1.70+",
            docs_url="https://doc.rust-lang.org/cargo/commands/cargo-test.html",
            cli_command_template="cargo test {test_name} -- --format junit > report.xml",
            env_vars=["RUST_BACKTRACE"],
        ),
        AdapterInfo(
            id="csharp-nunit",
            name="NUnit",
            language="C#",
            framework="NUnit",
            category="Unit & Integration",
            icon="hash",
            description="NUnit is a unit-testing framework for all .NET languages.",
            supported_test_types=["unit"],
            status="disabled",
            version="3.x",
            docs_url="https://nunit.org",
            cli_command_template="dotnet test {project_path} --logger:junit",
            env_vars=["DOTNET_ROOT"],
        ),
        AdapterInfo(
            id="ruby-rspec",
            name="RSpec",
            language="Ruby",
            framework="RSpec",
            category="Unit & Integration",
            icon="gem",
            description="Behaviour Driven Development for Ruby.",
            supported_test_types=["unit", "integration", "bdd"],
            status="disabled",
            version="3.x",
            docs_url="https://rspec.info",
            cli_command_template="bundle exec rspec {test_path} --format RspecJunitFormatter --out report.xml",
            env_vars=["RAILS_ENV"],
        ),
        AdapterInfo(
            id="php-phpunit",
            name="PHPUnit",
            language="PHP",
            framework="PHPUnit",
            category="Unit & Integration",
            icon="code-2",
            description="The PHP Unit Testing framework.",
            supported_test_types=["unit"],
            status="disabled",
            version="10.x",
            docs_url="https://phpunit.de",
            cli_command_template="./vendor/bin/phpunit {test_path} --log-junit report.xml",
            env_vars=["APP_ENV"],
        ),
        AdapterInfo(
            id="swift-xctest",
            name="XCTest",
            language="Swift",
            framework="XCTest",
            category="Unit & Integration",
            icon="smartphone",
            description="Create and run unit tests, performance tests, and UI tests for Xcode projects.",
            supported_test_types=["unit", "ui"],
            status="disabled",
            version="5.x",
            docs_url="https://developer.apple.com/documentation/xctest",
            cli_command_template="xcodebuild test -scheme {scheme}",
            env_vars=[],
        ),
        AdapterInfo(
            id="kotlin-junit",
            name="JUnit (Kotlin)",
            language="Kotlin",
            framework="JUnit",
            category="Unit & Integration",
            icon="code",
            description="The programmer-friendly testing framework for Java and the JVM.",
            supported_test_types=["unit", "integration"],
            status="disabled",
            version="5.x",
            docs_url="https://junit.org/junit5/",
            cli_command_template="./gradlew test",
            env_vars=["JAVA_HOME"],
        ),
        AdapterInfo(
            id="mobile-appium",
            name="Appium",
            language="Multi",
            framework="Appium",
            category="Mobile",
            icon="smartphone",
            description="Automation for iOS, Android, and Windows Apps.",
            supported_test_types=["e2e", "functional", "mobile"],
            status="pending",
            version="2.x",
            docs_url="https://appium.io",
            cli_command_template="appium driver run {driver} {test_path}",
            env_vars=["ANDROID_HOME", "JAVA_HOME"],
        ),
        AdapterInfo(
            id="mobile-detox",
            name="Detox",
            language="JavaScript",
            framework="Detox",
            category="Mobile",
            icon="smartphone",
            description="Gray box end-to-end testing and automation library for mobile apps.",
            supported_test_types=["e2e", "mobile"],
            status="disabled",
            version="20.x",
            docs_url="https://wix.github.io/Detox/",
            cli_command_template="detox test -c {config}",
            env_vars=[],
        ),
        AdapterInfo(
            id="api-postman",
            name="Postman/Newman",
            language="JavaScript",
            framework="Newman",
            category="API",
            icon="webhook",
            description="Newman is a command-line collection runner for Postman.",
            supported_test_types=["api", "integration"],
            status="connected",
            version="6.x",
            docs_url="https://www.postman.com/exports/postman-collection",
            cli_command_template="newman run {collection_path} --reporters cli,junit --reporter-junit-export report.xml",
            env_vars=["POSTMAN_API_KEY"],
        ),
    ]

    @rx.var
    def filtered_adapters(self) -> list[AdapterInfo]:
        filtered = self.adapters
        if self.selected_language != "All":
            filtered = [a for a in filtered if a.language == self.selected_language]
        if self.selected_status != "All":
            filtered = [a for a in filtered if a.status == self.selected_status]
        if self.selected_category != "All":
            filtered = [a for a in filtered if a.category == self.selected_category]
        if self.search_query:
            query = self.search_query.lower()
            filtered = [
                a
                for a in filtered
                if query in a.name.lower() or query in a.framework.lower()
            ]
        return filtered

    @rx.var
    def unique_languages(self) -> list[str]:
        langs = set((a.language for a in self.adapters))
        return ["All"] + sorted(list(langs))

    @rx.var
    def unique_categories(self) -> list[str]:
        cats = set((a.category for a in self.adapters))
        return ["All"] + sorted(list(cats))

    @rx.var
    def stats(self) -> dict[str, int]:
        return {
            "total": len(self.adapters),
            "connected": len([a for a in self.adapters if a.status == "connected"]),
            "pending": len([a for a in self.adapters if a.status == "pending"]),
        }

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def set_selected_language(self, language: str):
        self.selected_language = language

    @rx.event
    def set_selected_status(self, status: str):
        self.selected_status = status

    @rx.event
    def set_selected_category(self, category: str):
        self.selected_category = category

    @rx.event
    def open_config(self, adapter: AdapterInfo):
        self.selected_adapter = adapter

    @rx.event
    def close_config(self):
        self.selected_adapter = None

    @rx.event(background=True)
    async def toggle_status(self, adapter_id: str):
        async with self:
            self.is_connecting[adapter_id] = True
        await asyncio.sleep(0.8)
        async with self:
            for i, adapter in enumerate(self.adapters):
                if adapter.id == adapter_id:
                    if adapter.status == "disabled":
                        new_status = "connected"
                    else:
                        new_status = "disabled"
                    updated_adapter = adapter.dict()
                    updated_adapter["status"] = new_status
                    self.adapters[i] = AdapterInfo(**updated_adapter)
                    if self.selected_adapter and self.selected_adapter.id == adapter_id:
                        self.selected_adapter = self.adapters[i]
                    break
            self.is_connecting[adapter_id] = False

    @rx.event
    def connect_all(self):
        visible_ids = [a.id for a in self.filtered_adapters]
        for i, adapter in enumerate(self.adapters):
            if adapter.id in visible_ids and adapter.status == "disabled":
                updated = adapter.dict()
                updated["status"] = "pending"
                self.adapters[i] = AdapterInfo(**updated)