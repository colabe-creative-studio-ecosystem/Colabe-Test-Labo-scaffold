import reflex as rx
from .seo_state import SeoState

PROGRAMMATIC_CONTENT = {
    "adapters": {
        "python": {
            "title": "Python",
            "content": "Our Python adapter allows seamless integration with your Pytest or unittest frameworks.",
            "command": "pip install colabe-adapter-python",
        },
        "node": {
            "title": "Node.js",
            "content": "Integrate with Jest, Mocha, or any other Node.js testing framework.",
            "command": "npm install @colabe/adapter-node",
        },
        "java": {
            "title": "Java",
            "content": "Use our Java adapter with Maven or Gradle to connect with JUnit or TestNG.",
            "command": "mvn install colabe-adapter-java",
        },
    },
    "playbooks": {
        "web-perf": {
            "title": "Web Performance",
            "content": "A comprehensive playbook for measuring and improving web performance using Lighthouse and Playwright.",
        },
        "a11y": {
            "title": "Accessibility",
            "content": "Ensure your application is accessible to everyone with our a11y testing playbook, powered by axe-core.",
        },
        "security": {
            "title": "Security",
            "content": "A playbook to run static and dynamic security analysis on your codebase.",
        },
    },
    "integrations": {
        "github": {
            "title": "GitHub",
            "content": "Integrate Colabe directly into your GitHub Actions workflows for seamless CI/CD.",
        },
        "gitlab": {
            "title": "GitLab",
            "content": "Use Colabe with GitLab CI to get test results right in your merge requests.",
        },
        "bitbucket": {
            "title": "Bitbucket",
            "content": "Connect Colabe to your Bitbucket Pipelines to automate testing.",
        },
    },
}


class ProgrammaticPageState(SeoState):
    """State for programmatic SEO pages."""

    current_item_title: str = ""
    current_item_content: str = ""
    sample_command: str = ""

    @rx.event
    def on_public_page_load(self):
        """Overrides base SEO load to add programmatic content."""
        super().on_public_page_load()
        path_parts = self.router.page.path.strip("/").split("/")
        if len(path_parts) >= 3:
            lang, content_type, item_key = (path_parts[0], path_parts[1], path_parts[2])
            if (
                content_type in PROGRAMMATIC_CONTENT
                and item_key in PROGRAMMATIC_CONTENT[content_type]
            ):
                item_data = PROGRAMMATIC_CONTENT[content_type][item_key]
                self.current_item_title = item_data["title"]
                self.current_item_content = item_data["content"]
                if "command" in item_data:
                    self.sample_command = item_data["command"]
                self.meta_title = (
                    f"{self.current_item_title} {content_type.title()} | Colabe"
                )
                self.og_title = self.meta_title
                self.meta_description = self.current_item_content
                self.og_description = self.current_item_content