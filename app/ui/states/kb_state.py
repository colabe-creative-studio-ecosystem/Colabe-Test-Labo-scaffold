import reflex as rx
from typing import TypedDict
from app.ui.states.auth_state import AuthState


class GuideSection(TypedDict):
    title: str
    content: str
    subsections: list["GuideSection"]


class FaqItem(TypedDict):
    question: str
    answer: str


class KBState(AuthState):
    """State for the Knowledge Base (User Guide and FAQ)."""

    user_guide_content: list[GuideSection] = [
        {
            "title": "1. Onboarding Your Project",
            "content": "Connecting your repository is the first step to unlocking the power of Colabe Test Labo. We support connecting via Git URL or by uploading a ZIP archive of your source code.",
            "subsections": [
                {
                    "title": "1.1. Connecting a Git Repository",
                    "content": "Navigate to the 'Projects' page from the sidebar and click 'New Project'. Select the 'From Git URL' option, paste your repository's HTTPS or SSH URL, and provide an access token if it's a private repository. Colabe will then clone your project and automatically detect its technology stack.",
                    "subsections": [],
                },
                {
                    "title": "1.2. Uploading a ZIP file",
                    "content": "For local projects or projects not hosted on a Git provider, you can upload a ZIP archive. On the 'New Project' page, select 'Upload ZIP', and drag-and-drop or select your project's compressed file. The archive will be securely uploaded and extracted for analysis.",
                    "subsections": [],
                },
            ],
        },
        {
            "title": "2. Running Tests",
            "content": "Once your project is set up, you can configure and run test plans to get a comprehensive overview of your code's quality, security, and performance.",
            "subsections": [
                {
                    "title": "2.1. Creating a Test Plan",
                    "content": "A Test Plan is a reusable configuration that defines which tests and analyses to run. Go to the 'Test Plans' page, create a new plan, and select the adapters you want to enable (e.g., Pytest, Bandit, Lighthouse). You can have multiple test plans for different scenarios, like a quick PR check versus a full nightly build.",
                    "subsections": [],
                },
                {
                    "title": "2.2. Triggering a Run",
                    "content": "You can trigger runs manually from the UI on the 'Live Runs' page by selecting a project and a test plan. For automation, you can configure webhooks in your Git provider (e.g., GitHub Actions, GitLab CI) to trigger runs automatically on events like a new commit or pull request.",
                    "subsections": [],
                },
            ],
        },
        {
            "title": "3. Autofix Engine",
            "content": "Our Autofix engine can automatically generate patches for certain types of security and quality issues, helping you fix problems faster.",
            "subsections": [
                {
                    "title": "3.1. How it works",
                    "content": "When an eligible finding is detected, an 'Autofix' button will appear next to it on the Security or Quality dashboards. Clicking it will trigger a process where our AI generates a code patch. If you have auto-merge enabled in your policies and all gates pass, a pull request can be created and merged automatically.",
                    "subsections": [],
                }
            ],
        },
    ]
    faq_items: list[FaqItem] = [
        {
            "question": "What is Colabe Test Labo?",
            "answer": "Colabe Test Labo is a comprehensive, cloud-based platform for automated software testing, analysis, and quality assurance. It helps development teams ensure their code is secure, performant, and high-quality before deployment.",
        },
        {
            "question": "How does billing work?",
            "answer": "We use a hybrid model. Your subscription plan (e.g., Pro, Enterprise) gives you a monthly allowance of 'coins' and sets your concurrency limits. Specific actions, like run minutes or Autofix attempts, consume coins. You can purchase additional coin packs if you run out.",
        },
        {
            "question": "Can I use this for private repositories?",
            "answer": "Yes, absolutely. When connecting a private repository, you will be prompted to provide a read-only access token. This token is securely stored and used only for cloning and analyzing your code.",
        },
        {
            "question": "Which programming languages are supported?",
            "answer": "We support a wide range of languages through our pluggable adapter system, including Python, JavaScript/TypeScript, Java/Kotlin, Swift, Dart/Flutter, PHP, Ruby, Go, and .NET. You can see the full list of scanners and tools on the 'Adapters' page.",
        },
        {
            "question": "What is a 'Quality Score'?",
            "answer": "The Quality Score is a composite metric that gives you an at-a-glance understanding of your project's health. It is calculated based on factors like test pass rate, code coverage, security findings, performance metrics, and static analysis issues.",
        },
        {
            "question": "Is my source code secure?",
            "answer": "Security is our top priority. Your source code is processed in isolated, ephemeral environments. We only store metadata and analysis results, not your source code itself, after a run is complete. All data is encrypted at rest and in transit.",
        },
    ]